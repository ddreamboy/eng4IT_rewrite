import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateTable

from backend.core.config import settings
from backend.db.models import ChatDialogGenerated, EmailStructureGenerated


async def create_tables():
    # Создаем engine
    engine = create_async_engine(settings.DB_URL_asyncpg)

    async with engine.begin() as conn:
        # Создаем таблицы
        await conn.run_sync(
            lambda conn: CreateTable(ChatDialogGenerated.__table__).compile(engine)
        )
        await conn.execute(CreateTable(ChatDialogGenerated.__table__))

        await conn.run_sync(
            lambda conn: CreateTable(EmailStructureGenerated.__table__).compile(
                engine
            )
        )
        await conn.execute(CreateTable(EmailStructureGenerated.__table__))

        print('Таблицы успешно созданы!')

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(create_tables())
