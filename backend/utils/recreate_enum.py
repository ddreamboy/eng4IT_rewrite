# backend/utils/update_task_type_enum.py
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.core.config import settings


async def update_task_type_in_tables():
    engine = create_async_engine(settings.DB_URL_asyncpg)

    async with engine.begin() as conn:
        await conn.execute(text('BEGIN;'))

        try:
            # Обновляем значения в learning_attempts
            await conn.execute(
                text("""
                UPDATE learning_attempts 
                SET task_type = upper(task_type::text)::tasktype 
                WHERE task_type::text != upper(task_type::text);
            """)
            )

            # Обновляем значения в task_contexts
            await conn.execute(
                text("""
                UPDATE task_contexts 
                SET context_type = upper(context_type::text)::tasktype 
                WHERE context_type::text != upper(context_type::text);
            """)
            )

            # Фиксируем транзакцию
            await conn.execute(text('COMMIT;'))
            print('TaskType values successfully updated to uppercase!')

        except Exception as e:
            # В случае ошибки откатываем транзакцию
            await conn.execute(text('ROLLBACK;'))
            raise e


if __name__ == '__main__':
    asyncio.run(update_task_type_in_tables())
