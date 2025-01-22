# Source path: backend/tests/test_health.py
from pprint import pprint

import requests


def test_health_check(base_url: str, capsys):
    """Тест эндпоинта health check"""
    with capsys.disabled():
        print('\n=== Health Check ===')

    response = requests.get(f'{base_url}/health')

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert 'version' in response.json()
