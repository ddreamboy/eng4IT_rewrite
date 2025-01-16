from typing import Any, Dict

from logger import setup_logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.operations import ChatDialog
from backend.api.v1.endpoints.tasks.base import BaseTaskHandler
from backend.core.exceptions import ValidationError
from backend.db.models import (
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

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация задания с диалогом."""
        logger.debug(f'Generating chat dialog task with params: {params}')
        try:
            session: AsyncSession = params.get('session')
            user_id: int = params.get('user_id')
            messages_count: int = params.get('params', {}).get('messages_count', 3)
            specific_terms: list = params.get('params', {}).get('terms', [])
            specific_words: list = params.get('params', {}).get('words', [])
            categories: list = params.get('params', {}).get('categories', [])

            logger.debug(f'Terms: {specific_terms}, words: {specific_words}')

            if not session:
                raise ValidationError('Session is required')
            if not user_id:
                raise ValidationError('User ID is required')

            # Если не указаны конкретные слова/термины, выбираем случайные
            if not specific_terms and not specific_words:
                # Получаем случайные термины
                terms_query = select(TermORM)
                if categories:
                    terms_query = terms_query.where(
                        TermORM.category_main.in_(categories)
                    )
                terms = await session.execute(
                    terms_query.order_by(func.random()).limit(3)
                )
                specific_terms = [term.term for term in terms.scalars()]

                # Получаем случайные слова
                words = await session.execute(
                    select(WordORM).order_by(func.random()).limit(3)
                )
                specific_words = [word.word for word in words.scalars()]

            # Готовим параметры для AI
            ai_params = {
                'messages_count': messages_count,
                'terms': specific_terms,
                'words': specific_words,
                'difficulty': params.get('difficulty', 'intermediate'),
            }

            # Генерируем диалог через AI
            result = await self.operation.execute(ai_params)

            # result = {
            #     'task_id': 'chat_dialog_2214134558912',
            #     'status': 'completed',
            #     'result': {
            #         'type': 'chat_dialog',
            #         'content': {
            #             'context': 'Planning the deployment of a new feature and addressing potential performance issues.',
            #             'translation': 'Планирование развертывания новой функции и решение потенциальных проблем производительности.',
            #             'messages': [
            #                 {
            #                     'author': 'Sarah (Team Lead)',
            #                     'text': "Hey! We're ready to deploy the new user profile feature.  However, we need to ensure we've addressed potential performance bottlenecks.  The initial load testing showed some concerns with the database.",
            #                     'translation': 'Привет! Мы готовы развернуть новую функцию профиля пользователя. Однако, нам нужно убедиться, что мы решили потенциальные узкие места в производительности. Начальное нагрузочное тестирование показало некоторые проблемы с базой данных.',
            #                     'is_user_message': False,
            #                 },
            #                 {
            #                     'author': 'You',
            #                     'text': "Okay, I'll take the {gap1} to implement the necessary {gap2} strategies before we {gap3} the update.  I'll also double-check the efficiency of our current HTTP Request handling.",
            #                     'translation': 'Хорошо, я возьму на себя {gap1} по внедрению необходимых стратегий {gap2} перед тем, как мы {gap3} обновление. Я также повторно проверю эффективность обработки наших текущих HTTP-запросов.',
            #                     'is_user_message': True,
            #                     'gaps': [
            #                         {
            #                             'id': 1,
            #                             'correct': 'initiative',
            #                             'correct_translation': 'инициативу',
            #                             'options': [
            #                                 {
            #                                     'word': 'initiative',
            #                                     'translation': 'инициативу',
            #                                 },
            #                                 {
            #                                     'word': 'to make a decision',
            #                                     'translation': 'принять решение',
            #                                 },
            #                                 {
            #                                     'word': 'execute',
            #                                     'translation': 'выполнить',
            #                                 },
            #                                 {
            #                                     'word': 'Deployment',
            #                                     'translation': 'Развертывание',
            #                                 },
            #                             ],
            #                         },
            #                         {
            #                             'id': 2,
            #                             'correct': 'Feature Scaling',
            #                             'correct_translation': 'масштабирования функций',
            #                             'options': [
            #                                 {
            #                                     'word': 'Feature Scaling',
            #                                     'translation': 'масштабирования функций',
            #                                 },
            #                                 {
            #                                     'word': 'Deployment',
            #                                     'translation': 'Развертывание',
            #                                 },
            #                                 {
            #                                     'word': 'HTTP Request',
            #                                     'translation': 'HTTP-запрос',
            #                                 },
            #                                 {
            #                                     'word': 'to make a decision',
            #                                     'translation': 'принять решение',
            #                                 },
            #                             ],
            #                         },
            #                         {
            #                             'id': 3,
            #                             'correct': 'execute',
            #                             'correct_translation': 'выполним',
            #                             'options': [
            #                                 {
            #                                     'word': 'execute',
            #                                     'translation': 'выполним',
            #                                 },
            #                                 {
            #                                     'word': 'Deployment',
            #                                     'translation': 'Развертывание',
            #                                 },
            #                                 {
            #                                     'word': 'initiative',
            #                                     'translation': 'инициативу',
            #                                 },
            #                                 {
            #                                     'word': 'to make a decision',
            #                                     'translation': 'принять решение',
            #                                 },
            #                             ],
            #                         },
            #                     ],
            #                 },
            #                 {
            #                     'author': 'Sarah (Team Lead)',
            #                     'text': "Sounds good. Let's aim for a deployment by the end of the week. Keep me updated on your progress.",
            #                     'translation': 'Звучит хорошо. Давайте стремиться к развертыванию к концу недели. Держите меня в курсе вашего прогресса.',
            #                     'is_user_message': False,
            #                 },
            #             ],
            #             'metrics': {
            #                 'technical_terms_count': 4,
            #                 'complex_words_count': 3,
            #                 'difficulty_score': 0.6,
            #             },
            #         },
            #         'metadata': {
            #             'used_terms': [
            #                 'Deployment',
            #                 'Feature Scaling',
            #                 'HTTP Request',
            #             ],
            #             'used_words': [
            #                 'initiative',
            #                 'to make a decision',
            #                 'execute',
            #             ],
            #             'difficulty_metrics': {
            #                 'technical_terms_count': 4,
            #                 'complex_words_count': 3,
            #                 'difficulty_score': 0.6,
            #             },
            #         },
            #     },
            #     'error': None,
            # }

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

            logger.info('Generated chat dialog task')
            return task

        except Exception as e:
            logger.error(f'Error generating chat dialog task: {e}', exc_info=True)
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
