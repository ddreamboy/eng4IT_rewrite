from typing import Optional

from database import async_engine, async_session, get_session
from models import Base, TermORM, WordORM
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


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
    # Проверяем существование термина
    existing_term = await get_term_by_name(session, term_data['term'])
    if existing_term:
        return None

    # Создаем термин
    term = TermORM(
        term=term_data['term'],
        primary_translation=term_data['translations']['primary'],
        category_main=term_data['category']['main'],
        category_sub=term_data['category'].get('sub'),
        difficulty=term_data['difficulty'],
        definition_en=term_data['context']['definition']['en'],
        definition_ru=term_data['context']['definition']['ru'],
        example_en=term_data['context'].get('example', {}).get('en'),
        example_context=term_data['context'].get('example', {}).get('context'),
        related_terms=term_data.get('related_terms', []),
        alternate_translations=term_data['translations'].get('alternates', []),
    )

    session.add(term)
    return term


async def create_word(session: AsyncSession, word_data: dict) -> Optional[WordORM]:
    """Создает новую запись слова в БД."""
    existing_word = await get_word_by_name(session, word_data['word'])
    if existing_word:
        return None

    word = WordORM(
        word=word_data['word'],
        translation=word_data['translation'],
        context=word_data.get('context'),
        context_translation=word_data.get('context_translation'),
        word_type=word_data['word_type'],
        difficulty=word_data['difficulty'],
    )

    session.add(word)
    return word


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
