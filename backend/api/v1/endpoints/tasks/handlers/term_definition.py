# backend/api/v1/endpoints/tasks/handlers/term_definition.py

import random
from typing import Any, Dict, List

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

    async def validate(
        self, answer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Расширенная валидация задания на сопоставление слов.

        Args:
            task_id: ID задания
            answer: Словарь с параметрами валидации

        Returns:
            Dict[str, Any]: Результаты валидации
        """
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_pairs: Dict[str, str] = answer.get('pairs', {})
        correct_pairs: Dict[str, str] = answer.get('correct_pairs', {})
        wrong_attempts: List[Dict[str, Any]] = answer.get('wrong_attempts', [])
        time_spent: int = answer.get('time_spent', 0)
        level: int = answer.get('level', 1)
        lives: int = answer.get('lives', 0)
        current_score: int = answer.get('score', 0)
        total_multiplier: float = answer.get('multiplier', 1.0)

        if not user_pairs or not correct_pairs:
            raise ValidationError('Invalid answer format')

        # Подсчет правильных и неправильных попыток
        correct_count = 0
        total_pairs = len(correct_pairs)
        word_stats = {}

        # Анализ попыток сопоставления
        for word_id, translation in user_pairs.items():
            is_correct = correct_pairs.get(word_id) == translation.lower()

            if is_correct:
                correct_count += 1

            # Статистика по каждому слову
            word_stats[word_id] = {
                'attempts': 1,
                'wrong_attempts': 0,
                'is_correct': is_correct,
            }

        # Анализ неправильных попыток
        for attempt in wrong_attempts:
            word_id = str(attempt['word_id'])
            if word_id in word_stats:
                word_stats[word_id]['attempts'] += 1
                word_stats[word_id]['wrong_attempts'] += 1

        # Расчет точности и успешности
        accuracy = correct_count / total_pairs if total_pairs > 0 else 0
        is_successful = accuracy >= 0.5 and lives > 0

        # Базовый счет
        base_score = correct_count * 10  # 10 очков за каждую правильную пару

        # Финальный счет с учетом множителей
        final_score = (
            base_score
            * (1 + (level - 1) * 0.2)  # Множитель уровня
            * (1 - (len(wrong_attempts) * 0.1))  # Штраф за неправильные попытки
        )

        # Создаем записи о попытках для каждого слова
        for word_id, translation in user_pairs.items():
            is_correct = correct_pairs.get(word_id) == translation.lower()

            attempt = LearningAttempt(
                user_id=user_id,
                item_id=int(word_id),
                item_type=ItemType.WORD,
                task_type=TaskType.WORD_MATCHING,
                is_successful=is_correct,
                score=1.0 if is_correct else 0.0,
            )
            session.add(attempt)

            # Обновляем статистику для каждого слова
            status = await session.execute(
                select(UserWordStatus).where(
                    UserWordStatus.user_id == user_id,
                    UserWordStatus.item_id == int(word_id),
                    UserWordStatus.item_type == ItemType.WORD,
                )
            )
            word_status = status.scalar_one_or_none()

            if word_status:
                if is_correct:
                    word_status.mastery_level = min(
                        100, word_status.mastery_level + 5
                    )
                    word_status.ease_factor = min(
                        3.0, word_status.ease_factor + 0.05
                    )
                else:
                    word_status.ease_factor = max(
                        1.3, word_status.ease_factor - 0.1
                    )
            else:
                word_status = UserWordStatus(
                    user_id=user_id,
                    item_id=int(word_id),
                    item_type=ItemType.WORD,
                    mastery_level=5.0 if is_correct else 0.0,
                    ease_factor=2.5,
                )
                session.add(word_status)

        await session.commit()

        return {
            'is_successful': is_successful,
            'base_score': base_score,
            'final_score': final_score,
            'correct_pairs': correct_count,
            'wrong_pairs': len(wrong_attempts),
            'accuracy': accuracy,
            'words_stats': word_stats,
        }
