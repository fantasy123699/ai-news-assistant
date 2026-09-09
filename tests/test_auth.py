import inspect
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault(
    "DATABASE_URL",
    "mysql+aiomysql://test:test@localhost:3306/news_app?charset=utf8mb4",
)

from crud.user import hash_password, verify_password
from routers import news as news_routes
from routers import user as user_routes
from routers.user import get_access_token, require_admin
from schemas.user import PasswordUpdate, UserRegister


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
        )

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint.__name__):
                dependency = inspect.signature(endpoint).parameters["current_user"].default
                self.assertIs(dependency.dependency, require_admin)


if __name__ == "__main__":
    unittest.main()
