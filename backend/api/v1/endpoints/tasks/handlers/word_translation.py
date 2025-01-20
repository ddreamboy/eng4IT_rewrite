# backend/api/v1/endpoints/tasks/handlers/word_translation.py

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
    UserWordStatus,
    WordORM,
    WordType,
)
from backend.db.orm import get_words_for_learning

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

            word_type = word_type.upper()

            # Получаем все слова для задания, передавая word_type
            all_words = await get_words_for_learning(
                session=session,
                user_id=user_id,
                limit=incorrect_options + 1,  # +1 для правильного ответа
                word_type=word_type,
            )

            if not all_words:
                # Если не нашли слова указанного типа, пробуем без фильтра по типу
                all_words = await get_words_for_learning(
                    session=session, user_id=user_id, limit=incorrect_options + 1
                )

                if not all_words:
                    raise ValidationError('No words available')

            # Берем первое слово как правильный ответ
            word = all_words[0]

            # Формируем варианты ответов
            options = []

            # Добавляем неправильные варианты
            for wrong_word in all_words[1:]:
                options.append(wrong_word.translation.lower())

            # Если не хватает вариантов ответов, получаем дополнительные слова того же типа
            if len(options) < incorrect_options:
                additional_words = await get_words_for_learning(
                    session=session,
                    user_id=user_id,
                    limit=incorrect_options - len(options),
                    word_type=word_type,
                )
                for add_word in additional_words:
                    if add_word.id != word.id:
                        options.append(add_word.translation.lower())

                # Если всё ещё не хватает, берем любые слова
                if len(options) < incorrect_options:
                    additional_words = await get_words_for_learning(
                        session=session,
                        user_id=user_id,
                        limit=incorrect_options - len(options),
                    )
                    for add_word in additional_words:
                        if add_word.id != word.id:
                            options.append(add_word.translation.lower())

            # Добавляем правильный вариант
            options.append(word.translation.lower())

            # Перемешиваем варианты
            random.shuffle(options)

            # Создаем задание
            task = {
                'type': 'word_translation',
                'content': {
                    'word': word.word,
                    'options': options,
                    'context': word.context,
                    'context_translation': word.context_translation,
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
