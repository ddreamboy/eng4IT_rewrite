from typing import Dict

from core.exceptions import ValidationError
from db.database import get_session
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.tasks.handlers import *

from .base import TaskRegistry, TaskRequest, TaskResponse

router = APIRouter()


@router.post('/generate', response_model=TaskResponse)
async def generate_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Генерация нового задания.

    Args:
        request: Параметры для генерации задания
        background_tasks: Фоновые задачи FastAPI
        session: Сессия базы данных
    """
    handler = TaskRegistry.get_handler(request.task_type)
    if not handler:
        raise ValidationError(f'Unknown task type: {request.task_type}')

    try:
        # Запускаем генерацию в фоновом режиме
        task_id = f'{request.task_type}_{id(request)}'
        background_tasks.add_task(handler.generate, request.params)

        return TaskResponse(task_id=task_id, status='processing')

    except Exception as e:
        return TaskResponse(task_id='error', status='error', error=str(e))


@router.post('/validate/{task_id}', response_model=TaskResponse)
async def validate_task(
    task_id: str, answer: Dict, session: AsyncSession = Depends(get_session)
):
    """
    Проверка ответа на задание.

    Args:
        task_id: Идентификатор задания
        answer: Ответ пользователя
        session: Сессия базы данных
    """
    # Извлекаем тип задания из task_id
    task_type = task_id.split('_')[0]
    handler = TaskRegistry.get_handler(task_type)

    if not handler:
        raise ValidationError(f'Unknown task type: {task_type}')

    try:
        result = await handler.validate(task_id, answer)
        return TaskResponse(
            task_id=task_id, status='completed', result={'is_correct': result}
        )

    except Exception as e:
        return TaskResponse(task_id=task_id, status='error', error=str(e))


@router.get('/status/{task_id}', response_model=TaskResponse)
async def task_status(task_id: str):
    """
    Получение статуса задания.

    Args:
        task_id: Идентификатор задания
    """
    # TODO: Реализовать проверку статуса из хранилища
    return TaskResponse(task_id=task_id, status='processing')
