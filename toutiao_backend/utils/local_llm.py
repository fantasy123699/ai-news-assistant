import asyncio
import json
import os
import urllib.error
import urllib.request

from fastapi import HTTPException


LOCAL_LLM_PROVIDER = os.getenv("LOCAL_LLM_PROVIDER", "ollama")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "deepseek-r1:1.5b")
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:11435")


def _post_json(url: str, payload: dict, timeout: int = 120):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Local LLM service is not available: {exc}",
        ) from exc


def _ollama_chat(messages: list[dict]):
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "stream": False,
    }
    data = _post_json(url, payload)
    return data.get("message", {}).get("content", "")


def _openai_compatible_chat(messages: list[dict]):
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "temperature": 0.3,
    }
    data = _post_json(url, payload)
    choices = data.get("choices") or []
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "")


async def chat_with_local_llm(messages: list[dict]):
    provider = LOCAL_LLM_PROVIDER.lower()

    if provider == "ollama":
        return await asyncio.to_thread(_ollama_chat, messages)

    if provider in {"openai", "lmstudio", "vllm"}:
        return await asyncio.to_thread(_openai_compatible_chat, messages)

    raise HTTPException(status_code=500, detail=f"Unsupported local LLM provider: {provider}")
