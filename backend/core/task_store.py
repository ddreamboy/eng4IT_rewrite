import json
from datetime import timedelta
from typing import Dict, Optional

import redis.asyncio as redis

from backend.core.config import settings


class TaskStatusStore:
    """Хранилище статусов заданий в Redis."""

    def __init__(self):
        """Инициализация подключения к Redis."""
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    async def set_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        ttl: int = 3600,  # 1 час по умолчанию
    ) -> None:
        """
        Установка статуса задания.

        Args:
            task_id: ID задания
            status: Статус
            result: Результат выполнения
            error: Ошибка если есть
            ttl: Время жизни записи в секундах
        """
        data = {'status': status, 'result': result, 'error': error}

        await self.redis.setex(
            f'task:{task_id}', timedelta(seconds=ttl), json.dumps(data)
        )

    async def get_status(self, task_id: str) -> Optional[Dict]:
        """
        Получение статуса задания.

        Args:
            task_id: ID задания

        Returns:
            Optional[Dict]: Данные о статусе или None
        """
        data = await self.redis.get(f'task:{task_id}')
        if data:
            return json.loads(data)
        return None

    async def delete_status(self, task_id: str) -> None:
        """
        Удаление статуса задания.

        Args:
            task_id: ID задания
        """
        await self.redis.delete(f'task:{task_id}')


# Глобальный экземпляр хранилища
task_store = TaskStatusStore()
