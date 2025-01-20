from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

from backend.db.models import DifficultyLevel, ItemType


class WordDetails(BaseModel):
    """Детальная информация по слову/термину"""

    id: int
    word: str  # слово или термин
    type: ItemType
    difficulty: DifficultyLevel
    is_favorite: bool
    is_known: bool
    mastery_level: float
    last_reviewed: Optional[datetime]
    next_review_date: Optional[datetime]
    ease_factor: float
    interval_level: int


class WordsDetailedStats(BaseModel):
    """Детальная статистика по всем словам пользователя"""

    words: List[WordDetails] = Field(description='Статистика по каждому слову')
    terms: List[WordDetails] = Field(description='Статистика по каждому термину')


class UserStatistics(BaseModel):
    total_tasks: int
    completed_tasks: int
    accuracy_rate: float
    study_streak: int
    favorite_words: List[str]
    category_progress: Dict[str, float]
    detailed_stats: WordsDetailedStats


class UserProfileResponse(BaseModel):
    """Полный профиль пользователя с статистикой"""

    username: str
    email: EmailStr
    current_level: DifficultyLevel
    proficiency_score: float
    daily_goal: int
    study_streak: int
    total_attempts: int
    successful_attempts: int
    created_at: datetime
    last_login: Optional[datetime]
    statistics: UserStatistics
