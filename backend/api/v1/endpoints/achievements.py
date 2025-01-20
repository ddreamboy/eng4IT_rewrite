# Source path: backend/api/v1/endpoints/achievements.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user_id, get_session
from backend.services.achievements import AchievementsService

router = APIRouter()


@router.get('/stats')
async def get_achievement_stats(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    service = AchievementsService(session)

    # Получаем статистику и общие количества
    total_available = await service.get_total_items_count()
    daily_stats = await service.get_daily_stats(current_user_id)
    total_stats = await service.get_total_stats(current_user_id)

    # 30% от общего количества как цель
    words_goal = int(total_available['total_available_words'] * 0.3)
    terms_goal = int(total_available['total_available_terms'] * 0.3)

    # Для ежедневных целей используем фиксированные значения
    daily_goals_achieved = {
        'words': daily_stats['words'] >= 30,  # фиксированная цель
        'terms': daily_stats['terms'] >= 10,  # фиксированная цель
    }

    # Для общих целей используем динамические значения
    total_goals_achieved = {
        'words': total_stats['total_words'] >= words_goal,
        'terms': total_stats['total_terms'] >= terms_goal,
    }

    return {
        'daily_stats': {
            **daily_stats,
            'goals_achieved': daily_goals_achieved,
            'goals': {
                'words': 30,  # фиксированные ежедневные цели
                'terms': 10,
            },
        },
        'total_stats': {
            **total_stats,
            'goals_achieved': total_goals_achieved,
            'goals': {'words': words_goal, 'terms': terms_goal},
            'available': total_available,
        },
    }
