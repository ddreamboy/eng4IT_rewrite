# backend/api/v1/endpoints/users.py

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_current_user_id, get_session
from backend.db.models import (
    ItemType,
    LearningAttempt,
    TermORM,
    UserORM,
    UserWordStatus,
    WordORM,
)

from ..schemas.profile import (
    UserProfileResponse,
    UserStatistics,
    WordDetails,
    WordsDetailedStats,
)

router = APIRouter()


async def get_detailed_word_statistics(
    session: AsyncSession, user_id: int
) -> WordsDetailedStats:
    """Получение детальной статистики по каждому слову/термину"""

    # Запрос для слов
    words_query = (
        select(UserWordStatus, WordORM.word, WordORM.difficulty)
        .join(
            WordORM,
            and_(
                UserWordStatus.item_id == WordORM.id,
                UserWordStatus.item_type == ItemType.WORD,
            ),
        )
        .where(UserWordStatus.user_id == user_id)
    )

    # Запрос для терминов
    terms_query = (
        select(UserWordStatus, TermORM.term, TermORM.difficulty)
        .join(
            TermORM,
            and_(
                UserWordStatus.item_id == TermORM.id,
                UserWordStatus.item_type == ItemType.TERM,
            ),
        )
        .where(UserWordStatus.user_id == user_id)
    )

    # Выполняем запросы параллельно
    words_result, terms_result = await asyncio.gather(
        session.execute(words_query), session.execute(terms_query)
    )

    # Обрабатываем результаты для слов
    words_stats = [
        WordDetails(
            id=word_status.id,
            word=word,
            type=ItemType.WORD,
            difficulty=difficulty,
            is_favorite=word_status.is_favorite,
            is_known=word_status.is_known,
            mastery_level=word_status.mastery_level,
            last_reviewed=word_status.last_reviewed,
            next_review_date=word_status.next_review_date,
            ease_factor=word_status.ease_factor,
            interval_level=word_status.interval_level,
        )
        for word_status, word, difficulty in words_result
    ]

    # Обрабатываем результаты для терминов
    terms_stats = [
        WordDetails(
            id=term_status.id,
            word=term,
            type=ItemType.TERM,
            difficulty=difficulty,
            is_favorite=term_status.is_favorite,
            is_known=term_status.is_known,
            mastery_level=term_status.mastery_level,
            last_reviewed=term_status.last_reviewed,
            next_review_date=term_status.next_review_date,
            ease_factor=term_status.ease_factor,
            interval_level=term_status.interval_level,
        )
        for term_status, term, difficulty in terms_result
    ]

    return WordsDetailedStats(words=words_stats, terms=terms_stats)


async def get_user_statistics(
    session: AsyncSession, user_id: int
) -> UserStatistics:
    """Получение полной статистики пользователя"""

    # Все запросы делаем параллельно для оптимизации
    attempts_query = select(
        func.count().label('total'),
        func.sum(case((LearningAttempt.is_successful, 1), else_=0)).label(
            'successful'
        ),
    ).where(LearningAttempt.user_id == user_id)

    favorite_items_query = (
        select(WordORM.word)
        .join(UserWordStatus, UserWordStatus.item_id == WordORM.id)
        .where(
            UserWordStatus.user_id == user_id,
            UserWordStatus.is_favorite,
            UserWordStatus.item_type == ItemType.WORD,
        )
        .union_all(
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
        .where(
            LearningAttempt.user_id == user_id,
            LearningAttempt.item_type == ItemType.TERM,
        )
        .group_by(TermORM.category_main)
    )

    # Выполняем все запросы параллельно
    (
        attempts_result,
        favorite_result,
        category_results,
        detailed_stats,
    ) = await asyncio.gather(
        session.execute(attempts_query),
        session.execute(favorite_items_query),
        session.execute(category_progress_query),
        get_detailed_word_statistics(session, user_id),
    )

    # Обрабатываем результаты
    attempts_stats = attempts_result.first()
    total = attempts_stats.total or 0
    successful = attempts_stats.successful or 0

    favorite_items = [item[0] for item in favorite_result]

    category_progress = {
        row.category_main: float(row.progress) for row in category_results
    }

    accuracy_rate = (successful / total * 100) if total > 0 else 0

    return UserStatistics(
        total_tasks=total,
        completed_tasks=successful,
        accuracy_rate=accuracy_rate,
        study_streak=0,
        favorite_words=favorite_items,
        category_progress=category_progress,
        detailed_stats=detailed_stats,
    )


@router.get('/profile', response_model=UserProfileResponse)
async def get_user_profile(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Получение полного профиля пользователя"""

    # 1. Получаем пользователя со всеми необходимыми полями сразу
    user_query = (
        select(UserORM)
        .options(
            # Явно указываем, какие поля нам нужны
            selectinload(UserORM.learning_attempts),
            selectinload(UserORM.word_statuses),
        )
        .where(UserORM.id == current_user_id)
    )

    result = await session.execute(user_query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # 2. Сохраняем все необходимые данные до закрытия сессии
    user_data = {
        'username': user.username,
        'email': user.email,
        'current_level': user.current_level,
        'proficiency_score': user.proficiency_score,
        'daily_goal': user.daily_goal,
        'study_streak': user.study_streak,
        'total_attempts': user.total_attempts,
        'successful_attempts': user.successful_attempts,
        'created_at': user.created_at,
        'last_login': user.last_login,
    }

    # 3. Получаем статистику
    statistics = await get_user_statistics(session, current_user_id)

    # 4. Обновляем last_login
    update_stmt = (
        update(UserORM)
        .where(UserORM.id == current_user_id)
        .values(last_login=datetime.utcnow())
        .execution_options(synchronize_session=False)
    )
    await session.execute(update_stmt)
    await session.commit()

    # 5. Возвращаем собранные данные
    return UserProfileResponse(**user_data, statistics=statistics)
