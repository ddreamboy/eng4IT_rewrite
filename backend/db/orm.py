import random
from datetime import datetime
from typing import List, Optional

from logger import setup_logger
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import async_engine, get_session

from .models import (
    Base,
    DifficultyLevel,
    ItemType,
    TermORM,
    UserWordStatus,
    WordORM,
    WordType,
)

logger = setup_logger(__name__)


async def get_term_by_name(session: AsyncSession, term: str) -> Optional[TermORM]:
    """Получает термин по его названию."""
    result = await session.execute(select(TermORM).where(TermORM.term == term))
    return result.scalar_one_or_none()


async def get_word_by_name(session: AsyncSession, word: str) -> Optional[WordORM]:
    """Получает слово по его названию."""
    result = await session.execute(select(WordORM).where(WordORM.word == word))
    return result.scalar_one_or_none()


async def create_term(session: AsyncSession, term_data: dict) -> Optional[TermORM]:
    """Создает новую запись термина в БД."""
    try:
        existing_term = await get_term_by_name(session, term_data['term'])
        if existing_term:
            return None

        term = TermORM(
            term=term_data['term'],
            primary_translation=term_data['translations']['primary'],
            category_main=term_data['category']['main'],
            category_sub=term_data['category'].get('sub'),
            difficulty=DifficultyLevel[term_data['difficulty'].upper()],
            definition_en=term_data['context']['definition']['en'],
            definition_ru=term_data['context']['definition']['ru'],
            example_en=term_data['context'].get('example', {}).get('en'),
            example_context=term_data['context'].get('example', {}).get('context'),
            related_terms=term_data.get('related_terms', []),
            alternate_translations=term_data['translations'].get('alternates', []),
        )

        session.add(term)
        await session.flush()
        return term

    except Exception:
        await session.rollback()
        raise


async def create_word(session: AsyncSession, word_data: dict) -> Optional[WordORM]:
    """Создает новую запись слова в БД."""
    try:
        existing_word = await get_word_by_name(session, word_data['word'])
        if existing_word:
            return None

        # Преобразуем тип слова в формат enum
        word_type_map = {
            'noun': 'NOUN',
            'verb': 'VERB',
            'adjective': 'ADJECTIVE',
            'adverb': 'ADVERB',
            'phrasal verb': 'PHRASAL_VERB',
            'common phrase': 'COMMON_PHRASE',
        }

        word_type = word_type_map.get(word_data['word_type'].lower())
        if not word_type:
            raise ValueError(f'Неизвестный тип слова: {word_data["word_type"]}')

        word = WordORM(
            word=word_data['word'],
            translation=word_data['translation'],
            context=word_data.get('context'),
            context_translation=word_data.get('context_translation'),
            word_type=WordType[word_type],
            difficulty=DifficultyLevel[word_data['difficulty'].upper()],
        )

        session.add(word)
        await session.flush()
        return word

    except Exception:
        await session.rollback()
        raise


async def init_db_tables() -> None:
    """Инициализирует таблицы в базе данных."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_random_terms(session: AsyncSession, limit: int = 3) -> list[TermORM]:
    """Получает случайные термины из базы данных."""
    result = await session.execute(
        select(TermORM).order_by(func.random()).limit(limit)
    )
    return result.scalars().all()


async def get_random_words(session: AsyncSession, limit: int = 3) -> list[WordORM]:
    """Получает случайные слова из базы данных."""
    result = await session.execute(
        select(WordORM).order_by(func.random()).limit(limit)
    )
    return result.scalars().all()


async def get_random_items() -> tuple[list[TermORM], list[WordORM]]:
    """Получает случайные термины и слова."""
    async for session in get_session():
        terms = await get_random_terms(session)
        words = await get_random_words(session)
        return terms, words


async def save_word_statistics(
    session: AsyncSession, user_id: int, word_id: int, is_correct: bool
):
    """
    Сохраняет статистику использования слова пользователем

    Args:
        session: AsyncSession - сессия БД
        user_id: int - ID пользователя
        word_id: int - ID слова
        is_correct: bool - была ли попытка успешной
    """
    try:
        result = await session.execute(
            select(UserWordStatus).where(
                UserWordStatus.user_id == user_id,
                UserWordStatus.item_id == word_id,
                UserWordStatus.item_type == ItemType.WORD,
            )
        )
        word_status = result.scalar_one_or_none()

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
                item_id=word_id,
                item_type=ItemType.WORD,
                mastery_level=10.0 if is_correct else 0.0,
                ease_factor=2.5,
            )
            session.add(word_status)

        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


# backend/api/v1/endpoints/words.py


async def get_words_for_learning(
    session: AsyncSession,
    user_id: int,
    limit: int = 5,
    word_type: Optional[str] = None,
) -> List[WordORM]:
    """
    Получает слова для изучения:
    1. Все слова которых нет в UserWordStatus (с учетом word_type если указан)
    2. Добавляет слова с низким mastery_level пока не достигнут limit
    """
    # Базовый фильтр по типу слова
    word_type_filter = (
        and_(True) if not word_type else WordORM.word_type == word_type
    )

    # Получаем ID слов, которые есть в UserWordStatus
    tracked_words_query = select(UserWordStatus.item_id).where(
        UserWordStatus.user_id == user_id,
        UserWordStatus.item_type == ItemType.WORD,
    )
    tracked_result = await session.execute(tracked_words_query)
    tracked_word_ids = [row[0] for row in tracked_result]

    # Получаем новые слова (которых нет в UserWordStatus)
    new_words_query = select(WordORM).where(
        and_(
            WordORM.id.not_in(tracked_word_ids) if tracked_word_ids else True,
            word_type_filter,
        )
    )
    new_words_result = await session.execute(new_words_query)
    new_words = new_words_result.scalars().all()

    if random.randint(0, 9) == 0:
        new_words = new_words[:1]

    # Если новых слов >= limit, берем случайные limit штук
    if len(new_words) >= limit:
        selected_words = sorted(new_words, key=lambda x: random.random())[:limit]
        # Записываем взаимодействие только для выбранных слов
        for word in selected_words:
            await record_interaction(session, user_id, word.id, ItemType.WORD)
        return selected_words

    # Если новых слов недостаточно, добираем с низким mastery_level
    required_more = limit - len(new_words)

    tracked_words_query = (
        select(WordORM)
        .join(
            UserWordStatus,
            and_(
                UserWordStatus.item_id == WordORM.id,
                UserWordStatus.item_type == ItemType.WORD,
            ),
        )
        .where(and_(UserWordStatus.user_id == user_id, word_type_filter))
        .order_by(UserWordStatus.mastery_level.asc())
        .limit(required_more)
    )

    tracked_words_result = await session.execute(tracked_words_query)
    tracked_words = tracked_words_result.scalars().all()

    words = new_words + tracked_words

    # Записываем взаимодействие для каждого слова
    for word in words:
        await record_interaction(session, user_id, word.id, ItemType.WORD)

    return words


async def get_terms_for_learning(
    session: AsyncSession,
    user_id: int,
    limit: int = 5,
    category: Optional[str] = None,
) -> List[TermORM]:
    """
    Получает термины для изучения:
    1. Все термины которых нет в UserWordStatus (с учетом category если указана)
    2. Добавляет термины с низким mastery_level пока не достигнут limit
    """

    # Базовый фильтр категории
    category_filter = (
        and_(True) if not category else TermORM.category_main == category
    )

    # Получаем ID терминов из UserWordStatus
    tracked_terms_query = select(UserWordStatus.item_id).where(
        UserWordStatus.user_id == user_id,
        UserWordStatus.item_type == ItemType.TERM,
    )
    tracked_result = await session.execute(tracked_terms_query)
    tracked_term_ids = [row[0] for row in tracked_result]

    # Получаем новые термины
    new_terms_query = select(TermORM).where(
        and_(
            TermORM.id.not_in(tracked_term_ids) if tracked_term_ids else True,
            category_filter,
        )
    )
    new_terms_result = await session.execute(new_terms_query)
    new_terms = new_terms_result.scalars().all()

    if random.randint(0, 9) == 0:
        new_terms = new_terms[:1]

    # Если новых терминов >= limit, берем случайные limit штук
    if len(new_terms) >= limit:
        selected_terms = sorted(new_terms, key=lambda x: random.random())[:limit]
        # Записываем взаимодействие только для выбранных терминов
        for term in selected_terms:
            await record_interaction(session, user_id, term.id, ItemType.TERM)
        return selected_terms

    # Если новых терминов недостаточно, добираем с низким mastery_level
    required_more = limit - len(new_terms)

    tracked_terms_query = (
        select(TermORM)
        .join(
            UserWordStatus,
            and_(
                UserWordStatus.item_id == TermORM.id,
                UserWordStatus.item_type == ItemType.TERM,
            ),
        )
        .where(and_(UserWordStatus.user_id == user_id, category_filter))
        .order_by(UserWordStatus.mastery_level.asc())
        .limit(required_more)
    )

    tracked_terms_result = await session.execute(tracked_terms_query)
    tracked_terms = tracked_terms_result.scalars().all()

    terms = new_terms + tracked_terms

    # Записываем взаимодействие для каждого термина
    for term in terms:
        await record_interaction(session, user_id, term.id, ItemType.TERM)

    return terms


async def record_interaction(
    session: AsyncSession, user_id: int, item_id: int, item_type: ItemType
) -> None:
    """Записать взаимодействие с словом/термином"""
    try:
        logger.debug(f'Recording interaction for {item_type} {item_id}')
        status = await session.execute(
            select(UserWordStatus).where(
                UserWordStatus.user_id == user_id,
                UserWordStatus.item_id == item_id,
                UserWordStatus.item_type == item_type,
            )
        )
        user_word_status = status.scalar_one_or_none()

        if not user_word_status:
            user_word_status = UserWordStatus(
                user_id=user_id, item_id=item_id, item_type=item_type
            )
            session.add(user_word_status)

        user_word_status.last_reviewed = datetime.utcnow()
        await session.flush()

    except Exception as e:
        logger.error(f'Error recording interaction: {e}')
        await session.rollback()
        raise
