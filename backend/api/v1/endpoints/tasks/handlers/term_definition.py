# backend/api/v1/endpoints/tasks/handlers/term_definition.py

import random
from typing import Any, Dict

from logger import setup_logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import (
    DifficultyLevel,
    ItemType,
    LearningAttempt,
    TaskType,
    TermORM,
    UserWordStatus,
)

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
            difficulty: str = params.get('params', {}).get('difficulty')
            incorrect_options: int = params.get('params', {}).get(
                'incorrect_options', 3
            )

            if not session:
                raise ValidationError('Session is required')
            if not user_id:
                raise ValidationError('User ID is required')

            result = await session.execute(
                select(TermORM.category_main).distinct()
            )
            categories = [row[0] for row in result.fetchall()]

            if not category:
                category = random.choice(categories)

            if not difficulty:
                difficulty = random.choice(list(DifficultyLevel)).name.lower()

            if difficulty not in [level.value for level in DifficultyLevel]:
                raise ValidationError('Invalid difficulty level')

            difficulty = difficulty.upper()

            # Получаем случайный термин
            result = await session.execute(
                select(TermORM)
                .where(
                    TermORM.category_main == category,
                    TermORM.difficulty == difficulty,
                )
                .order_by(func.random())
                .limit(1)
            )
            term = result.scalar_one_or_none()

            if not term:
                # Получаем случайный термин
                result = await session.execute(
                    select(TermORM)
                    .where(TermORM.category_main == category)
                    .order_by(func.random())
                    .limit(1)
                )
                term = result.scalar_one_or_none()

                if not term:
                    raise ValidationError('No terms available')

            # Получаем неправильные варианты (другие термины из той же категории)
            wrong_options = await session.execute(
                select(TermORM)
                .where(
                    TermORM.id != term.id,
                    TermORM.category_main == term.category_main,
                    TermORM.difficulty == difficulty,
                )
                .order_by(func.random())
                .limit(incorrect_options)
            )

            # Формируем варианты ответов
            options = [
                {
                    'id': opt.id,
                    'term': opt.term,
                    'translation': opt.primary_translation,
                }
                for opt in wrong_options.scalars()
            ]

            if len(options) != incorrect_options:
                wrong_options = await session.execute(
                    select(TermORM)
                    .where(
                        TermORM.id != term.id,
                        TermORM.category_main == term.category_main,
                    )
                    .order_by(func.random())
                    .limit(incorrect_options)
                )
                options = [
                    {
                        'id': opt.id,
                        'term': opt.term,
                        'translation': opt.primary_translation,
                    }
                    for opt in wrong_options.scalars()
                ]

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
                'term_id': term.id,  # для логгирования и отладки
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
