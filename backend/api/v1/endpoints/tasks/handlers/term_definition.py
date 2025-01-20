# backend/api/v1/endpoints/tasks/handlers/term_definition.py

import random
from typing import Any, Dict

from logger import setup_logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import (
    ItemType,
    LearningAttempt,
    TaskType,
    TermORM,
    UserWordStatus,
)
from backend.db.orm import get_terms_for_learning

logger = setup_logger(__name__)


class TermDefinitionTaskHandler(BaseTaskHandler):
    """Обработчик заданий на сопоставление термина и определения."""

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания на выбор термина по определению."""
        logger.debug(f'Generating term definition task with params: {params}')
        try:
            session: AsyncSession = params.get('session')
            user_id: int = params.get('user_id')
            category: str = params.get('params', {}).get('category')

            if not session:
                raise ValidationError('Session is required')
            if not user_id:
                raise ValidationError('User ID is required')

            # Получаем все термины для задания
            all_terms = await get_terms_for_learning(
                session=session,
                user_id=user_id,
                limit=4,  # Получаем 4 термина (1 правильный + 3 неправильных)
                category=category,
            )

            if not all_terms:
                # Если с указанной категорией не нашли, пробуем без категории
                all_terms = await get_terms_for_learning(
                    session=session, user_id=user_id, limit=4
                )

                if not all_terms:
                    raise ValidationError('No terms available')

            # Берем первый термин как правильный ответ
            term = all_terms[0]

            # Формируем варианты ответов из оставшихся терминов
            options = []

            # Добавляем неправильные варианты
            for wrong_term in all_terms[1:]:
                options.append(
                    {
                        'id': wrong_term.id,
                        'term': wrong_term.term,
                        'translation': wrong_term.primary_translation,
                    }
                )

            # Добавляем правильный вариант
            options.append(
                {
                    'id': term.id,
                    'term': term.term,
                    'translation': term.primary_translation,
                }
            )

            # Перемешиваем варианты
            random.shuffle(options)

            # Создаем задание
            task = {
                'type': 'term_definition',
                'content': {
                    'definition': {
                        'en': term.definition_en,
                        'ru': term.definition_ru,
                    },
                    'options': options,
                    'category': term.category_main,
                    'difficulty': term.difficulty.value,
                },
                'correct_answer': term.id,
                'term_id': term.id,
            }

            logger.info(f'Generated term definition task: {task}')
            return task

        except Exception as e:
            logger.error(
                f'Error generating term definition task: {e}', exc_info=True
            )
            raise ValidationError(
                f'Error generating term definition task: {str(e)}'
            )

    async def validate(self, answer: Dict[str, Any]) -> bool:
        """Проверка ответа на задание."""
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_answer_id: int = answer.get('term_id')

        if not user_answer_id:
            raise ValidationError('Invalid answer format')

        # Получаем термин
        term = await session.get(TermORM, user_answer_id)
        if not term:
            raise ValidationError('Term not found')

        # Проверяем ответ
        is_correct = str(user_answer_id) == str(answer.get('correct_term_id'))

        # Создаем запись о попытке
        attempt = LearningAttempt(
            user_id=user_id,
            item_id=term.id,
            item_type=ItemType.TERM,
            task_type=TaskType.TERM_DEFINITION,  # Нужно добавить этот тип в enum
            is_successful=is_correct,
            score=1.0 if is_correct else 0.0,
        )
        session.add(attempt)

        # Обновляем статистику термина для пользователя
        status = await session.execute(
            select(UserWordStatus).where(
                UserWordStatus.user_id == user_id,
                UserWordStatus.item_id == term.id,
                UserWordStatus.item_type == ItemType.TERM,
            )
        )
        term_status = status.scalar_one_or_none()

        if term_status:
            if is_correct:
                term_status.mastery_level = min(
                    100, term_status.mastery_level + 10
                )
                term_status.ease_factor = min(3.0, term_status.ease_factor + 0.1)
            else:
                term_status.ease_factor = max(1.3, term_status.ease_factor - 0.2)
        else:
            term_status = UserWordStatus(
                user_id=user_id,
                item_id=term.id,
                item_type=ItemType.TERM,
                mastery_level=10.0 if is_correct else 0.0,
                ease_factor=2.5,
            )
            session.add(term_status)

        await session.commit()
        return is_correct
