from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_cond import get_db
from crud import user as user_crud
from schemas.user import PasswordUpdate, UserLogin, UserRegister, UserUpdate


router = APIRouter(prefix="/user", tags=["User"])


def get_access_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.strip().split()
    if len(parts) == 1 and parts[0].lower() != "bearer":
        return parts[0]
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    raise HTTPException(
        status_code=401,
        detail="Invalid Authorization header",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    token = get_access_token(authorization)
    user = await user_crud.get_user_by_token(db, token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(current_user=Depends(get_current_user)):
    if getattr(current_user, "role", "user") != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user


@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if data.gender not in user_crud.VALID_GENDERS:
        raise HTTPException(status_code=400, detail="Invalid gender")

    old_user = await user_crud.get_user_by_username(db, data.username)
    if old_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if data.phone:
        old_phone = await user_crud.get_user_by_phone(db, data.phone)
        if old_phone:
            raise HTTPException(status_code=400, detail="Phone already exists")

    user = await user_crud.create_user(db, data)
    return user_crud.user_to_dict(user)


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_username(db, data.username)

    if not user or not user_crud.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    token, expires_at = await user_crud.create_token(db, user.id)

    return {
        "token": token,
        "expires_at": expires_at,
        "user": user_crud.user_to_dict(user),
    }


@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if authorization:
        token = get_access_token(authorization)
        await user_crud.delete_token(db, token)

    return {"message": "Logout success"}


@router.get("/info")
async def user_info(current_user=Depends(get_current_user)):
    return user_crud.user_to_dict(current_user)


@router.get("/list")
async def user_list(
    keyword: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total, users = await user_crud.get_user_list(db, keyword, page, page_size)
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "list": [user_crud.user_to_dict(item) for item in users],
    }


@router.get("/detail/{user_id}")
async def user_detail(
    user_id: int,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.user_to_dict(user)


@router.put("/update")
async def update_my_info(
    data: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)

    if "gender" in update_data and update_data["gender"] not in user_crud.VALID_GENDERS:
        raise HTTPException(status_code=400, detail="Invalid gender")

    if update_data.get("phone"):
        old_phone = await user_crud.get_user_by_phone(db, update_data["phone"], current_user.id)
        if old_phone:
            raise HTTPException(status_code=400, detail="Phone already exists")

    user = await user_crud.update_user(db, current_user.id, update_data)
    return user_crud.user_to_dict(user)


@router.put("/password")
async def update_password(
    data: PasswordUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user_crud.verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is wrong")

    user = await user_crud.update_user(
        db,
        current_user.id,
        {"password": user_crud.hash_password(data.new_password)},
    )
    return user_crud.user_to_dict(user)


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)

    if "gender" in update_data and update_data["gender"] not in user_crud.VALID_GENDERS:
        raise HTTPException(status_code=400, detail="Invalid gender")

    if update_data.get("phone"):
        old_phone = await user_crud.get_user_by_phone(db, update_data["phone"], user_id)
        if old_phone:
            raise HTTPException(status_code=400, detail="Phone already exists")

    user = await user_crud.update_user(db, user_id, update_data)
    return user_crud.user_to_dict(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_crud.delete_user(db, user_id)
    return {"message": "User delete success"}
