# Source path: backend/tests/test_auth.py

from pprint import pprint
from typing import Dict

import requests


def test_register(base_url: str, test_user: Dict[str, str], capsys):
    """Тест регистрации пользователя"""
    with capsys.disabled():
        print('\n=== Регистрация ===')

    response = requests.post(f'{base_url}/api/v1/auth/register', json=test_user)

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code in [200, 201, 401]  # 401 если уже существует


def test_login(base_url: str, test_user: Dict[str, str], capsys):
    """Тест входа пользователя"""
    with capsys.disabled():
        print('\n=== Логин ===')

    login_data = {
        'username': test_user['email'],
        'password': test_user['password'],
        'grant_type': 'password',
    }
    response = requests.post(f'{base_url}/api/v1/auth/login', data=login_data)

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_refresh_token(base_url: str, auth_headers: Dict[str, str], capsys):
    """Тест обновления токена"""
    with capsys.disabled():
        print('\n=== Обновление токена ===')

    response = requests.post(
        f'{base_url}/api/v1/auth/refresh', headers=auth_headers
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'access_token' in response.json()
