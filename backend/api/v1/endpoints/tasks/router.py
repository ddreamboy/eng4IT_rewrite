# backend/api/v1/endpoints/tasks/router.py

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ValidationError
from backend.db.database import get_session

from .base import TaskRegistry, TaskRequest, TaskResponse

router = APIRouter()


@router.post('/generate', response_model=TaskResponse)
async def generate_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Генерация нового задания."""
    handler = TaskRegistry.get_handler(request.task_type)

    # Добавим логирование для отладки
    print(f'Доступные обработчики: {list(TaskRegistry._handlers.keys())}')
    print(f'Запрошенный тип задания: {request.task_type}')

    if not handler:
        raise ValidationError(f'Unknown task type: {request.task_type}')

    try:
        # Добавляем сессию в параметры
        params = {**request.params, 'session': session}

        # Запускаем генерацию
        result = await handler.generate(params)

        return TaskResponse(
            task_id=f'{request.task_type}_{id(request)}',
            status='completed',
            result=result,
        )

    except Exception as e:
        return TaskResponse(task_id='error', status='error', error=str(e))
