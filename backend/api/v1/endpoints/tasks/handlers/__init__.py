# backend/api/v1/endpoints/tasks/handlers/__init__.py

from typing import Dict

from ..base import BaseTaskHandler, TaskRegistry
from .activity_name import ActivityNameHandler
from .translation import TranslationTaskHandler

_handlers: Dict[str, BaseTaskHandler] = {
    'activity_name': ActivityNameHandler(),
    'translation': TranslationTaskHandler(),
}


def register_handlers() -> None:
    """Регистрация всех обработчиков задач"""
    for task_type, handler in _handlers.items():
        TaskRegistry.register(task_type, handler)
