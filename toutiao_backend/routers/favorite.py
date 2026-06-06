from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_cond import get_db
from crud import favorite as favorite_crud
from crud import news as news_crud
from routers.user import get_current_user
from schemas.favorite import FavoriteCreate


router = APIRouter(prefix="/favorite", tags=["Favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    favorite = await favorite_crud.check_favorite(db, current_user.id, news_id)
    return {"is_favorite": favorite is not None}


@router.post("/add")
async def add_favorite(
    data: FavoriteCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    news = await news_crud.get_news_by_id(db, data.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    await favorite_crud.add_favorite(db, current_user.id, data.news_id)
    return {"message": "Favorite add success"}


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await favorite_crud.remove_favorite(db, current_user.id, news_id)
    return {"message": "Favorite remove success"}


@router.get("/list")
async def favorite_list(
    keyword: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total, favorites = await favorite_crud.get_favorite_list(
        db,
        current_user.id,
        page,
        page_size,
        keyword,
    )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "list": [favorite_crud.news_to_dict(item) for item in favorites],
    }


@router.delete("/clear")
async def clear_favorite(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await favorite_crud.clear_favorites(db, current_user.id)
    return {"message": "Favorite clear success"}
