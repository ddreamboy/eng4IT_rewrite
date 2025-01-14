from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from backend.db.models import DifficultyLevel


class UserStatistics(BaseModel):
    total_tasks: int
    completed_tasks: int
    accuracy_rate: float
    study_streak: int
    favorite_words: List[str]
    category_progress: Dict[str, float]


class UserProfileResponse(BaseModel):
    username: str
    email: str
    current_level: DifficultyLevel
    proficiency_score: float
    daily_goal: int
    study_streak: int
    total_attempts: int
    successful_attempts: int
    created_at: datetime
    last_login: datetime
    statistics: Optional[UserStatistics] = None

    class Config:
        from_attributes = True
