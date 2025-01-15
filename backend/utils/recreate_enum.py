# backend/utils/recreate_enum.py
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.core.config import settings

async def check_tasktype_values():
    """Проверяет, какие значения есть в типе tasktype."""
    engine = create_async_engine(settings.DB_URL_asyncpg)

    async with engine.connect() as conn:
        # Получаем все значения типа tasktype
        result = await conn.execute(
            text("SELECT unnest(enum_range(NULL::tasktype)) AS tasktype_value;")
        )
        values = [row.tasktype_value for row in result]
        print("Текущие значения типа tasktype:")
        for value in values:
            print(value)
        return values

async def update_tasktype_values_to_uppercase():
    """Приводит все значения типа tasktype к верхнему регистру."""
    engine = create_async_engine(settings.DB_URL_asyncpg)

    async with engine.begin() as conn:
        try:
            # Получаем текущие значения типа tasktype
            result = await conn.execute(
                text("SELECT unnest(enum_range(NULL::tasktype)) AS tasktype_value;")
            )
            current_values = [row.tasktype_value for row in result]

            # Создаем новый тип tasktype_new
            await conn.execute(text("CREATE TYPE tasktype_new AS ENUM ();"))

            # Добавляем значения в новый тип, избегая дублирования
            for value in current_values:
                uppercase_value = value.upper()
                try:
                    await conn.execute(
                        text(f"ALTER TYPE tasktype_new ADD VALUE '{uppercase_value}';")
                    )
                except Exception as e:
                    # Если значение уже существует, пропускаем его
                    print(f"Значение '{uppercase_value}' уже существует в tasktype_new, пропускаем.")

            # Заменяем старый тип на новый
            await conn.execute(text("ALTER TABLE learning_attempts ALTER COLUMN task_type TYPE tasktype_new USING task_type::text::tasktype_new;"))
            await conn.execute(text("ALTER TABLE task_contexts ALTER COLUMN context_type TYPE tasktype_new USING context_type::text::tasktype_new;"))

            # Удаляем старый тип и переименовываем новый
            await conn.execute(text("DROP TYPE tasktype;"))
            await conn.execute(text("ALTER TYPE tasktype_new RENAME TO tasktype;"))

            print("Все значения типа tasktype приведены к верхнему регистру!")
        except Exception as e:
            print(f"Ошибка при обновлении типа tasktype: {e}")
            raise

async def add_tasktype_value(new_value: str):
    """Добавляет новое значение в тип tasktype."""
    engine = create_async_engine(settings.DB_URL_asyncpg)

    async with engine.begin() as conn:
        try:
            # Добавляем новое значение в тип tasktype
            await conn.execute(
                text(f"ALTER TYPE tasktype ADD VALUE '{new_value}';")
            )
            print(f"Значение '{new_value}' успешно добавлено в тип tasktype!")
        except Exception as e:
            print(f"Ошибка при добавлении значения '{new_value}': {e}")
            raise

async def main():
    # Приводим все значения типа tasktype к верхнему регистру
    await update_tasktype_values_to_uppercase()

    # Проверяем текущие значения
    current_values = await check_tasktype_values()

    # Если значение WORD_MATCHING отсутствует, добавляем его
    if 'WORD_MATCHING' not in current_values:
        await add_tasktype_value('WORD_MATCHING')
    else:
        print("Значение WORD_MATCHING уже существует в типе tasktype.")

if __name__ == '__main__':
    asyncio.run(main())