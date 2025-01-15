# backend/api/v1/endpoints/users.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user_id, get_session
from backend.db.models import (
    ItemType,
    LearningAttempt,
    TermORM,
    UserORM,
    UserWordStatus,
    WordORM,
)

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
    favorite_items_query = (
        # Подзапрос для слов
        select(WordORM.word)
        .join(UserWordStatus, UserWordStatus.item_id == WordORM.id)
        .where(
            UserWordStatus.user_id == user_id,
            UserWordStatus.is_favorite,
            UserWordStatus.item_type == ItemType.WORD,
        )
        .union_all(
            # Подзапрос для терминов
            select(TermORM.term)
            .join(UserWordStatus, UserWordStatus.item_id == TermORM.id)
            .where(
                UserWordStatus.user_id == user_id,
                UserWordStatus.is_favorite,
                UserWordStatus.item_type == ItemType.TERM,
            )
        )
        .limit(5)
    )
    favorite_items_result = await session.execute(favorite_items_query)
    favorite_items = [item[0] for item in favorite_items_result]

    category_progress_query = (
        select(
            TermORM.category_main,
            (
                func.sum(case((LearningAttempt.is_successful, 1), else_=0))
                * 100.0
                / func.count(LearningAttempt.id)
            ).label('progress'),
        )
        .join(TermORM, TermORM.id == LearningAttempt.item_id)
        .where(LearningAttempt.user_id == user_id)
        .group_by(TermORM.category_main)
    )
    category_results = await session.execute(category_progress_query)
    category_progress_rows = category_results.all()
    category_progress = (
        {row.category_main: float(row.progress) for row in category_progress_rows}
        if category_progress_rows
        else {}
    )

    return UserStatistics(
        total_tasks=attempts_stats.total or 0,
        completed_tasks=attempts_stats.successful or 0,
        accuracy_rate=attempts_stats.successful / attempts_stats.total * 100
        if attempts_stats.total
        else 0,
        study_streak=0,  # Будет реализовано позже
        favorite_words=favorite_items,
        category_progress=category_progress,
    )


@router.get('/profile', response_model=UserProfileResponse)
async def get_user_profile(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Получает полный профиль пользователя с статистикой"""

    # Получаем пользователя без selectinload
    stmt = select(UserORM).where(UserORM.id == current_user_id)
    result = await session.execute(stmt)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    # Получаем статистику
    statistics = await get_user_statistics(session, current_user_id)

    # Обновляем last_login через отдельный запрос
    await session.execute(
        select(UserORM)
        .where(UserORM.id == current_user_id)
        .execution_options(synchronize_session=False)
    )

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
