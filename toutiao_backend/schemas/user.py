from typing import Optional

from pydantic import BaseModel, Field, field_validator


def validate_new_password(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("password must be at most 72 UTF-8 bytes")
    return value


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar: Optional[str] = Field(default=None, max_length=255)
    gender: Optional[str] = "unknown"
    bio: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)

    _validate_password = field_validator("password")(validate_new_password)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar: Optional[str] = Field(default=None, max_length=255)
    gender: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)

    _validate_new_password = field_validator("new_password")(validate_new_password)
