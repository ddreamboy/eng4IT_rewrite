# Source path: backend/tests/test_achievements.py


from pprint import pprint
from typing import Dict

import requests


def test_get_achievement_stats(
    base_url: str, auth_headers: Dict[str, str], capsys
):
    """Тест получения статистики достижений"""
    with capsys.disabled():
        print('\n=== Статистика достижений ===')

    response = requests.get(
        f'{base_url}/api/v1/achievements/stats', headers=auth_headers
    )

    with capsys.disabled():
        pprint(response.json())

    assert response.status_code == 200
    stats = response.json()
    assert 'daily_stats' in stats
    assert 'total_stats' in stats
    assert 'goals' in stats['daily_stats']
    assert 'words' in stats['daily_stats']['goals']
    assert 'terms' in stats['daily_stats']['goals']
