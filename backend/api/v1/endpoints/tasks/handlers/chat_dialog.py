import json
from typing import Any, Dict, List

from backend.db.orm import get_terms_for_learning, get_words_for_learning
from logger import setup_logger
from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.operations import ChatDialog
from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import (
    ChatDialogGenerated,
    ItemType,
    LearningAttempt,
    TaskType,
    TermORM,
    UserWordStatus,
    WordORM,
)

logger = setup_logger(__name__)


class ChatDialogHandler(BaseTaskHandler):
    """Обработчик заданий с диалогами в чате."""

    def __init__(self):
        super().__init__()
        self.operation = ChatDialog()

    async def _find_existing_task(
        self,
        session: AsyncSession,
        words: List[str],
        terms: List[str],
        difficulty: str,
    ) -> Dict[str, Any] | None:
        """Поиск существующего задания с такими же параметрами."""
        try:
            # Сортируем списки для обеспечения постоянного порядка
            sorted_words = sorted(words) if words else []
            sorted_terms = sorted(terms) if terms else []

            # Выполняем поиск и берем самую свежую запись
            stmt = (
                select(ChatDialogGenerated)
                .where(
                    ChatDialogGenerated.words.cast(String)
                    == json.dumps(sorted_words),
                    ChatDialogGenerated.terms.cast(String)
                    == json.dumps(sorted_terms),
                    ChatDialogGenerated.difficulty == difficulty,
                )
                .order_by(ChatDialogGenerated.created_at.desc())
                .limit(1)
            )

            result = await session.execute(stmt)
            existing_task = result.scalar_one_or_none()

            if existing_task:
                logger.info(
                    f'Found existing chat dialog task with ID: {existing_task.id}'
                )
                return existing_task.response

            return None

        except Exception as e:
            logger.error(
                f'Error finding existing chat dialog task: {e}', exc_info=True
            )
            return None

    async def _save_generated_task(
        self,
        session: AsyncSession,
        words: List[str],
        terms: List[str],
        difficulty: str,
        response: Dict[str, Any],
    ) -> None:
        """Сохранение сгенерированного задания в БД."""
        try:
            # Сортируем списки для сохранения
            sorted_words = sorted(words) if words else []
            sorted_terms = sorted(terms) if terms else []

            # Создаем новую запись
            new_task = ChatDialogGenerated(
                words=sorted_words,
                terms=sorted_terms,
                difficulty=difficulty,
                response=response,
            )

            session.add(new_task)
            # Убираем await session.commit() отсюда, так как коммит будет выполнен в контексте

            logger.info('Created new chat dialog task, waiting for commit')

        except Exception as e:
            logger.error(f'Error saving chat dialog task: {e}', exc_info=True)
            raise

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания с диалогом."""
        logger.debug(f'Generating chat dialog task with params: {params}')
        try:
            session: AsyncSession = params.get('session')
            user_id: int = params.get('user_id')
            messages_count: int = params.get('params', {}).get('messages_count', 3)
            specific_terms: list = params.get('params', {}).get('terms', [])
            specific_words: list = params.get('params', {}).get('words', [])
            difficulty: str = params.get('difficulty', 'intermediate')
            categories: list = params.get('params', {}).get('categories', [])

            if not session:
                raise ValidationError('Session is required')
            if not user_id:
                raise ValidationError('User ID is required')

            # Если не указаны конкретные слова/термины, выбираем на основе критериев
            if not specific_terms and not specific_words:
                words = await get_words_for_learning(
                    session=session,
                    user_id=user_id,
                    limit=3
                )
                terms = await get_terms_for_learning(
                    session=session,
                    user_id=user_id,
                    limit=3
                )
                specific_words = [word.word for word in words]
                specific_terms = [term.term for term in terms]

            # Проверяем есть ли уже сгенерированное задание
            existing_task = await self._find_existing_task(
                session, specific_words, specific_terms, difficulty
            )

            logger.info(f'Existing task: {existing_task}')

            if existing_task:
                logger.info('Using existing chat dialog task')
                return {
                    'type': 'chat_dialog',
                    'content': existing_task.get('content'),
                    'metadata': existing_task.get('metadata'),
                }

            # Если существующего задания нет, генерируем новое
            ai_params = {
                'messages_count': messages_count,
                'terms': specific_terms,
                'words': specific_words,
                'difficulty': difficulty,
            }

            result = await self.operation.execute(ai_params)

            # Создаем задание
            task = {
                'type': 'chat_dialog',
                'content': result,
                'metadata': {
                    'used_terms': specific_terms,
                    'used_words': specific_words,
                    'difficulty_metrics': result.get('metrics', {}),
                },
            }

            # Сохраняем сгенерированное задание
            await self._save_generated_task(
                session, specific_words, specific_terms, difficulty, task
            )

            # Коммитим изменения здесь
            await session.commit()

            logger.info('Generated and saved new chat dialog task')
            return task

        except Exception as e:
            logger.error(f'Error generating chat dialog task: {e}', exc_info=True)
            # В случае ошибки делаем rollback
            await session.rollback()
            raise ValidationError(f'Error generating chat dialog task: {str(e)}')

    async def validate(self, task_id: str, answer: Dict[str, Any]) -> bool:
        """Проверка ответов на задание."""
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_answers: Dict[str, str] = answer.get('answers', {})
        correct_answers: Dict[str, str] = answer.get('correct_answers', {})

        if not user_answers or not correct_answers:
            raise ValidationError('Invalid answer format')

        # Подсчитываем правильные ответы
        correct_count = 0
        total_answers = len(correct_answers)

        for gap_id, user_answer in user_answers.items():
            if correct_answers.get(gap_id) == user_answer:
                correct_count += 1

        # Вычисляем процент правильных ответов
        score = correct_count / total_answers
        is_successful = (
            score >= 0.7
        )  # Успешно, если 70% или более правильных ответов

        # Создаем запись о попытке
        attempt = LearningAttempt(
            user_id=user_id,
            task_type=TaskType.CHAT_DIALOG,
            is_successful=is_successful,
            score=score,
        )
        session.add(attempt)

        # Обновляем статистику для каждого использованного термина/слова
        for word_id in answer.get('used_items', []):
            item_type = answer.get('item_types', {}).get(str(word_id))
            if not item_type:
                continue

            status = await session.execute(
                select(UserWordStatus).where(
                    UserWordStatus.user_id == user_id,
                    UserWordStatus.item_id == word_id,
                    UserWordStatus.item_type == ItemType(item_type),
                )
            )
            word_status = status.scalar_one_or_none()

            if word_status:
                if is_successful:
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
                    item_id=word_id,
                    item_type=ItemType(item_type),
                    mastery_level=5.0 if is_successful else 0.0,
                    ease_factor=2.5,
                )
                session.add(word_status)

        await session.commit()
        return is_successful
