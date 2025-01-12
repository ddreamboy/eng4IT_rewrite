from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import LearningAttempt, TaskType, TermORM, UserWordStatus


class TranslationTaskHandler(BaseTaskHandler):
    """Обработчик заданий на перевод."""

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания на перевод."""
        session: AsyncSession = params['session']
        user_id: int = params['user_id']

        # Получаем случайный термин
        result = await session.execute(
            select(TermORM).order_by(func.random()).limit(1)
        )
        term = result.scalar_one_or_none()

        if not term:
            raise ValidationError('No terms available')

        # Получаем неправильные варианты (другие переводы)
        wrong_options = await session.execute(
            select(TermORM.primary_translation)
            .where(TermORM.id != term.id)
            .order_by(func.random())
            .limit(3)
        )

        options = [opt[0] for opt in wrong_options.fetchall()]
        options.append(term.primary_translation)

        # Перемешиваем варианты
        import random

        random.shuffle(options)

        # Создаем задание
        task = {
            'task_id': f'translation_{term.id}',
            'type': 'translation',
            'content': {'term': term.term, 'options': options},
            'correct_answer': term.primary_translation,
            'term_id': term.id,
        }

        return task

    async def validate(self, task_id: str, answer: Dict[str, Any]) -> bool:
        """Проверка ответа на задание."""
        session: AsyncSession = answer['session']
        user_id: int = answer['user_id']
        user_answer: str = answer['answer']

        # Получаем term_id из task_id
        term_id = int(task_id.split('_')[1])

        # Получаем термин
        term = await session.get(TermORM, term_id)
        if not term:
            raise ValidationError('Term not found')

        # Проверяем ответ
        is_correct = user_answer == term.primary_translation

        # Создаем запись о попытке
        attempt = LearningAttempt(
            user_id=user_id,
            item_id=term.id,
            item_type='term',
            task_type=TaskType.TRANSLATION,
            is_successful=is_correct,
            score=1.0 if is_correct else 0.0,
        )
        session.add(attempt)

        # Обновляем статистику слова для пользователя
        status = await session.execute(
            select(UserWordStatus).where(
                UserWordStatus.user_id == user_id,
                UserWordStatus.item_id == term.id,
                UserWordStatus.item_type == 'term',
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
                item_id=term.id,
                item_type='term',
                mastery_level=10.0 if is_correct else 0.0,
                ease_factor=2.5,
            )
            session.add(word_status)

        await session.commit()
        return is_correct
