import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required setting: {name}. Copy .env.example to .env and configure it."
        )
    return value


def get_int_setting(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Setting {name} must be an integer.") from exc


def get_float_setting(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError(f"Setting {name} must be a number.") from exc


def get_bool_setting(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


DATABASE_URL = get_required_setting("DATABASE_URL")
DB_ECHO = get_bool_setting("DB_ECHO", False)
DB_POOL_SIZE = get_int_setting("DB_POOL_SIZE", 10)
DB_MAX_OVERFLOW = get_int_setting("DB_MAX_OVERFLOW", 20)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = get_int_setting("REDIS_PORT", 6379)
REDIS_DB = get_int_setting("REDIS_DB", 0)
REDIS_DECODE_RESPONSES = get_bool_setting("REDIS_DECODE_RESPONSES", True)

LOCAL_LLM_PROVIDER = os.getenv("LOCAL_LLM_PROVIDER", "ollama")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "deepseek-r1:1.5b")
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:11435")
LOCAL_LLM_TIMEOUT_SECONDS = get_float_setting("LOCAL_LLM_TIMEOUT_SECONDS", 60.0)
LOCAL_LLM_MAX_RETRIES = get_int_setting("LOCAL_LLM_MAX_RETRIES", 2)
LOCAL_LLM_RETRY_BACKOFF_SECONDS = get_float_setting(
    "LOCAL_LLM_RETRY_BACKOFF_SECONDS",
    0.5,
)

if LOCAL_LLM_TIMEOUT_SECONDS <= 0:
    raise RuntimeError("Setting LOCAL_LLM_TIMEOUT_SECONDS must be greater than zero.")
if LOCAL_LLM_MAX_RETRIES < 0:
    raise RuntimeError("Setting LOCAL_LLM_MAX_RETRIES cannot be negative.")
if LOCAL_LLM_RETRY_BACKOFF_SECONDS < 0:
    raise RuntimeError("Setting LOCAL_LLM_RETRY_BACKOFF_SECONDS cannot be negative.")
