# Source path: backend/services/achievements.py

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ItemType, TermORM, UserWordStatus, WordORM


class AchievementsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_daily_stats(self, user_id: int) -> dict:
        """Получение статистики за текущий день"""
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = today_start + timedelta(days=1)

        words_query = select(
            func.count(func.distinct(UserWordStatus.item_id))
        ).where(
            UserWordStatus.user_id == user_id,
            UserWordStatus.item_type == ItemType.WORD,
            UserWordStatus.last_reviewed.between(today_start, today_end),
        )

        terms_query = select(
            func.count(func.distinct(UserWordStatus.item_id))
        ).where(
            UserWordStatus.user_id == user_id,
            UserWordStatus.item_type == ItemType.TERM,
            UserWordStatus.last_reviewed.between(today_start, today_end),
        )

        words_count = await self.session.execute(words_query)
        terms_count = await self.session.execute(terms_query)

        return {
            'words': words_count.scalar() or 0,
            'terms': terms_count.scalar() or 0,
        }

    async def get_total_stats(self, user_id: int) -> dict:
        """Получение общей статистики"""
        words_query = select(
            func.count(func.distinct(UserWordStatus.item_id))
        ).where(
            UserWordStatus.user_id == user_id,
            UserWordStatus.item_type == ItemType.WORD,
            UserWordStatus.last_reviewed.isnot(None),
        )

        terms_query = select(
            func.count(func.distinct(UserWordStatus.item_id))
        ).where(
            UserWordStatus.user_id == user_id,
            UserWordStatus.item_type == ItemType.TERM,
            UserWordStatus.last_reviewed.isnot(None),
        )

        words_count = await self.session.execute(words_query)
        terms_count = await self.session.execute(terms_query)

        return {
            'total_words': words_count.scalar() or 0,
            'total_terms': terms_count.scalar() or 0,
        }
        
    async def get_total_items_count(self) -> dict:
        """Получение общего количества слов и терминов в базе"""
        words_count = await self.session.execute(select(func.count()).select_from(WordORM))
        terms_count = await self.session.execute(select(func.count()).select_from(TermORM))
        
        return {
            'total_available_words': words_count.scalar() or 0,
            'total_available_terms': terms_count.scalar() or 0
        }
