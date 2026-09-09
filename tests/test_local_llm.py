import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost/news_app")

from utils import local_llm


def make_response(status_code: int, data):
    request = httpx.Request("POST", "http://llm.test/api/chat")
    return httpx.Response(status_code, request=request, json=data)


class LocalLlmClientTests(unittest.IsolatedAsyncioTestCase):
    def make_client(self, *results):
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.post.side_effect = results
        return client

    async def test_ollama_success_returns_trimmed_content(self):
        client = self.make_client(
            make_response(200, {"message": {"content": "  answer  "}})
        )

        with patch.object(local_llm.httpx, "AsyncClient", return_value=client):
            result = await local_llm.chat_with_local_llm(
                [{"role": "user", "content": "question"}]
            )

        self.assertEqual(result, "answer")

    async def test_openai_compatible_provider_uses_chat_completions(self):
        client = self.make_client(
            make_response(200, {"choices": [{"message": {"content": "answer"}}]})
        )

        with (
            patch.object(local_llm.httpx, "AsyncClient", return_value=client),
            patch.object(local_llm, "LOCAL_LLM_PROVIDER", "vllm"),
        ):
            result = await local_llm.chat_with_local_llm([])

        self.assertEqual(result, "answer")
        self.assertTrue(client.post.await_args.args[0].endswith("/v1/chat/completions"))

    async def test_retryable_error_is_retried(self):
        client = self.make_client(
            make_response(503, {"error": "busy"}),
            make_response(200, {"message": {"content": "answer"}}),
        )

        with (
            patch.object(local_llm.httpx, "AsyncClient", return_value=client),
            patch.object(local_llm, "LOCAL_LLM_MAX_RETRIES", 1),
            patch.object(local_llm, "LOCAL_LLM_RETRY_BACKOFF_SECONDS", 0),
        ):
            result = await local_llm._post_json("http://llm.test/api/chat", {})

        self.assertEqual(result["message"]["content"], "answer")
        self.assertEqual(client.post.await_count, 2)

    async def test_timeout_is_mapped_to_gateway_timeout(self):
        request = httpx.Request("POST", "http://llm.test/api/chat")
        client = self.make_client(httpx.ReadTimeout("slow", request=request))

        with (
            patch.object(local_llm.httpx, "AsyncClient", return_value=client),
            patch.object(local_llm, "LOCAL_LLM_MAX_RETRIES", 0),
        ):
            with self.assertRaises(HTTPException) as context:
                await local_llm._post_json("http://llm.test/api/chat", {})

        self.assertEqual(context.exception.status_code, 504)

    async def test_non_retryable_error_is_not_exposed(self):
        client = self.make_client(make_response(400, {"secret": "upstream detail"}))

        with patch.object(local_llm.httpx, "AsyncClient", return_value=client):
            with self.assertRaises(HTTPException) as context:
                await local_llm._post_json("http://llm.test/api/chat", {})

        self.assertEqual(context.exception.status_code, 502)
        self.assertNotIn("upstream detail", context.exception.detail)
        self.assertEqual(client.post.await_count, 1)

    async def test_empty_model_content_is_rejected(self):
        client = self.make_client(make_response(200, {"message": {"content": ""}}))

        with patch.object(local_llm.httpx, "AsyncClient", return_value=client):
            with self.assertRaises(HTTPException) as context:
                await local_llm.chat_with_local_llm([])

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
