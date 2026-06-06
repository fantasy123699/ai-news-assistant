from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def news_to_dict(row):
    return dict(row._mapping)


async def check_favorite(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(
        text(
            """
            SELECT id
            FROM favorite
            WHERE user_id = :user_id AND news_id = :news_id
            """
        ),
        {"user_id": user_id, "news_id": news_id},
    )
    return result.fetchone()


async def add_favorite(db: AsyncSession, user_id: int, news_id: int):
    exists = await check_favorite(db, user_id, news_id)
    if exists:
        return exists

    result = await db.execute(
        text(
            """
            INSERT INTO favorite (user_id, news_id)
            VALUES (:user_id, :news_id)
            """
        ),
        {"user_id": user_id, "news_id": news_id},
    )
    await db.commit()
    return result.lastrowid


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int):
    await db.execute(
        text(
            """
            DELETE FROM favorite
            WHERE user_id = :user_id AND news_id = :news_id
            """
        ),
        {"user_id": user_id, "news_id": news_id},
    )
    await db.commit()


async def clear_favorites(db: AsyncSession, user_id: int):
    await db.execute(text("DELETE FROM favorite WHERE user_id = :user_id"), {"user_id": user_id})
    await db.commit()


async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
):
    params = {
        "user_id": user_id,
        "offset": (page - 1) * page_size,
        "page_size": page_size,
    }
    where_sql = "WHERE f.user_id = :user_id"

    if keyword:
        where_sql += " AND (n.title LIKE :keyword OR n.description LIKE :keyword)"
        params["keyword"] = f"%{keyword}%"

    total_result = await db.execute(
        text(
            f"""
            SELECT COUNT(*)
            FROM favorite f
            JOIN news n ON n.id = f.news_id
            {where_sql}
            """
        ),
        params,
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        text(
            f"""
            SELECT
                f.id AS favorite_id,
                f.created_at AS favorite_time,
                n.id,
                n.title,
                n.description,
                n.image,
                n.author,
                n.category_id,
                c.name AS category_name,
                n.views,
                n.publish_time
            FROM favorite f
            JOIN news n ON n.id = f.news_id
            LEFT JOIN news_category c ON c.id = n.category_id
            {where_sql}
            ORDER BY f.created_at DESC, f.id DESC
            LIMIT :offset, :page_size
            """
        ),
        params,
    )
    return total, result.fetchall()
