# Source path: backend/tests/conftest.py

from typing import Dict

import pytest
import requests


@pytest.fixture(scope='session')
def base_url() -> str:
    """Фикстура с базовым URL"""
    return 'http://localhost:7000'


@pytest.fixture(scope='session')
def test_user() -> Dict[str, str]:
    """Фикстура с тестовым пользователем"""
    return {
        'email': 'check@example.com',
        'username': 'testuser',
        'password': 'StrongP@ss123',
    }


@pytest.fixture(scope='session')
def auth_headers(base_url: str, test_user: Dict[str, str]) -> Dict[str, str]:
    """Фикстура для получения заголовков авторизации"""
    # Сначала регистрируем пользователя
    requests.post(f'{base_url}/api/v1/auth/register', json=test_user)

    # Логинимся для получения токена
    login_data = {
        'username': test_user['email'],
        'password': test_user['password'],
        'grant_type': 'password',
    }
    response = requests.post(f'{base_url}/api/v1/auth/login', data=login_data)
    token = response.json()['access_token']

    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='session')
def first_word_id(base_url: str) -> int:
    """Фикстура для получения ID первого слова"""
    response = requests.get(f'{base_url}/api/v1/words/all')
    return response.json()[0]['id']


@pytest.fixture(scope='session')
def first_term_id(base_url: str) -> int:
    """Фикстура для получения ID первого термина"""
    response = requests.get(f'{base_url}/api/v1/terms/all')
    return response.json()[0]['id']
