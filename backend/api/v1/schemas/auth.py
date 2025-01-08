# api/v1/schemas/auth.py

from datetime import datetime
from typing import Optional

from core.security import check_password_strength
from pydantic import BaseModel, EmailStr, constr, validator


class UserCreate(BaseModel):
    """Схема для создания пользователя."""

    username: constr(min_length=3, max_length=50)  # type: ignore
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        is_valid, error_message = check_password_strength(v)
        if not is_valid:
            raise ValueError(error_message)
        return v


class UserLogin(BaseModel):
    """Схема для входа пользователя."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема токена доступа."""

    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    """Схема полезной нагрузки токена."""

    sub: Optional[int] = None
    exp: Optional[datetime] = None
