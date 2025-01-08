from typing import Any, Dict

from ai.gemini import GeminiServiceSinglethon
from ai.operations import ActivityName
from core.task_store import task_store

from ..base import BaseTaskHandler


class ActivityNameHandler(BaseTaskHandler):
    """Обработчик для генерации имен активностей."""

    def __init__(self):
        super().__init__()
        self.ai_service = GeminiServiceSinglethon
        self.operation = ActivityName()

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация имени активности.

        Args:
            params: Параметры для генерации

        Returns:
            Dict[str, Any]: Результат генерации
        """
        try:
            result = await self.operation.execute(params)
            await task_store.set_status(
                task_id=f'activity_{id(params)}', status='completed', result=result
            )
            return result
        except Exception as e:
            await task_store.set_status(
                task_id=f'activity_{id(params)}', status='error', error=str(e)
            )
            raise

    async def validate(self, task_id: str, answer: Dict[str, Any]) -> bool:
        """
        Проверка ответа.

        Args:
            task_id: ID задания
            answer: Ответ пользователя

        Returns:
            bool: Результат проверки
        """
        # Для этого типа задания валидация не требуется
        return True
