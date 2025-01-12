from ..base import TaskRegistry
from .activity_name import ActivityNameHandler
from .translation import TranslationTaskHandler

# Регистрируем обработчики
TaskRegistry.register('activity_name', ActivityNameHandler())
TaskRegistry.register('translation', TranslationTaskHandler())
