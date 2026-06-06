from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.news import News, NewsCategory, RelatedNews


async def get_categories(db: AsyncSession):
    result = await db.execute(
        select(NewsCategory).order_by(NewsCategory.sort_order.asc(), NewsCategory.id.asc())
    )
    return result.scalars().all()


async def get_news_list(
    db: AsyncSession,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
):
    filters = []

    if category_id is not None:
        filters.append(News.category_id == category_id)

    if keyword:
        like_keyword = f"%{keyword}%"
        filters.append(
            or_(
                News.title.like(like_keyword),
                News.description.like(like_keyword),
                News.content.like(like_keyword),
            )
        )

    count_stmt = select(func.count()).select_from(News)
    list_stmt = select(News).options(joinedload(News.category))

    if filters:
        count_stmt = count_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    list_stmt = (
        list_stmt
        .order_by(News.publish_time.desc(), News.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    list_result = await db.execute(list_stmt)
    news_list = list_result.scalars().all()

    return total, news_list


async def get_news_by_id(db: AsyncSession, news_id: int):
    result = await db.execute(
        select(News)
        .options(joinedload(News.category))
        .where(News.id == news_id)
    )
    return result.scalar_one_or_none()


async def increase_news_views(db: AsyncSession, news: News):
    news.views = int(news.views or 0) + 1
    await db.commit()
    return news


async def get_related_news(db: AsyncSession, news_id: int, limit: int = 5):
    result = await db.execute(
        select(News)
        .join(RelatedNews, RelatedNews.related_news_id == News.id)
        .options(joinedload(News.category))
        .where(RelatedNews.news_id == news_id)
        .order_by(News.publish_time.desc(), News.id.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_category_by_id(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(NewsCategory).where(NewsCategory.id == category_id)
    )
    return result.scalar_one_or_none()


async def create_news(
    db: AsyncSession,
    title: str,
    content: str,
    category_id: int,
    description: Optional[str] = None,
    image: Optional[str] = None,
    author: Optional[str] = None,
    publish_time: Optional[datetime] = None,
):
    news = News(
        title=title,
        description=description,
        content=content,
        image=image,
        author=author,
        category_id=category_id,
        publish_time=publish_time or datetime.now(),
    )

    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


async def update_news(db: AsyncSession, news: News, **kwargs):
    for key, value in kwargs.items():
        if value is not None:
            setattr(news, key, value)

    await db.commit()
    return news


async def delete_news(db: AsyncSession, news: News):
    await db.delete(news)
    await db.commit()
