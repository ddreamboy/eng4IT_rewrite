# Source path: backend/tests/test_tasks.py


from pprint import pprint
from typing import Dict

import requests


def test_get_tasks_info(base_url: str, capsys):
    """Тест получения информации о заданиях"""
    with capsys.disabled():
        print('\n=== Информация о заданиях ===')

    response = requests.get(f'{base_url}/api/v1/tasks/info')

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    tasks_info = response.json()
    assert isinstance(tasks_info, list)
    assert len(tasks_info) > 0
    assert 'id' in tasks_info[0]
    assert 'title' in tasks_info[0]


def test_generate_word_matching(
    base_url: str, auth_headers: Dict[str, str], capsys
):
    """Тест генерации word matching задания"""
    with capsys.disabled():
        print('\n=== Генерация word matching ===')

    task_data = {
        'task_type': 'word_matching',
        'user_id': 1,
        'params': {
            'pairs_count': 5,
            'category': 'databases',
            'difficulty': 'intermediate',
        },
    }

    response = requests.post(
        f'{base_url}/api/v1/tasks/generate/word-matching',
        headers=auth_headers,
        json=task_data,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'task_id' in response.json()
    assert 'status' in response.json()
    assert response.json()['status'] == 'completed'


def test_generate_term_definition(
    base_url: str, auth_headers: Dict[str, str], capsys
):
    """Тест генерации term definition задания"""
    with capsys.disabled():
        print('\n=== Генерация term definition ===')

    task_data = {
        'task_type': 'term_definition',
        'user_id': 1,
        'params': {
            'category': 'backend',
            'with_context': True,
            'difficulty': 'intermediate',
        },
    }

    response = requests.post(
        f'{base_url}/api/v1/tasks/generate/term-definition',
        headers=auth_headers,
        json=task_data,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'task_id' in response.json()
    assert 'result' in response.json()


def test_generate_word_translation(
    base_url: str, auth_headers: Dict[str, str], capsys
):
    """Тест генерации word translation задания"""
    with capsys.disabled():
        print('\n=== Генерация word translation ===')

    task_data = {
        'task_type': 'word_translation',
        'user_id': 1,
        'params': {
            'word_type': 'verb',
            'with_context': True,
            'difficulty': 'basic',
        },
    }

    response = requests.post(
        f'{base_url}/api/v1/tasks/generate/word-translation',
        headers=auth_headers,
        json=task_data,
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'task_id' in response.json()
    assert 'result' in response.json()
