from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_cond import get_db
from crud import history as history_crud
from crud import news as news_crud
from routers.user import get_current_user
from schemas.history import HistoryCreate


router = APIRouter(prefix="/history", tags=["History"])


@router.post("/add")
async def add_history(
    data: HistoryCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    news = await news_crud.get_news_by_id(db, data.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    await history_crud.add_history(db, current_user.id, data.news_id)
    return {"message": "History add success"}


@router.get("/list")
async def history_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total, histories = await history_crud.get_history_list(
        db,
        current_user.id,
        page,
        page_size,
    )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "list": [history_crud.history_to_dict(item) for item in histories],
    }


@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    history = await history_crud.get_history_by_id(db, history_id)
    if not history or history.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="History not found")

    await history_crud.delete_history(db, history_id, current_user.id)
    return {"message": "History delete success"}


@router.delete("/clear")
async def clear_history(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await history_crud.clear_history(db, current_user.id)
    return {"message": "History clear success"}
