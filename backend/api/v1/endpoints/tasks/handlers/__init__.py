# backend/api/v1/endpoints/tasks/handlers/__init__.py

from typing import Dict

from ..base import BaseTaskHandler, TaskRegistry
from .activity_name import ActivityNameHandler
from .chat_dialog import ChatDialogHandler
from .term_definition import TermDefinitionTaskHandler
from .word_matching import WordMatchingTaskHandler
from .word_translation import WordTranslationTaskHandler

_handlers: Dict[str, BaseTaskHandler] = {
    'activity_name': ActivityNameHandler(),
    'word_translation': WordTranslationTaskHandler(),
    'word_matching': WordMatchingTaskHandler(),
    'term_definition': TermDefinitionTaskHandler(),
    'chat_dialog': ChatDialogHandler(),
}


def register_handlers() -> None:
    """Регистрация всех обработчиков задач"""
    for task_type, handler in _handlers.items():
        TaskRegistry.register(task_type, handler)
