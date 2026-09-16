import os
import sys
import unittest
from pathlib import Path

from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost/news_app")

from utils.llm_telemetry import LlmTelemetry, classify_llm_error


class LlmTelemetryTests(unittest.TestCase):
    def test_snapshot_aggregates_outcomes_latency_and_ttft(self):
        telemetry = LlmTelemetry(max_events=10)
        telemetry.record(
            operation="site_chat_stream",
            provider="ollama",
            model="demo-model",
            outcome="success",
            latency_ms=120,
            ttft_ms=30,
        )
        telemetry.record(
            operation="news_summary",
            provider="ollama",
            model="demo-model",
            outcome="failure",
            latency_ms=80,
            error_type="timeout",
        )

        snapshot = telemetry.snapshot()

        self.assertEqual(snapshot["totals"]["requests"], 2)
        self.assertEqual(snapshot["totals"]["success_rate"], 0.5)
        self.assertEqual(snapshot["latency_ms"], {"average": 100, "p95": 120})
        self.assertEqual(snapshot["ttft_ms"], {"samples": 1, "average": 30, "p95": 30})
        self.assertEqual(snapshot["failures_by_type"], {"timeout": 1})

    def test_window_is_bounded_to_recent_events(self):
        telemetry = LlmTelemetry(max_events=2)
        for operation in ("first", "second", "third"):
            telemetry.record(
                operation=operation,
                provider="ollama",
                model="demo-model",
                outcome="success",
                latency_ms=10,
            )

        snapshot = telemetry.snapshot()

        self.assertEqual(snapshot["window"]["recorded_events"], 2)
        self.assertEqual(snapshot["by_operation"], {"second": 1, "third": 1})

    def test_snapshot_never_contains_prompt_response_or_user_identity(self):
        telemetry = LlmTelemetry()
        telemetry.record(
            operation="news_chat",
            provider="ollama",
            model="demo-model",
            outcome="success",
            latency_ms=20,
        )

        snapshot_text = str(telemetry.snapshot()).lower()

        self.assertNotIn("question", snapshot_text)
        self.assertNotIn("answer", snapshot_text)
        self.assertEqual(
            telemetry.snapshot()["privacy"],
            {
                "records_prompts": False,
                "records_responses": False,
                "records_user_ids": False,
            },
        )

    def test_error_classification_uses_safe_categories(self):
        self.assertEqual(
            classify_llm_error(HTTPException(status_code=504, detail="secret detail")),
            "timeout",
        )
        self.assertEqual(classify_llm_error(RuntimeError("secret detail")), "internal")


if __name__ == "__main__":
    unittest.main()
