import asyncio
from backend.db.orm import get_random_items


async def show_random_items():
    """Показывает случайные термины и слова."""
    terms, words = await get_random_items()

    print('\n=== Случайные технические термины ===')
    for term in terms:
        print(f'\n• {term.term} - {term.primary_translation}')
        print(f'  Категория: {term.category_main}')
        print(f'  Сложность: {term.difficulty}')
        print(f'  Определение: {term.definition_ru}')

    print('\n=== Случайные слова ===')
    for word in words:
        print(f'\n• {word.word} - {word.translation}')
        print(f'  Тип: {word.word_type}')
        print(f'  Сложность: {word.difficulty}')
        if word.context:
            print(f'  Контекст: {word.context}')
            print(f'  Перевод: {word.context_translation}')


if __name__ == '__main__':
    asyncio.run(show_random_items())
