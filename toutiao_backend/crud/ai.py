from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def save_ai_chat(
    db: AsyncSession,
    user_id: int,
    message: str,
    response: str,
):
    result = await db.execute(
        text(
            """
            INSERT INTO ai_chat (user_id, message, response)
            VALUES (:user_id, :message, :response)
            """
        ),
        {
            "user_id": user_id,
            "message": message,
            "response": response,
        },
    )
    await db.commit()
    return result.lastrowid


async def get_ai_chat_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
):
    params = {
        "user_id": user_id,
        "offset": (page - 1) * page_size,
        "page_size": page_size,
    }

    total_result = await db.execute(
        text("SELECT COUNT(*) FROM ai_chat WHERE user_id = :user_id"),
        params,
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        text(
            """
            SELECT id, user_id, message, response, created_at
            FROM ai_chat
            WHERE user_id = :user_id
            ORDER BY created_at DESC, id DESC
            LIMIT :offset, :page_size
            """
        ),
        params,
    )
    return total, result.fetchall()


async def get_user_recent_news_context(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
):
    result = await db.execute(
        text(
            """
            SELECT DISTINCT n.id, n.title, n.description, c.name AS category_name
            FROM history h
            JOIN news n ON n.id = h.news_id
            LEFT JOIN news_category c ON c.id = n.category_id
            WHERE h.user_id = :user_id
            ORDER BY h.view_time DESC
            LIMIT :limit
            """
        ),
        {"user_id": user_id, "limit": limit},
    )
    return result.fetchall()


async def get_user_favorite_news_context(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
):
    result = await db.execute(
        text(
            """
            SELECT DISTINCT n.id, n.title, n.description, c.name AS category_name
            FROM favorite f
            JOIN news n ON n.id = f.news_id
            LEFT JOIN news_category c ON c.id = n.category_id
            WHERE f.user_id = :user_id
            ORDER BY f.created_at DESC
            LIMIT :limit
            """
        ),
        {"user_id": user_id, "limit": limit},
    )
    return result.fetchall()


async def search_news_for_recommendation(
    db: AsyncSession,
    keyword: Optional[str] = None,
    limit: int = 5,
):
    params = {"limit": limit}
    where_sql = ""

    if keyword:
        where_sql = "WHERE title LIKE :keyword OR description LIKE :keyword OR content LIKE :keyword"
        params["keyword"] = f"%{keyword}%"

    result = await db.execute(
        text(
            f"""
            SELECT id, title, description, image, author, category_id, views, publish_time
            FROM news
            {where_sql}
            ORDER BY publish_time DESC, views DESC
            LIMIT :limit
            """
        ),
        params,
    )
    return result.fetchall()


async def search_news_for_chat(
    db: AsyncSession,
    search_terms: list[str],
    category_name: Optional[str] = None,
    limit: int = 6,
):
    params = {"limit": limit}
    match_parts = []
    score_parts = []

    for index, term in enumerate(search_terms):
        param_name = f"keyword_{index}"
        params[param_name] = f"%{term}%"
        match_parts.append(
            f"(n.title LIKE :{param_name} "
            f"OR n.description LIKE :{param_name} "
            f"OR n.content LIKE :{param_name})"
        )
        score_parts.append(
            f"(CASE WHEN n.title LIKE :{param_name} THEN 5 ELSE 0 END + "
            f"CASE WHEN n.description LIKE :{param_name} THEN 3 ELSE 0 END + "
            f"CASE WHEN n.content LIKE :{param_name} THEN 1 ELSE 0 END)"
        )

    where_parts = []
    if match_parts:
        where_parts.append(f"({' OR '.join(match_parts)})")

    if category_name:
        where_parts.append("c.name = :category_name")
        params["category_name"] = category_name

    where_sql = " AND ".join(where_parts) or "1 = 1"
    score_sql = " + ".join(score_parts) or "0"

    result = await db.execute(
        text(
            f"""
            SELECT
                n.id,
                n.title,
                n.description,
                n.content,
                n.image,
                n.author,
                n.category_id,
                c.name AS category_name,
                n.views,
                n.publish_time,
                {score_sql} AS retrieval_score
            FROM news n
            LEFT JOIN news_category c ON c.id = n.category_id
            WHERE {where_sql}
            ORDER BY retrieval_score DESC, n.publish_time DESC, n.views DESC, n.id DESC
            LIMIT :limit
            """
        ),
        params,
    )
    rows = result.fetchall()

    if rows or (not match_parts and not category_name):
        return rows

    if category_name and match_parts:
        result = await db.execute(
            text(
                """
                SELECT
                    n.id,
                    n.title,
                    n.description,
                    n.content,
                    n.image,
                    n.author,
                    n.category_id,
                    c.name AS category_name,
                    n.views,
                    n.publish_time,
                    0 AS retrieval_score
                FROM news n
                LEFT JOIN news_category c ON c.id = n.category_id
                WHERE c.name = :category_name
                ORDER BY n.publish_time DESC, n.views DESC, n.id DESC
                LIMIT :limit
                """
            ),
            {"category_name": category_name, "limit": limit},
        )
        rows = result.fetchall()

    if rows:
        return rows

    result = await db.execute(
        text(
            """
            SELECT
                n.id,
                n.title,
                n.description,
                n.content,
                n.image,
                n.author,
                n.category_id,
                c.name AS category_name,
                n.views,
                n.publish_time,
                0 AS retrieval_score
            FROM news n
            LEFT JOIN news_category c ON c.id = n.category_id
            ORDER BY n.publish_time DESC, n.views DESC, n.id DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )
    return result.fetchall()
