from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from config import settings

async_engine = create_async_engine(
    url=settings.DB_URL_asyncpg,
    echo=True,
    pool_size=5,
    max_overflow=10
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