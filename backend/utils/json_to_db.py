import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.db.database import async_session, get_session
from backend.db.orm import create_term, create_word, init_db_tables
from sqlalchemy.ext.asyncio import AsyncSession


async def load_terms_data(file_path: Path) -> List[Dict[Any, Any]]:
    """Загружает данные терминов из JSON файла с учетом категорий."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            categories_data = json.load(file)

            # Собираем все термины из всех категорий
            terms_data = []
            print(f'\nЗагрузка терминов из {file_path}:')
            for category, terms in categories_data.items():
                print(f'• Категория "{category}": {len(terms)} терминов')
                terms_data.extend(terms)

            print(f'\nВсего найдено терминов: {len(terms_data)}')
            if terms_data:
                print('\nСтруктура первого термина:')
                print(json.dumps(terms_data[0], indent=2, ensure_ascii=False))
            return terms_data

    except FileNotFoundError:
        print(f'❌ Файл не найден: {file_path}')
        return []
    except json.JSONDecodeError as e:
        print(f'❌ Ошибка декодирования JSON в файле {file_path}: {str(e)}')
        return []
    except Exception as e:
        print(f'❌ Неожиданная ошибка при чтении {file_path}: {str(e)}')
        return []


async def load_words_data(file_path: Path) -> List[Dict[Any, Any]]:
    """Загружает данные слов из JSON файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words_data = json.load(file)
            print(f'\nЗагрузка слов из {file_path}:')
            print(f'Найдено слов: {len(words_data)}')
            if words_data:
                print('\nСтруктура первого слова:')
                print(json.dumps(words_data[0], indent=2, ensure_ascii=False))
            return words_data

    except FileNotFoundError:
        print(f'❌ Файл не найден: {file_path}')
        return []
    except json.JSONDecodeError as e:
        print(f'❌ Ошибка декодирования JSON в файле {file_path}: {str(e)}')
        return []
    except Exception as e:
        print(f'❌ Неожиданная ошибка при чтении {file_path}: {str(e)}')
        return []


async def process_terms(
    session: AsyncSession, terms_data: List[dict]
) -> Tuple[int, int, int]:
    """Обрабатывает данные терминов."""
    total = len(terms_data)
    success = 0
    skipped = 0
    errors = 0

    print('\n=== Импорт терминов ===')
    for i, term_data in enumerate(terms_data, 1):
        try:
            term = await create_term(session, term_data)
            if term:
                print(f'✓ [{i}/{total}] Добавлен термин: {term.term}')
                success += 1
            else:
                print(
                    f'⚠ [{i}/{total}] Пропущен существующий термин: {term_data.get("term", "Unknown")}'
                )
                skipped += 1
        except Exception as e:
            print(f'\n❌ Ошибка при добавлении термина #{i}:')
            print(f'Данные: {json.dumps(term_data, indent=2, ensure_ascii=False)}')
            print(f'Ошибка: {str(e)}\n')
            errors += 1

    return success, skipped, errors


async def process_words(
    session: AsyncSession, words_data: List[dict]
) -> Tuple[int, int, int]:
    """Обрабатывает данные слов."""
    total = len(words_data)
    success = 0
    skipped = 0
    errors = 0

    print('\n=== Импорт слов ===')
    for i, word_data in enumerate(words_data, 1):
        try:
            word = await create_word(session, word_data)
            if word:
                print(f'✓ [{i}/{total}] Добавлено слово: {word.word}')
                success += 1
            else:
                print(
                    f'⚠ [{i}/{total}] Пропущено существующее слово: {word_data.get("word", "Unknown")}'
                )
                skipped += 1
        except Exception as e:
            print(f'\n❌ Ошибка при добавлении слова #{i}:')
            print(f'Данные: {json.dumps(word_data, indent=2, ensure_ascii=False)}')
            print(f'Ошибка: {str(e)}\n')
            errors += 1

    return success, skipped, errors


async def init_db_from_json() -> None:
    """Инициализирует базу данных данными из JSON файлов."""
    print('\n=== Инициализация базы данных ===')
    await init_db_tables()
    print('✓ Таблицы успешно созданы')

    # Определяем пути к JSON файлам
    base_path = Path(r'Q:\PythonProjects\eng4IT_rewrite\backend\json_data')
    terms_file = base_path / 'terms_db.json'
    words_file = base_path / 'words_db.json'

    # Загружаем данные из JSON
    terms_data = await load_terms_data(terms_file)
    words_data = await load_words_data(words_file)

    if not terms_data and not words_data:
        print('\n❌ Нет данных для импорта')
        return

    # Импортируем данные
    async for session in get_session():
        try:
            # Обрабатываем слова
            if words_data:
                w_success, w_skipped, w_errors = await process_words(
                    session, words_data
                )

            # Обрабатываем термины
            if terms_data:
                t_success, t_skipped, t_errors = await process_terms(
                    session, terms_data
                )

            # Фиксируем изменения
            print('\n=== Итоги импорта ===')
            if terms_data:
                print(
                    f'Термины: {t_success} добавлено, {t_skipped} пропущено, {t_errors} ошибок'
                )
            if words_data:
                print(
                    f'Слова: {w_success} добавлено, {w_skipped} пропущено, {w_errors} ошибок'
                )
            print('✓ Все изменения успешно сохранены')

        except Exception as e:
            print(f'\n❌ Ошибка при импорте данных: {str(e)}')
            print('✗ Изменения отменены')


if __name__ == '__main__':
    import asyncio

    asyncio.run(init_db_from_json())
