from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from passlib.context import CryptContext
except ImportError:
    CryptContext = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None
VALID_GENDERS = {"male", "female", "unknown"}


def user_to_dict(row):
    data = dict(row._mapping)
    data.pop("password", None)
    return data


def hash_password(password: str) -> str:
    if pwd_context:
        return pwd_context.hash(password)
    return password


def verify_password(password: str, saved_password: str) -> bool:
    if saved_password.startswith(("$2a$", "$2b$", "$2y$")):
        if not pwd_context:
            raise HTTPException(status_code=500, detail="Please install passlib[bcrypt]")
        return pwd_context.verify(password, saved_password)
    return password == saved_password


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        text("SELECT * FROM `user` WHERE id = :user_id"),
        {"user_id": user_id},
    )
    return result.fetchone()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        text("SELECT * FROM `user` WHERE username = :username"),
        {"username": username},
    )
    return result.fetchone()


async def get_user_by_phone(db: AsyncSession, phone: str, exclude_user_id: Optional[int] = None):
    sql = "SELECT * FROM `user` WHERE phone = :phone"
    params = {"phone": phone}

    if exclude_user_id is not None:
        sql += " AND id != :exclude_user_id"
        params["exclude_user_id"] = exclude_user_id

    result = await db.execute(text(sql), params)
    return result.fetchone()


async def create_user(db: AsyncSession, data):
    result = await db.execute(
        text(
            """
            INSERT INTO `user` (username, password, nickname, avatar, gender, bio, phone)
            VALUES (:username, :password, :nickname, :avatar, :gender, :bio, :phone)
            """
        ),
        {
            "username": data.username,
            "password": hash_password(data.password),
            "nickname": data.nickname,
            "avatar": data.avatar,
            "gender": data.gender or "unknown",
            "bio": data.bio,
            "phone": data.phone,
        },
    )
    await db.commit()
    return await get_user_by_id(db, result.lastrowid)


async def create_token(db: AsyncSession, user_id: int):
    token = uuid4().hex
    expires_at = datetime.now() + timedelta(days=7)

    await db.execute(
        text(
            """
            INSERT INTO user_token (user_id, token, expires_at)
            VALUES (:user_id, :token, :expires_at)
            """
        ),
        {"user_id": user_id, "token": token, "expires_at": expires_at},
    )
    await db.commit()

    return token, expires_at


async def get_user_by_token(db: AsyncSession, token: str):
    result = await db.execute(
        text(
            """
            SELECT u.*
            FROM user_token t
            JOIN `user` u ON u.id = t.user_id
            WHERE t.token = :token AND t.expires_at > NOW()
            """
        ),
        {"token": token},
    )
    return result.fetchone()


async def delete_token(db: AsyncSession, token: str):
    await db.execute(text("DELETE FROM user_token WHERE token = :token"), {"token": token})
    await db.commit()


async def get_user_list(db: AsyncSession, keyword: Optional[str], page: int, page_size: int):
    params = {"offset": (page - 1) * page_size, "page_size": page_size}
    where_sql = ""

    if keyword:
        where_sql = """
        WHERE username LIKE :keyword
        OR nickname LIKE :keyword
        OR phone LIKE :keyword
        """
        params["keyword"] = f"%{keyword}%"

    total_result = await db.execute(text(f"SELECT COUNT(*) FROM `user` {where_sql}"), params)
    total = total_result.scalar() or 0

    result = await db.execute(
        text(
            f"""
            SELECT *
            FROM `user`
            {where_sql}
            ORDER BY id DESC
            LIMIT :offset, :page_size
            """
        ),
        params,
    )
    return total, result.fetchall()


async def update_user(db: AsyncSession, user_id: int, update_data: dict):
    if not update_data:
        return await get_user_by_id(db, user_id)

    allowed_fields = ["nickname", "avatar", "gender", "bio", "phone", "password"]
    fields = []
    params = {"user_id": user_id}

    for field in allowed_fields:
        if field in update_data:
            fields.append(f"{field} = :{field}")
            params[field] = update_data[field]

    await db.execute(
        text(f"UPDATE `user` SET {', '.join(fields)} WHERE id = :user_id"),
        params,
    )
    await db.commit()
    return await get_user_by_id(db, user_id)


async def delete_user(db: AsyncSession, user_id: int):
    await db.execute(text("DELETE FROM `user` WHERE id = :user_id"), {"user_id": user_id})
    await db.commit()
