from typing import AsyncGenerator

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.core.config import settings

from .models import Base


async def init_db():
    async_engine = create_async_engine(settings.DB_URL_asyncpg)

    async with async_engine.begin() as conn:
        await conn.run_sync(check_and_create_tables)


def check_and_create_tables(conn):
    inspector = inspect(conn)
    table_names = inspector.get_table_names()

    if not table_names:
        # Если таблиц нет, создаем их
        print('База данных пуста. Создаем таблицы...')
        Base.metadata.create_all(conn)
        print('Таблицы созданы.')
    else:
        # Если таблицы есть, не создаем их заново
        print('База данных уже содержит таблицы.')


async_engine = create_async_engine(
    url=settings.DB_URL_asyncpg, echo=True, pool_size=5, max_overflow=10
)

async_session = async_sessionmaker(async_engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает новую сессию базы данных с автоматической фиксацией или откатом изменений.
    Использование:

    async for session in get_session():
        # Работа с сессией
        ...

    # Или через aclosing:
    async with aclosing(get_session()) as session:
        # Работа с сессией
        ...
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
