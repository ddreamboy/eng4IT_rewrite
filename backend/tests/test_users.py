# Source path: backend/tests/test_users.py

from pprint import pprint
from typing import Dict

import requests


def test_get_profile(base_url: str, auth_headers: Dict[str, str], capsys):
    """Тест получения профиля пользователя"""
    with capsys.disabled():
        print('\n=== Профиль пользователя ===')

    response = requests.get(
        f'{base_url}/api/v1/users/profile', headers=auth_headers
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert 'username' in response.json()
    assert 'statistics' in response.json()
