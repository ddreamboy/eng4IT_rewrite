import asyncio

from database import async_engine
from sqlalchemy import text


async def drop_all_tables():
    """Удаляет все таблицы из базы данных."""
    print('Удаление всех таблиц...')
    async with async_engine.begin() as conn:
        try:
            # Отключаем проверку внешних ключей
            await conn.execute(text('SET session_replication_role = replica'))

            # Получаем список всех таблиц
            tables_query = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            )
            tables = [row[0] for row in tables_query]

            # Удаляем каждую таблицу
            for table in tables:
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

            # Возвращаем режим проверки внешних ключей
            await conn.execute(text('SET session_replication_role = origin'))

            # Явно коммитим транзакцию
            await conn.commit()

            print('Все таблицы успешно удалены!')

        except Exception as e:
            # Логируем ошибку
            print(f'Ошибка при удалении таблиц: {e}')
            # Откатываем транзакцию
            await conn.rollback()
            raise


if __name__ == '__main__':
    asyncio.run(drop_all_tables())
