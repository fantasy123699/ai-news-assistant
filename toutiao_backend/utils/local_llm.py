import asyncio
import logging
import re
import time

import httpx
from fastapi import HTTPException

from config.settings import (
    LOCAL_LLM_BASE_URL,
    LOCAL_LLM_MAX_RETRIES,
    LOCAL_LLM_MODEL,
    LOCAL_LLM_PROVIDER,
    LOCAL_LLM_RETRY_BACKOFF_SECONDS,
    LOCAL_LLM_TIMEOUT_SECONDS,
)


logger = logging.getLogger(__name__)
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
REASONING_BLOCK_PATTERN = re.compile(
    r"<(think|analysis|reasoning)\b[^>]*>.*?</\1>",
    flags=re.IGNORECASE | re.DOTALL,
)
REASONING_OPEN_PATTERN = re.compile(
    r"<(?:think|analysis|reasoning)\b[^>]*>",
    flags=re.IGNORECASE,
)
FINAL_ANSWER_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:最终答案|final answer)\s*[:：]\s*",
    flags=re.IGNORECASE,
)


def extract_final_answer(content: str) -> str:
    """Remove tagged model reasoning while preserving the user-facing answer."""
    answer = REASONING_BLOCK_PATTERN.sub("", content).strip()
    markers = list(FINAL_ANSWER_PATTERN.finditer(answer))
    if markers:
        answer = answer[markers[-1].end():].strip()
    if REASONING_OPEN_PATTERN.search(answer):
        return ""
    return answer


async def _post_json(url: str, payload: dict):
    last_status_code = 502
    last_detail = "LLM service is not available"

    async with httpx.AsyncClient(
        timeout=LOCAL_LLM_TIMEOUT_SECONDS,
        trust_env=False,
    ) as client:
        for attempt in range(LOCAL_LLM_MAX_RETRIES + 1):
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("LLM response must be a JSON object")
                return data
            except httpx.TimeoutException:
                last_status_code = 504
                last_detail = "LLM service request timed out"
            except httpx.HTTPStatusError as exc:
                upstream_status = exc.response.status_code
                if upstream_status not in RETRYABLE_STATUS_CODES:
                    logger.warning(
                        "llm_request_rejected provider=%s status=%s",
                        LOCAL_LLM_PROVIDER,
                        upstream_status,
                    )
                    raise HTTPException(
                        status_code=502,
                        detail="LLM service rejected the request",
                    ) from exc
                last_detail = "LLM service is temporarily unavailable"
            except httpx.RequestError:
                last_detail = "LLM service is not available"
            except ValueError as exc:
                logger.warning("llm_invalid_response provider=%s", LOCAL_LLM_PROVIDER)
                raise HTTPException(
                    status_code=502,
                    detail="LLM service returned an invalid response",
                ) from exc

            if attempt < LOCAL_LLM_MAX_RETRIES:
                delay = LOCAL_LLM_RETRY_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "llm_request_retry provider=%s attempt=%s delay_seconds=%s",
                    LOCAL_LLM_PROVIDER,
                    attempt + 1,
                    delay,
                )
                await asyncio.sleep(delay)

    logger.error(
        "llm_request_failed provider=%s attempts=%s",
        LOCAL_LLM_PROVIDER,
        LOCAL_LLM_MAX_RETRIES + 1,
    )
    raise HTTPException(status_code=last_status_code, detail=last_detail)


async def _ollama_chat(messages: list[dict]):
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "stream": False,
    }
    data = await _post_json(url, payload)
    return data.get("message", {}).get("content", "")


async def _openai_compatible_chat(messages: list[dict]):
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "temperature": 0.3,
    }
    data = await _post_json(url, payload)
    choices = data.get("choices") or []
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "")


async def chat_with_local_llm(messages: list[dict]):
    provider = LOCAL_LLM_PROVIDER.lower()
    started_at = time.perf_counter()

    if provider == "ollama":
        content = await _ollama_chat(messages)
    elif provider in {"openai", "lmstudio", "vllm"}:
        content = await _openai_compatible_chat(messages)
    else:
        raise HTTPException(status_code=500, detail=f"Unsupported local LLM provider: {provider}")

    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=502, detail="LLM service returned empty content")

    latency_ms = round((time.perf_counter() - started_at) * 1000)
    logger.info(
        "llm_request_success provider=%s model=%s latency_ms=%s",
        provider,
        LOCAL_LLM_MODEL,
        latency_ms,
    )
    return content.strip()
