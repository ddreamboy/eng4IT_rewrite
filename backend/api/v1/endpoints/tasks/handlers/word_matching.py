# backend/api/v1/endpoints/tasks/handlers/word_matching.py

import random
from typing import Any, Dict

from logger import setup_logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import (
    ItemType,
    LearningAttempt,
    TaskType,
    UserWordStatus,
    WordORM,
)

logger = setup_logger(__name__)


class WordMatchingTaskHandler(BaseTaskHandler):
    """Обработчик заданий на сопоставление слов с переводами."""

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания на сопоставление."""
        logger.debug(f'Generating matching task with params: {params}')
        try:
            session: AsyncSession = params.get('session')
            user_id: int = params.get('user_id')

            if not session:
                raise ValidationError('Session is required')
            if not user_id:
                raise ValidationError('User ID is required')

            # Получаем 20 случайных слов
            result = await session.execute(
                select(WordORM).order_by(func.random()).limit(20)
            )
            words = result.scalars().all()

            if len(words) < 20:
                raise ValidationError('Not enough words available')

            # Создаем списки для перемешивания
            original_pairs = [
                {'id': word.id, 'text': word.word, 'translation': word.translation}
                for word in words
            ]

            # Создаем отдельные списки для слов и переводов
            originals = [
                {'id': w['id'], 'text': w['text']} for w in original_pairs
            ]
            translations = [
                {'id': w['id'], 'text': w['translation']} for w in original_pairs
            ]

            # Перемешиваем оба списка
            random.shuffle(originals)
            random.shuffle(translations)

            # Создаем задание
            task = {
                'type': 'matching',
                'content': {
                    'pairs_count': len(words),
                    'originals': originals,
                    'translations': translations,
                },
                'correct_pairs': {
                    str(pair['id']): pair['translation'] for pair in original_pairs
                },
            }

            logger.info('Generated matching task')
            return task

        except Exception as e:
            logger.error(f'Error generating matching task: {e}', exc_info=True)
            raise ValidationError(f'Error generating matching task: {str(e)}')

    async def validate(self, task_id: str, answer: Dict[str, Any]) -> bool:
        """Проверка ответа на задание."""
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_pairs: Dict[str, str] = answer.get('pairs', {})
        correct_pairs: Dict[str, str] = answer.get('correct_pairs', {})

        if not user_pairs or not correct_pairs:
            raise ValidationError('Invalid answer format')

        # Подсчитываем количество правильных ответов
        correct_count = 0
        total_pairs = len(correct_pairs)

        for word_id, translation in user_pairs.items():
            if correct_pairs.get(word_id) == translation:
                correct_count += 1

        # Вычисляем процент правильных ответов
        score = correct_count / total_pairs
        is_successful = (
            score >= 0.7
        )  # Успешно, если 70% или более правильных ответов

        # Создаем записи о попытках для каждого слова
        for word_id, user_translation in user_pairs.items():
            is_correct = correct_pairs.get(word_id) == user_translation

            attempt = LearningAttempt(
                user_id=user_id,
                item_id=int(word_id),
                item_type=ItemType.WORD,
                task_type=TaskType.MATCHING,
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
        return is_successful
