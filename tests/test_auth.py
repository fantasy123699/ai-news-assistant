import inspect
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+aiomysql://test:test@localhost:3306/news_app?charset=utf8mb4",
)

from crud.user import hash_password, verify_password
from routers import ai as ai_routes
from routers import news as news_routes
from routers import user as user_routes
from routers.user import get_access_token, require_admin
from schemas.user import PasswordUpdate, UserLogin, UserRegister


class PasswordSecurityTests(unittest.TestCase):
    def test_password_is_hashed_and_verified(self):
        password_hash = hash_password("correct-password")

        self.assertNotEqual(password_hash, "correct-password")
        self.assertTrue(verify_password("correct-password", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))

    def test_plaintext_password_is_rejected(self):
        self.assertFalse(verify_password("legacy-password", "legacy-password"))

    def test_oversized_login_password_is_rejected_safely(self):
        password_hash = hash_password("correct-password")
        self.assertFalse(verify_password("中" * 25, password_hash))

    def test_new_password_policy(self):
        with self.assertRaises(ValueError):
            UserRegister(username="demo", password="short")

        with self.assertRaises(ValueError):
            PasswordUpdate(old_password="old", new_password="中" * 25)


class AuthorizationTests(unittest.IsolatedAsyncioTestCase):
    def test_bearer_and_legacy_tokens_are_supported(self):
        self.assertEqual(get_access_token("Bearer abc123"), "abc123")
        self.assertEqual(get_access_token("abc123"), "abc123")

    def test_invalid_authorization_header_is_rejected(self):
        for header in ("Basic abc123", "Bearer", ""):
            with self.subTest(header=header):
                with self.assertRaises(HTTPException) as context:
                    get_access_token(header)

                self.assertEqual(context.exception.status_code, 401)

    async def test_admin_dependency_enforces_role(self):
        admin = SimpleNamespace(role="admin")
        self.assertIs(await require_admin(admin), admin)

        with self.assertRaises(HTTPException) as context:
            await require_admin(SimpleNamespace(role="user"))

        self.assertEqual(context.exception.status_code, 403)

    def test_admin_endpoints_declare_admin_dependency(self):
        endpoints = (
            user_routes.user_list,
            user_routes.user_detail,
            user_routes.update_user,
            user_routes.delete_user,
            news_routes.create_news,
            news_routes.update_news,
            news_routes.delete_news,
            ai_routes.ai_telemetry,
        )

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint.__name__):
                dependency = inspect.signature(endpoint).parameters["current_user"].default
                self.assertIs(dependency.dependency, require_admin)


class LoginProtectionTests(unittest.IsolatedAsyncioTestCase):
    request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))

    async def test_locked_account_is_rejected_before_database_lookup(self):
        db = AsyncMock()
        with patch.object(
            user_routes.login_rate_limiter,
            "retry_after",
            new=AsyncMock(return_value=45),
        ):
            with self.assertRaises(HTTPException) as context:
                await user_routes.login(
                    UserLogin(username="demo", password="wrong"),
                    self.request,
                    db,
                )

        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.headers["Retry-After"], "45")
        db.execute.assert_not_awaited()

    async def test_threshold_failure_returns_rate_limit_response(self):
        db = AsyncMock()
        with (
            patch.object(
                user_routes.login_rate_limiter,
                "retry_after",
                new=AsyncMock(return_value=0),
            ),
            patch.object(
                user_routes.login_rate_limiter,
                "record_failure",
                new=AsyncMock(return_value=900),
            ),
            patch.object(
                user_routes.user_crud,
                "get_user_by_username",
                new=AsyncMock(return_value=None),
            ),
        ):
            with self.assertRaises(HTTPException) as context:
                await user_routes.login(
                    UserLogin(username="missing", password="wrong"),
                    self.request,
                    db,
                )

        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.headers["Retry-After"], "900")

    async def test_successful_login_clears_previous_failures(self):
        db = AsyncMock()
        user = SimpleNamespace(id=3, password=hash_password("correct-password"))
        reset = AsyncMock()
        with (
            patch.object(
                user_routes.login_rate_limiter,
                "retry_after",
                new=AsyncMock(return_value=0),
            ),
            patch.object(user_routes.login_rate_limiter, "reset", new=reset),
            patch.object(
                user_routes.user_crud,
                "get_user_by_username",
                new=AsyncMock(return_value=user),
            ),
            patch.object(
                user_routes.user_crud,
                "create_token",
                new=AsyncMock(return_value=("raw-token", "expires")),
            ),
            patch.object(
                user_routes.user_crud,
                "user_to_dict",
                return_value={"id": 3},
            ),
        ):
            result = await user_routes.login(
                UserLogin(username="demo", password="correct-password"),
                self.request,
                db,
            )

        reset.assert_awaited_once_with("demo", "127.0.0.1")
        self.assertEqual(result["token"], "raw-token")


if __name__ == "__main__":
    unittest.main()
