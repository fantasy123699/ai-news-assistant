import hashlib
import logging

from config.settings import (
    AUTH_LOGIN_LOCKOUT_SECONDS,
    AUTH_LOGIN_MAX_FAILURES,
    AUTH_LOGIN_WINDOW_SECONDS,
)
from utils.cache import redis_client


logger = logging.getLogger("uvicorn.error")


class LoginRateLimiter:
    """Bound repeated login failures without retaining raw account names."""

    def __init__(
        self,
        client,
        *,
        max_failures: int = AUTH_LOGIN_MAX_FAILURES,
        window_seconds: int = AUTH_LOGIN_WINDOW_SECONDS,
        lockout_seconds: int = AUTH_LOGIN_LOCKOUT_SECONDS,
    ):
        self.client = client
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds

    @staticmethod
    def _subject_key(username: str, client_id: str) -> str:
        normalized = f"{username.strip().casefold()}\0{client_id}".encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()

    def _attempt_key(self, username: str, client_id: str) -> str:
        return f"auth:login:failures:{self._subject_key(username, client_id)}"

    def _lock_key(self, username: str, client_id: str) -> str:
        return f"auth:login:locked:{self._subject_key(username, client_id)}"

    async def retry_after(self, username: str, client_id: str) -> int:
        if not self.client:
            return 0
        try:
            ttl = await self.client.ttl(self._lock_key(username, client_id))
            return max(0, ttl)
        except Exception:
            logger.warning("auth_rate_limit_unavailable action=check")
            return 0

    async def record_failure(self, username: str, client_id: str) -> int:
        if not self.client:
            return 0
        try:
            attempt_key = self._attempt_key(username, client_id)
            failures = await self.client.incr(attempt_key)
            await self.client.expire(attempt_key, self.window_seconds)
            if failures < self.max_failures:
                return 0

            await self.client.set(
                self._lock_key(username, client_id),
                "1",
                ex=self.lockout_seconds,
            )
            await self.client.delete(attempt_key)
            return self.lockout_seconds
        except Exception:
            logger.warning("auth_rate_limit_unavailable action=record")
            return 0

    async def reset(self, username: str, client_id: str) -> None:
        if not self.client:
            return
        try:
            await self.client.delete(
                self._attempt_key(username, client_id),
                self._lock_key(username, client_id),
            )
        except Exception:
            logger.warning("auth_rate_limit_unavailable action=reset")


login_rate_limiter = LoginRateLimiter(redis_client)
