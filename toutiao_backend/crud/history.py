from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def history_to_dict(row):
    return dict(row._mapping)


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(
        text(
            """
            INSERT INTO history (user_id, news_id)
            VALUES (:user_id, :news_id)
            """
        ),
        {"user_id": user_id, "news_id": news_id},
    )
    await db.commit()
    return result.lastrowid


async def get_history_by_id(db: AsyncSession, history_id: int):
    result = await db.execute(
        text("SELECT * FROM history WHERE id = :history_id"),
        {"history_id": history_id},
    )
    return result.fetchone()


async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    params = {
        "user_id": user_id,
        "offset": (page - 1) * page_size,
        "page_size": page_size,
    }

    total_result = await db.execute(
        text("SELECT COUNT(*) FROM history WHERE user_id = :user_id"),
        params,
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        text(
            """
            SELECT
                h.id AS history_id,
                h.view_time,
                n.id,
                n.title,
                n.description,
                n.image,
                n.author,
                n.category_id,
                c.name AS category_name,
                n.views,
                n.publish_time
            FROM history h
            JOIN news n ON n.id = h.news_id
            LEFT JOIN news_category c ON c.id = n.category_id
            WHERE h.user_id = :user_id
            ORDER BY h.view_time DESC, h.id DESC
            LIMIT :offset, :page_size
            """
        ),
        params,
    )
    return total, result.fetchall()


async def delete_history(db: AsyncSession, history_id: int, user_id: int):
    await db.execute(
        text("DELETE FROM history WHERE id = :history_id AND user_id = :user_id"),
        {"history_id": history_id, "user_id": user_id},
    )
    await db.commit()


async def clear_history(db: AsyncSession, user_id: int):
    await db.execute(text("DELETE FROM history WHERE user_id = :user_id"), {"user_id": user_id})
    await db.commit()
