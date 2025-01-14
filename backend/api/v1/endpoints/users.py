from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_db
from backend.db.models import LearningAttempt, UserORM, UserWordStatus

from ..schemas.profile import UserProfileResponse, UserStatistics

router = APIRouter()


async def get_user_statistics(
    session: AsyncSession, user_id: int
) -> Optional[UserStatistics]:
    # Получаем общую статистику попыток
    attempts_query = select(
        func.count().label('total'),
        func.sum(case((LearningAttempt.is_successful, 1), else_=0)).label(
            'successful'
        ),
    ).where(LearningAttempt.user_id == user_id)

    attempts_result = await session.execute(attempts_query)
    attempts_stats = attempts_result.first()

    # Получаем любимые слова
    favorite_words_query = (
        select(UserWordStatus)
        .where(UserWordStatus.user_id == user_id, UserWordStatus.is_favorite)
        .limit(5)
    )
    favorite_words_result = await session.execute(favorite_words_query)
    favorite_words = [word.item_id for word in favorite_words_result.scalars()]

    # Прогресс по категориям (упрощенно)
    category_progress = {
        'backend': 75.5,
        'frontend': 60.2,
        'database': 85.0,
        'network': 45.8,
    }

    return UserStatistics(
        total_tasks=attempts_stats.total or 0,
        completed_tasks=attempts_stats.successful or 0,
        accuracy_rate=attempts_stats.successful / attempts_stats.total * 100
        if attempts_stats.total
        else 0,
        study_streak=0,  # Будет реализовано позже
        favorite_words=favorite_words,
        category_progress=category_progress,
    )


@router.get('/profile', response_model=UserProfileResponse)
async def get_user_profile(
    current_user: UserORM = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Получает полный профиль пользователя с статистикой"""

    # Обновляем информацию о последнем входе
    current_user.last_login = func.now()
    session.add(current_user)

    # Получаем статистику
    statistics = await get_user_statistics(session, current_user.id)

    return UserProfileResponse(
        username=current_user.username,
        email=current_user.email,
        current_level=current_user.current_level,
        proficiency_score=current_user.proficiency_score,
        daily_goal=current_user.daily_goal,
        study_streak=current_user.study_streak,
        total_attempts=current_user.total_attempts,
        successful_attempts=current_user.successful_attempts,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        statistics=statistics,
    )
