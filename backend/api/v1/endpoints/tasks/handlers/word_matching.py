# backend/api/v1/endpoints/tasks/handlers/word_matching.py

from typing import Any, Dict, List

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
                {'id': w['id'], 'text': w['text'].lower()} for w in original_pairs
            ]
            translations = [
                {'id': w['id'], 'text': w['translation'].lower()}
                for w in original_pairs
            ]

            # Перемешиваем оба списка
            # random.shuffle(originals)
            # random.shuffle(translations)

            # Создаем задание
            task = {
                'type': 'matching',
                'content': {
                    'pairs_count': len(words),
                    'originals': originals,
                    'translations': translations,
                },
                'correct_pairs': {
                    str(pair['id']): pair['translation'].lower()
                    for pair in original_pairs
                },
            }

            logger.info('Generated matching task')
            return task

        except Exception as e:
            logger.error(f'Error generating matching task: {e}', exc_info=True)
            raise ValidationError(f'Error generating matching task: {str(e)}')

    async def validate(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка ответа на задание."""
        task_id: str = answer.get('task_id')  # Получаем task_id из answer
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_pairs: Dict[str, str] = answer.get('user_pairs', {})
        correct_pairs: Dict[str, str] = answer.get('correct_pairs', {})
        wrong_attempts: List[Dict[str, Any]] = answer.get('wrong_attempts', [])
        time_spent: int = answer.get('time_spent', 0)
        level: int = answer.get('level', 1)
        lives: int = answer.get('lives', 0)
        current_score: int = answer.get('score', 0)
        total_multiplier: float = answer.get('multiplier', 1.0)
        
        logger.debug(f'Validating matching task with answer: {answer}')

        if not user_pairs or not correct_pairs:
            raise ValidationError('Invalid answer format')

        # Подсчет правильных и неправильных ответов
        correct_count = 0
        total_pairs = len(correct_pairs)
        words_stats = {}

        # Анализ попыток сопоставления
        for word_id, translation in user_pairs.items():
            is_correct = correct_pairs.get(word_id) == translation.lower()

            if is_correct:
                correct_count += 1

            # Статистика по каждому слову
            words_stats[word_id] = {
                'attempts': 1,
                'wrong_attempts': 0,
                'is_correct': is_correct,
            }

        # Анализ неправильных попыток
        for attempt in wrong_attempts:
            word_id = str(attempt['word_id'])
            if word_id in words_stats:
                words_stats[word_id]['attempts'] += 1
                words_stats[word_id]['wrong_attempts'] += 1

        # Расчет точности
        accuracy = correct_count / total_pairs if total_pairs > 0 else 0
        is_successful = accuracy >= 0.5 and lives > 0

        # Базовый счет
        base_score = correct_count * 10  # 10 очков за каждую правильную пару

        # Финальный счет с учетом множителей
        final_score = base_score * total_multiplier

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

        # Возвращаем словарь с требуемыми ключами
        return {
            'is_successful': is_successful,
            'base_score':  round(base_score, 1),
            'final_score':  round(final_score, 1),
            'correct_pairs': correct_count,
            'wrong_pairs': len(wrong_attempts),
            'accuracy': round(accuracy, 1),
            'words_stats': words_stats,
        }
