# backend/api/v1/endpoints/tasks/handlers/word_translation.py

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
    UserWordStatus,
    WordORM,
    WordType,
)

logger = setup_logger(__name__)


class WordTranslationTaskHandler(BaseTaskHandler):
    """Обработчик заданий на перевод."""

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания на перевод."""
        logger.debug(f'Generating translation task with params: {params}')
        try:
            session: AsyncSession = params.get('session')
            user_id: int = params.get('user_id')
            word_type: str = params.get('params', {}).get('word_type')
            difficulty: str = params.get('params', {}).get('difficulty')
            incorrect_options: int = params.get('params', {}).get(
                'incorrect_options', 3
            )

            if not session:
                raise ValidationError('Session is required')

            if not user_id:
                raise ValidationError('User ID is required')

            if not word_type:
                word_type = random.choice(list(WordType)).name

            if word_type.upper() not in [wordType.value for wordType in WordType]:
                raise ValidationError('Word type is invalid')

            if not difficulty:
                difficulty = random.choice(list(DifficultyLevel)).name.lower()

            if difficulty not in [level.value for level in DifficultyLevel]:
                raise ValidationError('Invalid difficulty level')

            word_type = word_type.upper()
            difficulty = difficulty.upper()

            # Получаем случайное слово
            result = await session.execute(
                select(WordORM)
                .where(
                    WordORM.word_type == word_type,
                    WordORM.difficulty == difficulty,
                )
                .order_by(func.random())
                .limit(1)
            )
            word = result.scalar_one_or_none()

            if not word:
                # Пробуем получить слово любой сложности для данного типа
                result = await session.execute(
                    select(WordORM)
                    .where(WordORM.word_type == word_type)
                    .order_by(func.random())
                    .limit(1)
                )
                word = result.scalar_one_or_none()

                if not word:
                    # Пробуем получить любое слово
                    result = await session.execute(
                        select(WordORM).order_by(func.random()).limit(1)
                    )
                    word = result.scalar_one_or_none()

                    if not word:
                        raise ValidationError('No words available')

            # Получаем неправильные варианты (другие переводы)
            wrong_options = await session.execute(
                select(WordORM.translation)
                .where(
                    WordORM.id != word.id,
                    WordORM.word_type == word_type,
                    WordORM.difficulty == difficulty,
                )
                .order_by(func.random())
                .limit(incorrect_options)
            )

            options = [opt[0] for opt in wrong_options.fetchall()]
            if len(options) != incorrect_options:
                wrong_options = await session.execute(
                    select(WordORM.translation)
                    .where(
                        WordORM.id != word.id,
                        WordORM.word_type == word_type,
                    )
                    .order_by(func.random())
                    .limit(incorrect_options)
                )

                if len(options) != incorrect_options:
                    wrong_options = await session.execute(
                        select(WordORM.translation)
                        .where(
                            WordORM.id != word.id,
                        )
                        .order_by(func.random())
                        .limit(incorrect_options)
                    )
                    options = [opt[0].lower() for opt in wrong_options.fetchall()]

            options.append(word.translation.lower())

            # Перемешиваем варианты
            random.shuffle(options)

            # Создаем задание
            task = {
                'type': 'word_translation',
                'content': {
                    'word': word.word,
                    'options': options,
                    'context': word.context,  # Добавляем контекст
                    'context_translation': word.context_translation,  # И его перевод
                    'word_type': word.word_type,
                    'difficulty': word.difficulty,
                },
                'correct_answer': word.translation,
                'word_id': word.id,
            }

            logger.info(f'Generated translation task: {task}')
            return task
        except Exception as e:
            logger.error(f'Error generating translation task: {e}', exc_info=True)
            raise ValidationError(f'Error generating translation task: {str(e)}')

    async def validate(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Расширенная валидация задания на перевод слова.

        Args:
            answer: Словарь с параметрами валидации

        Returns:
            Dict[str, Any]: Результаты валидации
        """
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_answer: str = answer.get('answer')
        word_id: int = answer.get('word_id')
        
        logger.debug(f'Word ID: {word_id}')

        # Получаем слово
        if word_id:
            word = await session.get(WordORM, word_id)
            if not word:
                raise ValidationError('Word not found')

        # Проверяем ответ
        is_correct = user_answer.lower() == word.translation.lower()

        # Создаем запись о попытке
        attempt = LearningAttempt(
            user_id=user_id,
            item_id=word.id,
            item_type=ItemType.WORD,
            task_type=TaskType.WORD_TRANSLATION,
            is_successful=is_correct,
            score=1.0 if is_correct else 0.0,
        )
        session.add(attempt)

        # Обновляем статистику слова для пользователя
        status = await session.execute(
            select(UserWordStatus).where(
                UserWordStatus.user_id == user_id,
                UserWordStatus.item_id == word.id,
                UserWordStatus.item_type == ItemType.WORD,
            )
        )
        word_status = status.scalar_one_or_none()

        if word_status:
            # Обновляем существующий статус
            if is_correct:
                word_status.mastery_level = min(
                    100, word_status.mastery_level + 10
                )
                word_status.ease_factor = min(3.0, word_status.ease_factor + 0.1)
            else:
                word_status.ease_factor = max(1.3, word_status.ease_factor - 0.2)
        else:
            # Создаем новый статус
            word_status = UserWordStatus(
                user_id=user_id,
                item_id=word.id,
                item_type=ItemType.WORD,
                mastery_level=10.0 if is_correct else 0.0,
                ease_factor=2.5,
            )
            session.add(word_status)

        await session.commit()

        return {'is_correct': is_correct}
