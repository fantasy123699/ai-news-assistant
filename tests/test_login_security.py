import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost/news_app")

from crud import user as user_crud
from utils.login_rate_limit import LoginRateLimiter


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.ttls = {}

    async def ttl(self, key):
        return self.ttls.get(key, -2)

    async def incr(self, key):
        self.values[key] = int(self.values.get(key, 0)) + 1
        return self.values[key]

    async def expire(self, key, seconds):
        self.ttls[key] = seconds

    async def set(self, key, value, ex):
        self.values[key] = value
        self.ttls[key] = ex

    async def delete(self, *keys):
        for key in keys:
            self.values.pop(key, None)
            self.ttls.pop(key, None)


class LoginRateLimiterTests(unittest.IsolatedAsyncioTestCase):
    async def test_repeated_failures_create_a_temporary_lock(self):
        limiter = LoginRateLimiter(
            FakeRedis(),
            max_failures=3,
            window_seconds=60,
            lockout_seconds=120,
        )

        self.assertEqual(await limiter.record_failure("DemoUser", "127.0.0.1"), 0)
        self.assertEqual(await limiter.record_failure("demouser", "127.0.0.1"), 0)
        self.assertEqual(await limiter.record_failure("DEMOUSER", "127.0.0.1"), 120)
        self.assertEqual(await limiter.retry_after("demoUser", "127.0.0.1"), 120)
        self.assertEqual(await limiter.retry_after("demoUser", "127.0.0.2"), 0)

    async def test_success_reset_clears_failures_and_lock(self):
        limiter = LoginRateLimiter(FakeRedis(), max_failures=1)
        await limiter.record_failure("demo", "127.0.0.1")

        await limiter.reset("demo", "127.0.0.1")

        self.assertEqual(await limiter.retry_after("demo", "127.0.0.1"), 0)
        self.assertEqual(
            await limiter.record_failure("demo", "127.0.0.1"),
            limiter.lockout_seconds,
        )

    async def test_redis_failure_does_not_break_login_flow(self):
        client = AsyncMock()
        client.ttl.side_effect = RuntimeError("redis unavailable")
        client.incr.side_effect = RuntimeError("redis unavailable")
        limiter = LoginRateLimiter(client)

        self.assertEqual(await limiter.retry_after("demo", "127.0.0.1"), 0)
        self.assertEqual(await limiter.record_failure("demo", "127.0.0.1"), 0)


class TokenSecurityTests(unittest.IsolatedAsyncioTestCase):
    def test_token_hash_is_deterministic_and_not_the_raw_token(self):
        raw_token = "raw-session-token"
        digest = user_crud.hash_token(raw_token)

        self.assertEqual(len(digest), 64)
        self.assertNotEqual(digest, raw_token)
        self.assertEqual(digest, user_crud.hash_token(raw_token))

    async def test_new_token_is_hashed_before_storage(self):
        db = AsyncMock()

        with patch.object(user_crud.secrets, "token_urlsafe", return_value="raw-token"):
            token, _ = await user_crud.create_token(db, user_id=7)

        stored_params = db.execute.await_args.args[1]
        self.assertEqual(token, "raw-token")
        self.assertEqual(stored_params["token"], user_crud.hash_token("raw-token"))
        self.assertNotEqual(stored_params["token"], token)

    async def test_token_lookup_and_logout_use_the_digest(self):
        db = AsyncMock()
        result = MagicMock()
        result.fetchone.return_value = "user-row"
        db.execute.return_value = result

        user = await user_crud.get_user_by_token(db, "raw-token")
        lookup_params = db.execute.await_args.args[1]
        self.assertEqual(user, "user-row")
        self.assertEqual(lookup_params["token"], user_crud.hash_token("raw-token"))

        await user_crud.delete_token(db, "raw-token")
        delete_params = db.execute.await_args.args[1]
        self.assertEqual(delete_params["token"], user_crud.hash_token("raw-token"))

    async def test_password_update_revokes_all_user_sessions_atomically(self):
        db = AsyncMock()
        with patch.object(
            user_crud,
            "get_user_by_id",
            new=AsyncMock(return_value="updated-user"),
        ):
            result = await user_crud.update_password_and_revoke_sessions(
                db,
                user_id=9,
                password_hash="new-password-hash",
            )

        statements = [str(call.args[0]) for call in db.execute.await_args_list]
        self.assertEqual(result, "updated-user")
        self.assertIn("UPDATE `user`", statements[0])
        self.assertIn("DELETE FROM user_token", statements[1])
        db.commit.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
