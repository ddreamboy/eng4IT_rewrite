# backend/api/v1/endpoints/tasks/handlers/email_structure.py

import random
from typing import Any, Dict, List

from logger import setup_logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.operations import EmailStructure  # Нужно будет создать
from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import (
    DifficultyLevel,
    ItemType,
    LearningAttempt,
    TaskType,
    TermORM,
    UserORM,
    UserWordStatus,
    WordORM,
)

logger = setup_logger(__name__)


class EmailStructureHandler(BaseTaskHandler):
    """Обработчик заданий на составление структуры email."""

    STYLES = ['formal', 'semi-formal', 'informal']
    TOPICS = ['meeting', 'report', 'request', 'update']

    DIFFICULTY_MAPPING = {
        DifficultyLevel.BEGINNER: 'basic',
        DifficultyLevel.BASIC: 'basic',
        DifficultyLevel.INTERMEDIATE: 'intermediate',
        DifficultyLevel.ADVANCED: 'advanced',
    }

    def __init__(self):
        super().__init__()
        self.operation = EmailStructure()

    async def _get_random_terms(
        self, session: AsyncSession, count: int = 3
    ) -> List[str]:
        """Получение случайных технических терминов."""
        terms = await session.execute(
            select(TermORM.term).order_by(func.random()).limit(count)
        )
        return [term for term in terms.scalars()]

    async def _get_random_words(
        self, session: AsyncSession, count: int = 3
    ) -> List[str]:
        """Получение случайных бизнес-слов."""
        words = await session.execute(
            select(WordORM.word).order_by(func.random()).limit(count)
        )
        return [word for word in words.scalars()]

    async def _get_user_difficulty(
        self, session: AsyncSession, user_id: int
    ) -> str:
        """Определение сложности на основе уровня пользователя."""
        user = await session.get(UserORM, user_id)
        if not user:
            return 'intermediate'  # дефолтное значение

        # Учитываем proficiency_score и current_level
        if user.proficiency_score < 40:
            return 'basic'
        elif user.proficiency_score > 75:
            return 'advanced'

        # Если score в среднем диапазоне, используем current_level
        return self.DIFFICULTY_MAPPING.get(user.current_level, 'intermediate')

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания на составление email."""
        logger.debug(f'Generating email structure task with params: {params}')
        try:
            session: AsyncSession = params.get('session')
            user_id: int = params.get('user_id')

            if not session:
                raise ValidationError('Session is required')
            if not user_id:
                raise ValidationError('User ID is required')

            # Получаем или генерируем параметры
            style = params.get('style', random.choice(self.STYLES))
            topic = params.get('topic', random.choice(self.TOPICS))

            # Определяем сложность на основе уровня пользователя если не указана
            difficulty = params.get(
                'difficulty'
            ) or await self._get_user_difficulty(session, user_id)

            # Получаем термины и слова
            terms = params.get('params', {}).get(
                'terms'
            ) or await self._get_random_terms(session, count=2)
            words = params.get('params', {}).get(
                'words'
            ) or await self._get_random_words(session, count=3)

            # Готовим параметры для AI
            ai_params = {
                'style': style,
                'difficulty': difficulty,
                'topic': topic,
                'terms': terms,
                'words': words,
            }

            # Генерируем задание через AI
            result = await self.operation.execute(ai_params)

            # Создаем задание
            task = {
                'type': 'email_structure',
                'content': result,
                'metadata': {
                    'style': style,
                    'topic': topic,
                    'used_terms': terms,
                    'used_words': words,
                    'difficulty_metrics': result.get('metrics', {}),
                },
            }

            logger.info('Generated email structure task')
            return task

        except Exception as e:
            logger.error(
                f'Error generating email structure task: {e}', exc_info=True
            )
            raise ValidationError(
                f'Error generating email structure task: {str(e)}'
            )

    async def validate(self, answer: Dict[str, Any]) -> bool:
        """Проверка ответа на задание."""
        logger.debug(f'Validating email structure answer: {answer}')
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_blocks: List[Dict] = answer.get('blocks', [])
        correct_blocks: List[Dict] = answer.get('correct_blocks', [])
        words: List[str] = answer.get('words', [])  # теперь это список строк
        terms: List[str] = answer.get('terms', [])  # теперь это список строк

        if not user_blocks or not correct_blocks:
            raise ValidationError('Invalid answer format')

        # Проверяем порядок и правильность блоков
        is_order_correct = True
        correct_blocks_count = 0
        total_blocks = len(correct_blocks)

        for i, (user_block, correct_block) in enumerate(
            zip(user_blocks, correct_blocks)
        ):
            if user_block['type'] != correct_block['type']:
                is_order_correct = False
            else:
                correct_blocks_count += 1

        # Вычисляем общий результат
        score = correct_blocks_count / total_blocks
        is_successful = score >= 0.7 and is_order_correct

        # Получаем первое слово или термин из БД для записи попытки
        first_word_or_term = None
        first_type = None

        if words:
            first_word = await session.execute(
                select(WordORM).filter(WordORM.word == words[0]).limit(1)
            )
            first_word = first_word.scalar_one_or_none()
            if first_word:
                first_word_or_term = first_word.id
                first_type = ItemType.WORD

        if not first_word_or_term and terms:
            first_term = await session.execute(
                select(TermORM).filter(TermORM.term == terms[0]).limit(1)
            )
            first_term = first_term.scalar_one_or_none()
            if first_term:
                first_word_or_term = first_term.id
                first_type = ItemType.TERM

        # Создаем запись попытки
        attempt = LearningAttempt(
            user_id=user_id,
            task_type=TaskType.EMAIL_STRUCTURE,
            is_successful=is_successful,
            score=score,
            item_id=first_word_or_term
            or 0,  # дефолтное значение если ничего не нашли
            item_type=first_type
            or ItemType.WORD,  # дефолтное значение если ничего не нашли
        )
        session.add(attempt)

        # Обновляем статистику для слов
        if words:
            word_records = await session.execute(
                select(WordORM).filter(WordORM.word.in_(words))
            )
            word_records = word_records.scalars().all()

            for word_record in word_records:
                status = await session.execute(
                    select(UserWordStatus).where(
                        UserWordStatus.user_id == user_id,
                        UserWordStatus.item_id == word_record.id,
                        UserWordStatus.item_type == ItemType.WORD,
                    )
                )
                word_status = status.scalar_one_or_none()
                await self._update_word_status(
                    session,
                    word_status,
                    word_record.id,
                    user_id,
                    is_successful,
                    ItemType.WORD,
                )

        # Обновляем статистику для терминов
        if terms:
            term_records = await session.execute(
                select(TermORM).filter(TermORM.term.in_(terms))
            )
            term_records = term_records.scalars().all()

            for term_record in term_records:
                status = await session.execute(
                    select(UserWordStatus).where(
                        UserWordStatus.user_id == user_id,
                        UserWordStatus.item_id == term_record.id,
                        UserWordStatus.item_type == ItemType.TERM,
                    )
                )
                term_status = status.scalar_one_or_none()
                await self._update_word_status(
                    session,
                    term_status,
                    term_record.id,
                    user_id,
                    is_successful,
                    ItemType.TERM,
                )

        await session.commit()
        return is_successful

    async def _update_word_status(
        self, session, status, item_id, user_id, is_successful, item_type
    ):
        """Вспомогательная функция для обновления статуса слова/термина"""
        if status:
            if is_successful:
                status.mastery_level = min(100, status.mastery_level + 5)
                status.ease_factor = min(3.0, status.ease_factor + 0.05)
            else:
                status.ease_factor = max(1.3, status.ease_factor - 0.1)
        else:
            new_status = UserWordStatus(
                user_id=user_id,
                item_id=item_id,
                item_type=item_type,
                mastery_level=5.0 if is_successful else 0.0,
                ease_factor=2.5,
            )
            session.add(new_status)
