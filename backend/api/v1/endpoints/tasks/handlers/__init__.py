from ..base import TaskRegistry
from .activity_name import ActivityNameHandler

# Регистрируем обработчики
TaskRegistry.register('activity_name', ActivityNameHandler())
