# api/v1/schemas/auth.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.core.security import check_password_strength


class UserCreate(BaseModel):
    """Схема для создания пользователя."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description='Имя пользователя (от 3 до 50 символов)',
        example='john_doe',
    )
    email: EmailStr = Field(
        ..., description='Email пользователя', example='user@example.com'
    )
    password: str = Field(
        ...,
        description="""
        Пароль должен содержать:
        - Минимум 8 символов
        - Хотя бы одну заглавную букву
        - Хотя бы одну строчную букву
        - Хотя бы одну цифру
        - Хотя бы один специальный символ (!@#$%^&*()_+-=[]{}|;:,.<>?)
        """,
        example='StrongP@ss123',
    )

    @field_validator('password')
    def validate_password(cls, v):
        is_valid, error_message = check_password_strength(v)
        if not is_valid:
            raise ValueError(error_message)
        return v

    model_config = {
        'json_schema_extra': {
            'example': {
                'username': 'john_doe',
                'email': 'user@example.com',
                'password': 'StrongP@ss123',
            }
        }
    }


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
