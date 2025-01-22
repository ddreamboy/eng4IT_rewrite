# Source path: backend/tests/test_terms.py

from pprint import pprint
from typing import Dict

import requests


def test_get_terms_paginated(base_url: str, auth_headers: Dict[str, str], capsys):
    """Тест получения терминов с пагинацией"""
    with capsys.disabled():
        print('\n=== Список терминов с пагинацией ===')

    response = requests.get(
        f'{base_url}/api/v1/terms/',
        params={'page': 1, 'page_size': 5},
        headers=auth_headers,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'items' in response.json()
    assert len(response.json()['items']) <= 5
    assert 'total_pages' in response.json()


def test_get_all_terms(base_url: str, capsys):
    """Тест получения всех терминов"""
    with capsys.disabled():
        print('\n=== Все термины ===')

    response = requests.get(f'{base_url}/api/v1/terms/all')
    terms = response.json()

    with capsys.disabled():
        print(f'Получено терминов: {len(terms)}')
        if terms:
            print('Пример термина:')
            pprint(terms[0])

    assert response.status_code == 200
    assert isinstance(terms, list)
    assert len(terms) > 0
    assert 'id' in terms[0]
    assert 'term' in terms[0]


def test_term_favorites(
    base_url: str, auth_headers: Dict[str, str], first_term_id: int, capsys
):
    """Тест работы с избранными терминами"""
    # Проверка статуса
    with capsys.disabled():
        print('\n=== Статус избранного термина ===')

    response = requests.get(
        f'{base_url}/api/v1/terms/favorite/{first_term_id}', headers=auth_headers
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'is_favorite' in response.json()

    # Добавление в избранное
    with capsys.disabled():
        print('\n=== Добавление термина в избранное ===')

    response = requests.post(
        f'{base_url}/api/v1/terms/favorite',
        params={'term_id': first_term_id, 'state': True},
        headers=auth_headers,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'message' in response.json()
