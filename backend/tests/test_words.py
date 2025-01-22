# Source path: backend/tests/test_words.py

from pprint import pprint
from typing import Dict

import requests


def test_get_words_paginated(base_url: str, auth_headers: Dict[str, str], capsys):
    """Тест получения слов с пагинацией"""
    with capsys.disabled():
        print('\n=== Список слов с пагинацией ===')

    response = requests.get(
        f'{base_url}/api/v1/words/',
        params={'page': 1, 'page_size': 5},
        headers=auth_headers,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'items' in response.json()
    assert len(response.json()['items']) <= 5


def test_get_all_words(base_url: str, capsys):
    """Тест получения всех слов"""
    with capsys.disabled():
        print('\n=== Все слова ===')

    response = requests.get(f'{base_url}/api/v1/words/all')
    words = response.json()

    with capsys.disabled():
        print(f'Получено слов: {len(words)}')
        if words:
            print('Пример слова:')
            pprint(words[0])

    assert response.status_code == 200
    assert isinstance(words, list)
    assert len(words) > 0


def test_word_favorites(
    base_url: str, auth_headers: Dict[str, str], first_word_id: int, capsys
):
    """Тест работы с избранными словами"""
    # Проверка статуса
    with capsys.disabled():
        print('\n=== Статус избранного ===')

    response = requests.get(
        f'{base_url}/api/v1/words/favorite/{first_word_id}', headers=auth_headers
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'is_favorite' in response.json()

    # Добавление в избранное
    with capsys.disabled():
        print('\n=== Добавление в избранное ===')

    response = requests.post(
        f'{base_url}/api/v1/words/favorite',
        params={'word_id': first_word_id, 'state': True},
        headers=auth_headers,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'message' in response.json()
