# Source path: backend/tests/test_audio.py


import requests


def test_get_term_audio(base_url: str, first_term_id: int, capsys):
    """Тест получения аудио для термина"""
    with capsys.disabled():
        print('\n=== Получение аудио термина ===')

    response = requests.get(f'{base_url}/api/v1/audio/terms/{first_term_id}')

    with capsys.disabled():
        print(f'Статус код: {response.status_code}')
        print(f'Content-Type: {response.headers.get("content-type")}')

    assert response.status_code == 200
    assert response.headers.get('content-type') == 'audio/wav'


def test_get_word_audio(base_url: str, first_word_id: int, capsys):
    """Тест получения аудио для слова"""
    with capsys.disabled():
        print('\n=== Получение аудио слова ===')

    response = requests.get(f'{base_url}/api/v1/audio/words/{first_word_id}')

    with capsys.disabled():
        print(f'Статус код: {response.status_code}')
        print(f'Content-Type: {response.headers.get("content-type")}')

    assert response.status_code == 200
    assert response.headers.get('content-type') == 'audio/wav'


def test_regenerate_audio(base_url: str, first_word_id: int, capsys):
    """Тест перегенерации аудио"""
    with capsys.disabled():
        print('\n=== Перегенерация аудио ===')

    response = requests.post(
        f'{base_url}/api/v1/audio/regenerate/word/{first_word_id}'
    )

    with capsys.disabled():
        print(f'Статус код: {response.status_code}')
        print(f'Content-Type: {response.headers.get("content-type")}')

    assert response.status_code == 200
    assert response.headers.get('content-type') == 'audio/wav'
