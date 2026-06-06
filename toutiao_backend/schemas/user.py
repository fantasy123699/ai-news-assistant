from typing import Optional

from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = "unknown"
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
