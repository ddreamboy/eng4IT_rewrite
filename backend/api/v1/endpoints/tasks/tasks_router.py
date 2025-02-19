# backend/api/v1/endpoints/tasks/router.py

from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Query
from logger import setup_logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user_id
from backend.core.exceptions import ValidationError
from backend.db.database import get_session

from .base import TaskRegistry, TaskRequest, TaskResponse

logger = setup_logger(__name__)

router = APIRouter()


class TaskLevel(str, Enum):
    BEGINNER = 'beginner'
    BASIC = 'basic'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'


class TaskInfo(BaseModel):
    """Информация о типе задания"""

    id: str = Field(..., description='Уникальный идентификатор типа задания')
    title: str = Field(..., description='Название задания')
    description: str = Field(..., description='Описание задания')
    difficulty_levels: List[TaskLevel] = Field(
        ..., description='Доступные уровни сложности'
    )
    skills: List[str] = Field(..., description='Развиваемые навыки')
    example: Optional[Dict] = Field(None, description='Пример задания')


# Базовые модели для запросов
class BaseTaskRequest(TaskRequest):
    """Базовый класс для запросов заданий."""

    difficulty: Optional[str] = Query(
        None, description='Task difficulty (basic/intermediate/advanced)'
    )


class ChatDialogRequest(BaseTaskRequest):
    """Модель запроса для чат-диалога."""

    messages_count: Optional[int] = Query(
        3, description='Number of messages in dialog', ge=2, le=10
    )
    terms: Optional[List[str]] = Query(
        None, description='Technical terms to include'
    )
    words: Optional[List[str]] = Query(
        None, description='General words to include'
    )


class WordMatchingRequest(BaseTaskRequest):
    """Модель запроса для сопоставления слов."""

    pairs_count: Optional[int] = Query(
        5, description='Number of word pairs for matching', ge=3, le=20
    )
    category: Optional[str] = Query(None, description='Specific category of terms')


class TermDefinitionRequest(BaseTaskRequest):
    """Модель запроса для определения термина."""

    category: Optional[str] = Query(None, description='Category of terms to use')
    with_context: Optional[bool] = Query(True, description='Include usage context')


class WordTranslationRequest(BaseTaskRequest):
    """Модель запроса для перевода слов."""

    word_type: Optional[str] = Query(
        None, description='Type of words (noun/verb/adjective/etc)'
    )
    with_context: Optional[bool] = Query(True, description='Include usage context')


class EmailStructureRequest(BaseTaskRequest):
    """Модель запроса для задания по структуре email."""

    style: Optional[str] = Query(
        None, description='Email style (formal/semi-formal/informal)'
    )
    topic: Optional[str] = Query(
        None, description='Email topic (meeting/report/request/update)'
    )
    terms: Optional[List[str]] = Query(
        None, description='Technical terms to include'
    )
    words: Optional[List[str]] = Query(
        None, description='Business words to include'
    )


# Роутеры для каждого типа задания
@router.post(
    '/generate/chat-dialog',
    response_model=TaskResponse,
    summary='Generate chat dialog task',
    description="""
    Generates a task with IT-focused chat dialog.
    
    Features:
    - Natural conversation between two people
    - Gap-fill exercises in user responses
    - Technical terms and common words usage
    - Translations for all content
    
    Example request:
    ```json
    {
      "task_type": "chat_dialog",
      "user_id": 1,
      "params": {
        "messages_count": 3,
        "terms": ["API", "deployment"],
        "words": ["implement", "schedule"],
        "difficulty": "intermediate"
      }
    }
    ```
    """,
    tags=['tasks'],
)
async def generate_chat_dialog(
    request: ChatDialogRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Генерация задания с диалогом."""
    return await _generate_task('chat_dialog', request, current_user_id, session)


@router.post(
    '/generate/chat-dialog/validate',
    response_model=Dict[str, Any],
    summary='Validate chat dialog answer',
    description='Validates user answers for chat dialog task and returns detailed statistics',
    tags=['tasks'],
)
async def validate_chat_dialog(
    task_id: str = Body(..., description='ID of the task'),
    user_answers: Dict[str, str] = Body(..., description='User answers for gaps'),
    correct_answers: Dict[str, str] = Body(
        ..., description='Correct answers for gaps'
    ),
    used_items: List[int] = Body(..., description='List of used word/term IDs'),
    item_types: Dict[str, str] = Body(
        ..., description='Types of used items (word/term)'
    ),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Валидация ответов для задания с чат-диалогом.

    Args:
        task_id: ID задания
        user_answers: Ответы пользователя для пропусков
        correct_answers: Правильные ответы для пропусков
        used_items: Список использованных слов/терминов
        item_types: Типы использованных элементов (word/term)
        current_user_id: ID текущего пользователя
        session: Сессия базы данных
    """
    handler = TaskRegistry.get_handler('chat_dialog')

    if not handler:
        raise ValidationError('Chat dialog task handler not found')

    try:
        result = await handler.validate(
            {
                'session': session,
                'user_id': current_user_id,
                'user_answers': user_answers,
                'correct_answers': correct_answers,
                'used_items': used_items,
                'item_types': item_types,
                'task_id': task_id,
            }
        )

        return {
            'is_successful': result,
            'statistics': {
                'correct_answers': len(
                    [
                        k
                        for k, v in user_answers.items()
                        if v == correct_answers.get(k)
                    ]
                ),
                'total_answers': len(correct_answers),
            },
        }

    except Exception as e:
        raise ValidationError(f'Error validating answer: {str(e)}')


@router.post(
    '/generate/word-matching',
    response_model=TaskResponse,
    summary='Generate word matching task',
    description="""
    Generates a word matching exercise.
    
    Features:
    - Pairs of related terms/translations
    - Category-based grouping
    - Difficulty-based selection
    
    Example request:
    ```json
    {
      "task_type": "word_matching",
      "user_id": 1,
      "params": {
        "pairs_count": 5,
        "category": "databases",
        "difficulty": "intermediate"
      }
    }
    ```
    """,
    tags=['tasks'],
)
async def generate_word_matching(
    request: WordMatchingRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Генерация задания на сопоставление."""
    return await _generate_task('word_matching', request, current_user_id, session)


@router.post(
    '/generate/word-matching/validate',
    response_model=Dict[str, Any],
    summary='Validate word matching answer',
    description='Validates pairs of matched words and returns detailed statistics',
    tags=['tasks'],
)
async def validate_word_matching(
    task_id: str = Body(..., description='ID of the task'),
    pairs: Dict[str, str] = Body(..., description='Matched word pairs'),
    correct_pairs: Dict[str, str] = Body(..., description='Matched word pairs'),
    wrong_attempts: List = Body(..., description='Wrong match attempts'),
    time_spent: int = Body(..., description='Time spent in seconds'),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Валидация ответов для задания на сопоставление слов.

    Args:
        task_id: ID задания
        pairs: Сопоставленные пары слов
        wrong_attempts: Список неправильных попыток сопоставления
        time_spent: Затраченное время в секундах
        current_user_id: ID текущего пользователя
        session: Сессия базы данных
    """
    logger.info(
        f'Received validation request: task_id={task_id}, pairs={pairs}, correct_pairs={correct_pairs}'
    )

    handler = TaskRegistry.get_handler('word_matching')

    if not handler:
        raise ValidationError('Word matching task handler not found')

    try:
        result = await handler.validate(
            {
                'session': session,
                'user_id': current_user_id,
                'user_pairs': pairs,
                'correct_pairs': correct_pairs,
                'wrong_attempts': wrong_attempts,
                'time_spent': time_spent,
                'task_id': task_id,
            }
        )

        return {
            'statistics': {
                'correct_pairs': result['correct_pairs'],
                'wrong_pairs': result['wrong_pairs'],
                'accuracy': result['accuracy'],
                'time_spent': time_spent,
                'words_stats': result['words_stats'],
            },
        }

    except Exception as e:
        logger.error(f'Error validating answer: {str(e)}', exc_info=True)
        raise ValidationError(f'Error validating answer: {str(e)}')


@router.post(
    '/generate/term-definition',
    response_model=TaskResponse,
    summary='Generate term definition task',
    description="""
    Generates a technical term definition exercise.
    
    Features:
    - Term and definition matching
    - Category-specific terms
    - Optional usage context
    
    Example request:
    ```json
    {
      "task_type": "term_definition",
      "user_id": 1,
      "params": {
        "category": "backend",
        "with_context": true,
        "difficulty": "intermediate"
      }
    }
    ```
    """,
    tags=['tasks'],
)
async def generate_term_definition(
    request: TermDefinitionRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Генерация задания на определение термина."""
    return await _generate_task(
        'term_definition', request, current_user_id, session
    )


@router.post(
    '/generate/term-definition/validate',
    response_model=Dict[str, bool],
    summary='Validate term definition answer',
    description='Проверяет правильность выбранного ответа для задания на определение термина',
    tags=['tasks'],
)
async def validate_term_definition(
    task_id: str = Body(..., description='ID задания'),
    term_id: int = Body(..., description='ID выбранного термина'),
    correct_term_id: int = Body(..., description='ID правильного термина'),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Валидация ответа на задание по определению термина."""
    handler = TaskRegistry.get_handler('term_definition')

    if not handler:
        raise ValidationError('Term definition task handler not found')

    try:
        is_correct = await handler.validate(
            {
                'session': session,
                'user_id': current_user_id,
                'term_id': term_id,
                'correct_term_id': correct_term_id,
                'task_id': task_id,
            }
        )

        return {'is_correct': is_correct}

    except Exception as e:
        raise ValidationError(f'Error validating answer: {str(e)}')


@router.post(
    '/generate/word-translation',
    response_model=TaskResponse,
    summary='Generate word translation task',
    description="""
    Generates a word translation exercise.
    
    Features:
    - Word type filtering
    - Context sentences
    - Multiple choice options
    
    Example request:
    ```json
    {
      "task_type": "word_translation",
      "user_id": 1,
      "params": {
        "word_type": "verb",
        "with_context": true,
        "difficulty": "basic"
      }
    }
    ```
    """,
    tags=['tasks'],
)
async def generate_word_translation(
    request: WordTranslationRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Генерация задания на перевод."""
    return await _generate_task(
        'word_translation', request, current_user_id, session
    )


@router.post(
    '/generate/word-translation/validate',
    response_model=Dict[str, Any],
    summary='Validate word translation answer',
    description='Validates selected translation and returns result',
    tags=['tasks'],
)
async def validate_word_translation(
    task_id: str = Body(..., description='ID of the task'),
    answer: str = Body(..., description='Selected translation'),
    word_id: int = Body(..., description='ID of the word'),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Валидация ответа для задания на перевод слова.
    """
    handler = TaskRegistry.get_handler('word_translation')

    if not handler:
        raise ValidationError('Word translation task handler not found')

    try:
        result = await handler.validate(
            {
                'session': session,
                'user_id': current_user_id,
                'answer': answer,
                'word_id': word_id,
                'task_id': task_id,
            }
        )

        return {'is_correct': result}

    except Exception as e:
        raise ValidationError(f'Error validating answer: {str(e)}')


@router.post(
    '/generate/email-structure',
    response_model=TaskResponse,
    summary='Generate email structure task',
    description="""
    Generates an email structure learning task.
    
    Features:
    - Email block ordering
    - Style variations
    - Technical vocabulary integration
    
    Example request:
    ```json
    {
      "task_type": "email_structure",
      "user_id": 1,
      "params": {
        "style": "formal",
        "topic": "meeting",
        "terms": ["API integration"],
        "difficulty": "intermediate"
      }
    }
    ```
    """,
    tags=['tasks'],
)
async def generate_email_structure(
    request: EmailStructureRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Генерация задания по структуре email."""
    logger.info(f'Received email structure request: {request}')
    logger.info(f'Current user ID: {current_user_id}')

    try:
        result = await _generate_task(
            'email_structure', request, current_user_id, session
        )
        logger.info(f'Generated result: {result}')
        return result
    except Exception as e:
        logger.error(f'Error in generate_email_structure: {str(e)}', exc_info=True)
        raise


@router.post(
    '/generate/email-structure/validate',
    response_model=Dict[str, Any],
    summary='Validate email structure answer',
    description='Validates the order and content of email blocks and returns detailed statistics',
    tags=['tasks'],
)
async def validate_email_structure(
    task_id: str = Body(..., description='ID of the task'),
    user_blocks: List[Dict] = Body(..., description='User arranged blocks'),
    correct_blocks: List[Dict] = Body(..., description='Correct blocks order'),
    words: List[str] = Body(default=[], description='Used words'),
    terms: List[str] = Body(default=[], description='Used terms'),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Валидация ответа для задания по структуре email.

    Args:
        task_id: ID задания
        user_blocks: Расставленные пользователем блоки
        correct_blocks: Правильный порядок блоков
        used_items: Список использованных слов/терминов
        item_types: Типы использованных элементов (word/term)
        current_user_id: ID текущего пользователя
        session: Сессия базы данных
    """
    handler = TaskRegistry.get_handler('email_structure')

    if not handler:
        raise ValidationError('Email structure task handler not found')

    try:
        is_correct = await handler.validate(
            {
                'session': session,
                'user_id': current_user_id,
                'blocks': user_blocks,
                'correct_blocks': correct_blocks,
                'terms': terms,
                'words': words,
                'task_id': task_id,
            }
        )

        return {
            'is_successful': is_correct,
            'statistics': {
                'correct_blocks': len(
                    [
                        i
                        for i, (user, correct) in enumerate(
                            zip(user_blocks, correct_blocks)
                        )
                        if user['type'] == correct['type']
                    ]
                ),
                'total_blocks': len(correct_blocks),
            },
        }

    except Exception as e:
        logger.error(f'Error validating answer: {str(e)}', exc_info=True)
        raise ValidationError(f'Error validating answer: {str(e)}')


# Вспомогательная функция для генерации заданий
async def _generate_task(
    task_type: str,
    request: BaseTaskRequest,
    current_user_id: int,
    session: AsyncSession,
) -> TaskResponse:
    """Общая функция генерации заданий."""
    handler = TaskRegistry.get_handler(task_type)

    if not handler:
        raise ValidationError(f'{task_type} task handler not found')

    try:
        params = {
            **request.model_dump(exclude_none=True),
            'session': session,
        }

        result = await handler.generate(params)

        return TaskResponse(
            task_id=f'{task_type}_{id(request)}', status='completed', result=result
        )

    except Exception as e:
        return TaskResponse(task_id='error', status='error', error=str(e))


@router.get(
    '/info',
    response_model=List[TaskInfo],
    summary='Get available tasks info',
    description='Получение информации о всех доступных типах заданий',
    tags=['tasks'],
)
async def get_tasks_info():
    """
    Возвращает информацию о всех доступных типах заданий.
    Включает описание, уровни сложности, примерное время выполнения и развиваемые навыки.
    """
    return [
        {
            'id': 'chat_dialog',
            'title': 'Chat Dialog',
            'description': 'Practice IT communication through realistic chat conversations. Fill in gaps with appropriate technical terms and common expressions.',
            'difficulty_levels': [
                TaskLevel.BASIC,
                TaskLevel.INTERMEDIATE,
                TaskLevel.ADVANCED,
            ],
            'skills': [
                'Technical Communication',
                'Context Understanding',
                'Professional Vocabulary',
            ],
            'example': {
                'context': 'Discussing API integration project',
                'messages': [
                    {
                        'author': 'Team Lead',
                        'text': 'We need to update the API documentation. Can you help?',
                    },
                    {
                        'author': 'You',
                        'text': "Sure! I'll [implement] the changes in the [continuous integration] pipeline.",
                    },
                ],
            },
        },
        {
            'id': 'word_matching',
            'title': 'Word Matching',
            'description': 'Match technical terms with their translations or definitions. Improve your tech vocabulary through association.',
            'difficulty_levels': [
                TaskLevel.BEGINNER,
                TaskLevel.BASIC,
                TaskLevel.INTERMEDIATE,
            ],
            'skills': [
                'Technical Vocabulary',
                'Term Recognition',
                'Memory Development',
            ],
            'example': {
                'terms': ['API', 'Database', 'Framework'],
                'definitions': [
                    'Application Programming Interface',
                    'Organized collection of data',
                    'Software development platform',
                ],
            },
        },
        {
            'id': 'term_definition',
            'title': 'Term Definition',
            'description': 'Learn technical terms through their definitions. Choose the correct term that matches the given technical description.',
            'difficulty_levels': [
                TaskLevel.BASIC,
                TaskLevel.INTERMEDIATE,
                TaskLevel.ADVANCED,
            ],
            'skills': [
                'Technical Reading',
                'Term Understanding',
                'Professional Terminology',
            ],
        },
        {
            'id': 'word_translation',
            'title': 'Word Translation',
            'description': 'Practice translating technical and professional vocabulary between English and Russian.',
            'difficulty_levels': [
                TaskLevel.BEGINNER,
                TaskLevel.BASIC,
                TaskLevel.INTERMEDIATE,
            ],
            'skills': [
                'Vocabulary Translation',
                'Technical Terms',
                'Language Switching',
            ],
        },
        {
            'id': 'email_structure',
            'title': 'Email Structure',
            'description': 'Learn to write professional emails in English. Practice organizing email components and using appropriate business language.',
            'difficulty_levels': [
                TaskLevel.BASIC,
                TaskLevel.INTERMEDIATE,
                TaskLevel.ADVANCED,
            ],
            'skills': [
                'Business Writing',
                'Email Etiquette',
                'Professional Communication',
            ],
            'example': {
                'style': 'formal',
                'topic': 'meeting',
                'blocks': [
                    'Subject: Project Update Meeting Request',
                    'Dear Team,',
                    'I am writing to schedule...',
                    'Best regards,',
                ],
            },
        },
    ]
