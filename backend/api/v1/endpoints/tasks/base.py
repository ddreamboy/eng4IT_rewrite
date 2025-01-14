from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class TaskRequest(BaseModel):
    """Базовая модель запроса для всех типов заданий."""

    task_type: str
    user_id: int
    params: Dict[str, Any]


class TaskResponse(BaseModel):
    """Базовая модель ответа для всех типов заданий."""

    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseTaskHandler(ABC):
    """Базовый класс для всех обработчиков заданий."""

    def __init__(self):
        """Инициализация обработчика."""
        self.task_type: str = self.__class__.__name__.lower().replace(
            'handler', ''
        )

    @abstractmethod
    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация задания.

        Args:
            params: Параметры для генерации задания

        Returns:
            Dict[str, Any]: Сгенерированное задание
        """
        pass

    @abstractmethod
    async def validate(self, task_id: str, answer: Dict[str, Any]) -> bool:
        """
        Проверка ответа на задание.

        Args:
            task_id: Идентификатор задания
            answer: Ответ пользователя

        Returns:
            bool: Результат проверки
        """
        pass

    async def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка ответа от AI сервиса.

        Args:
            response: Ответ от AI

        Returns:
            Dict[str, Any]: Обработанный ответ
        """
        # Базовая реализация просто возвращает ответ как есть
        # Наследники могут переопределить для своей логики
        return response


class TaskRegistry:
    """Реестр обработчиков заданий."""

    _handlers: Dict[str, BaseTaskHandler] = {}

    @classmethod
    def register(cls, task_type: str, handler: BaseTaskHandler) -> None:
        """
        Регистрация обработчика для типа задания.

        Args:
            task_type: Тип задания
            handler: Обработчик задания
        """
        print(f'Регистрируем обработчик {task_type}')
        cls._handlers[task_type] = handler

    @classmethod
    def get_handler(cls, task_type: str) -> Optional[BaseTaskHandler]:
        """
        Получение обработчика по типу задания.

        Args:
            task_type: Тип задания

        Returns:
            Optional[BaseTaskHandler]: Обработчик задания или None
        """
        print(f'Доступные обработчики: {list(cls._handlers.keys())}')
        return cls._handlers.get(task_type)
