from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_cond import get_db
from crud import news as news_crud
from routers.user import require_admin
from utils.cache import delete_cache, delete_pattern, get_cache, set_cache


router = APIRouter(
    prefix="/news",
    tags=["新闻模块"]
)


class NewsCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    publish_time: Optional[datetime] = None


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[int] = None
    publish_time: Optional[datetime] = None


def category_to_dict(item):
    return {
        "id": item.id,
        "name": item.name,
        "sort_order": item.sort_order,
    }


def news_to_dict(item, include_content: bool = False):
    data = {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "image": item.image,
        "author": item.author,
        "category_id": item.category_id,
        "category_name": item.category.name if item.category else None,
        "views": item.views,
        "publish_time": item.publish_time,
    }

    if include_content:
        data["content"] = item.content

    return data


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    cache_key = "news:categories"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    categories = await news_crud.get_categories(db)
    data = [category_to_dict(item) for item in categories]
    await set_cache(cache_key, data, expire=7200)
    return data


@router.get("/list")
async def get_news_list(
    category_id: Optional[int] = Query(default=None, description="分类ID"),
    keyword: Optional[str] = Query(default=None, description="关键词"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"news:list:{category_id or 'all'}:{keyword or 'none'}:{page}:{page_size}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    total, news_list = await news_crud.get_news_list(
        db=db,
        category_id=category_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    data = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "list": [news_to_dict(item) for item in news_list],
    }
    await set_cache(cache_key, data, expire=1800)
    return data


@router.get("/detail/{news_id}")
async def get_news_detail(
    news_id: int,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"news:detail:{news_id}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    news = await news_crud.get_news_by_id(db, news_id)

    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    news = await news_crud.increase_news_views(db, news)
    related_news = await news_crud.get_related_news(db, news_id, limit=5)

    data = news_to_dict(news, include_content=True)
    data["related_news"] = [news_to_dict(item) for item in related_news]

    await set_cache(cache_key, data, expire=3600)
    return data


@router.post("/")
async def create_news(
    data: NewsCreate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    category = await news_crud.get_category_by_id(db, data.category_id)

    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    news = await news_crud.create_news(
        db=db,
        title=data.title,
        description=data.description,
        content=data.content,
        image=data.image,
        author=data.author,
        category_id=data.category_id,
        publish_time=data.publish_time,
    )

    news = await news_crud.get_news_by_id(db, news.id)
    await delete_pattern("news:list:*")
    await delete_cache("news:categories")
    return news_to_dict(news, include_content=True)


@router.put("/{news_id}")
async def update_news(
    news_id: int,
    data: NewsUpdate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    news = await news_crud.get_news_by_id(db, news_id)

    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    if data.category_id is not None:
        category = await news_crud.get_category_by_id(db, data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")

    news = await news_crud.update_news(
        db=db,
        news=news,
        **data.model_dump(),
    )

    news = await news_crud.get_news_by_id(db, news.id)
    await delete_pattern("news:list:*")
    await delete_cache(f"news:detail:{news_id}")
    await delete_cache("news:categories")
    return news_to_dict(news, include_content=True)


@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    news = await news_crud.get_news_by_id(db, news_id)

    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    await news_crud.delete_news(db, news)
    await delete_pattern("news:list:*")
    await delete_cache(f"news:detail:{news_id}")

    return {"message": "新闻删除成功"}
