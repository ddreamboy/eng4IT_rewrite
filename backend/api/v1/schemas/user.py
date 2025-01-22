# api/v1/schemas/user.py

from typing import Dict, Optional

from pydantic import BaseModel, EmailStr

from backend.db.models import DifficultyLevel


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    settings: Optional[Dict] = None
    learning_preferences: Optional[Dict] = None
    daily_goal: Optional[int] = None
    current_level: Optional[DifficultyLevel] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""

    id: int
    current_level: DifficultyLevel
    proficiency_score: float
    study_streak: int
    total_attempts: int
    successful_attempts: int

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Расширенная схема профиля пользователя."""

    settings: Dict
    learning_preferences: Dict
    daily_goal: int

    class Config:
        from_attributes = True
