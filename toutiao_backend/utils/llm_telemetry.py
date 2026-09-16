import json
import logging
import math
from collections import Counter, deque
from datetime import datetime, timezone
from threading import Lock

from fastapi import HTTPException


logger = logging.getLogger("uvicorn.error")
VALID_OUTCOMES = {"success", "failure", "cancelled"}


def classify_llm_error(error: Exception) -> str:
    if isinstance(error, HTTPException):
        return {
            500: "configuration",
            502: "upstream",
            504: "timeout",
        }.get(error.status_code, "application")
    return "internal"


def _average(values: list[int]):
    if not values:
        return None
    return round(sum(values) / len(values))


def _percentile(values: list[int], percentile: float):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


class LlmTelemetry:
    """Keep a bounded, content-free operational view of model calls."""

    def __init__(self, max_events: int = 200):
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self._events = deque(maxlen=max_events)
        self._lock = Lock()

    def record(
        self,
        *,
        operation: str,
        provider: str,
        model: str,
        outcome: str,
        latency_ms: int,
        ttft_ms: int | None = None,
        error_type: str | None = None,
    ) -> None:
        if outcome not in VALID_OUTCOMES:
            raise ValueError(f"Unsupported telemetry outcome: {outcome}")

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "provider": provider,
            "model": model,
            "outcome": outcome,
            "latency_ms": max(0, round(latency_ms)),
            "ttft_ms": None if ttft_ms is None else max(0, round(ttft_ms)),
            "error_type": error_type,
        }
        with self._lock:
            self._events.append(event)

        logger.info(
            "llm_telemetry %s",
            json.dumps(event, ensure_ascii=True, separators=(",", ":")),
        )

    def snapshot(self) -> dict:
        with self._lock:
            events = list(self._events)

        outcomes = Counter(event["outcome"] for event in events)
        latencies = [event["latency_ms"] for event in events]
        ttft_values = [
            event["ttft_ms"]
            for event in events
            if event["ttft_ms"] is not None
        ]
        failures_by_type = Counter(
            event["error_type"]
            for event in events
            if event["outcome"] == "failure" and event["error_type"]
        )
        total = len(events)

        return {
            "window": {
                "recorded_events": total,
                "max_events": self._events.maxlen,
                "resets_on_restart": True,
            },
            "totals": {
                "requests": total,
                "success": outcomes["success"],
                "failure": outcomes["failure"],
                "cancelled": outcomes["cancelled"],
                "success_rate": (
                    round(outcomes["success"] / total, 4) if total else None
                ),
            },
            "latency_ms": {
                "average": _average(latencies),
                "p95": _percentile(latencies, 0.95),
            },
            "ttft_ms": {
                "samples": len(ttft_values),
                "average": _average(ttft_values),
                "p95": _percentile(ttft_values, 0.95),
            },
            "by_operation": dict(
                sorted(Counter(event["operation"] for event in events).items())
            ),
            "failures_by_type": dict(sorted(failures_by_type.items())),
            "latest_event_at": events[-1]["timestamp"] if events else None,
            "privacy": {
                "records_prompts": False,
                "records_responses": False,
                "records_user_ids": False,
            },
        }


llm_telemetry = LlmTelemetry()


def record_llm_event(**event) -> None:
    llm_telemetry.record(**event)


def get_llm_telemetry_snapshot() -> dict:
    return llm_telemetry.snapshot()
