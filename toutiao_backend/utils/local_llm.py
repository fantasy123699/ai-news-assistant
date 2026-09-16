import asyncio
import json
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
FINAL_BLOCK_PATTERN = re.compile(
    r"<final\b[^>]*>(.*?)</final>",
    flags=re.IGNORECASE | re.DOTALL,
)
FINAL_ANSWER_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:最终答案|final answer)\s*[:：]\s*",
    flags=re.IGNORECASE,
)
CHINESE_FINAL_SECTION_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:回答如下|结论如下|以下(?:是|为)[^\n：:]{0,30}(?:回答|总结|推荐|结果))\s*[:：]\s*",
)
FINAL_BLOCK_START_PATTERN = re.compile(r"<final\b[^>]*>", flags=re.IGNORECASE)
FINAL_BLOCK_END_PATTERN = re.compile(r"</final>", flags=re.IGNORECASE)


def extract_final_answer(content: str) -> str:
    """Remove tagged model reasoning while preserving the user-facing answer."""
    final_blocks = FINAL_BLOCK_PATTERN.findall(content)
    if final_blocks:
        return final_blocks[-1].strip()

    answer = REASONING_BLOCK_PATTERN.sub("", content).strip()
    markers = list(FINAL_ANSWER_PATTERN.finditer(answer))
    markers.extend(CHINESE_FINAL_SECTION_PATTERN.finditer(answer))
    if markers:
        last_marker = max(markers, key=lambda marker: marker.start())
        answer = answer[last_marker.end():].strip()
    if REASONING_OPEN_PATTERN.search(answer):
        return ""
    return answer


class FinalAnswerStreamFilter:
    """Expose only a model's final-answer section while chunks arrive."""

    def __init__(self):
        self._buffer = ""
        self._started = False
        self._final_block = False
        self._finished = False

    def feed(self, chunk: str) -> str:
        if self._finished or not chunk:
            return ""

        self._buffer += chunk
        if not self._started:
            candidates = []
            for pattern, is_final_block in (
                (FINAL_BLOCK_START_PATTERN, True),
                (FINAL_ANSWER_PATTERN, False),
                (CHINESE_FINAL_SECTION_PATTERN, False),
            ):
                match = pattern.search(self._buffer)
                if match:
                    candidates.append((match.start(), match.end(), is_final_block))

            if not candidates:
                return ""

            _, marker_end, self._final_block = min(candidates, key=lambda item: item[0])
            self._buffer = self._buffer[marker_end:].lstrip()
            self._started = True

        if not self._final_block:
            output = self._buffer
            self._buffer = ""
            return output

        closing = FINAL_BLOCK_END_PATTERN.search(self._buffer)
        if closing:
            output = self._buffer[:closing.start()]
            self._buffer = ""
            self._finished = True
            return output

        protected_suffix_length = len("</final>") - 1
        if len(self._buffer) <= protected_suffix_length:
            return ""
        output = self._buffer[:-protected_suffix_length]
        self._buffer = self._buffer[-protected_suffix_length:]
        return output

    def feed_final(self, chunk: str) -> str:
        """Accept content from a provider's dedicated final-answer channel."""
        if self._finished or not chunk:
            return ""
        if not self._started:
            self._buffer = ""
            self._started = True
            self._final_block = False
        return chunk

    def finish(self) -> str:
        if self._finished:
            return ""
        if not self._started:
            answer = extract_final_answer(self._buffer)
            self._buffer = ""
            return answer

        output = FINAL_BLOCK_END_PATTERN.sub("", self._buffer).strip()
        self._buffer = ""
        self._finished = True
        return output


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
        "think": True,
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


async def _ollama_chat_stream(messages: list[dict]):
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "stream": True,
        "think": True,
    }
    async with httpx.AsyncClient(timeout=LOCAL_LLM_TIMEOUT_SECONDS, trust_env=False) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            separate_reasoning_seen = False
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if data.get("error"):
                    raise ValueError("LLM stream returned an error")
                message = data.get("message", {})
                separate_reasoning_seen = separate_reasoning_seen or "thinking" in message
                content = message.get("content", "")
                if content:
                    yield {
                        "content": content,
                        "is_final": separate_reasoning_seen,
                    }


async def _openai_compatible_chat_stream(messages: list[dict]):
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=LOCAL_LLM_TIMEOUT_SECONDS, trust_env=False) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            separate_reasoning_seen = False
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                payload_text = line[5:].strip()
                if payload_text == "[DONE]":
                    break
                data = json.loads(payload_text)
                choices = data.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                separate_reasoning_seen = separate_reasoning_seen or any(
                    key in delta for key in ("reasoning", "reasoning_content")
                )
                content = delta.get("content", "")
                if content:
                    yield {
                        "content": content,
                        "is_final": separate_reasoning_seen,
                    }


async def stream_chat_with_local_llm(messages: list[dict]):
    provider = LOCAL_LLM_PROVIDER.lower()
    started_at = time.perf_counter()
    emitted_content = False

    try:
        if provider == "ollama":
            stream = _ollama_chat_stream(messages)
        elif provider in {"openai", "lmstudio", "vllm"}:
            stream = _openai_compatible_chat_stream(messages)
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported local LLM provider: {provider}")

        async for chunk in stream:
            emitted_content = True
            yield chunk
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="LLM service request timed out") from exc
    except httpx.HTTPStatusError as exc:
        logger.warning("llm_stream_rejected provider=%s status=%s", provider, exc.response.status_code)
        raise HTTPException(status_code=502, detail="LLM service rejected the request") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="LLM service is not available") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("llm_invalid_stream provider=%s", provider)
        raise HTTPException(status_code=502, detail="LLM service returned an invalid stream") from exc

    if not emitted_content:
        raise HTTPException(status_code=502, detail="LLM service returned empty content")

    latency_ms = round((time.perf_counter() - started_at) * 1000)
    logger.info(
        "llm_stream_success provider=%s model=%s latency_ms=%s",
        provider,
        LOCAL_LLM_MODEL,
        latency_ms,
    )


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
