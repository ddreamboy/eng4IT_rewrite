# Source path: backend/tests/test_api.py

from pprint import pprint

import requests

# Базовый URL API
BASE_URL = 'http://localhost:7000'


def test_health():
    """Тест эндпоинта health check"""
    print('\n=== Health Check ===')
    response = requests.get(f'{BASE_URL}/health')
    pprint(response.json())
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_auth_flow():
    """Тест полного потока аутентификации"""
    print('\n=== Тестирование аутентификации ===')

    # 1. Регистрация
    user_data = {
        'email': 'check@example.com',
        'username': 'testuser',
        'password': 'StrongP@ss123',
    }
    print('\n--- Регистрация ---')
    response = requests.post(f'{BASE_URL}/api/v1/auth/register', json=user_data)
    pprint(response.json())

    # 2. Логин
    login_data = {
        'username': user_data['email'],
        'password': user_data['password'],
        'grant_type': 'password',
    }
    print('\n--- Логин ---')
    response = requests.post(f'{BASE_URL}/api/v1/auth/login', data=login_data)
    token_data = response.json()
    pprint(token_data)

    # 3. Обновление токена
    print('\n--- Обновление токена ---')
    headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
    response = requests.post(f'{BASE_URL}/api/v1/auth/refresh', headers=headers)
    pprint(response.json())

    return headers


def test_user_profile(headers):
    """Тест получения профиля пользователя"""
    print('\n=== Профиль пользователя ===')
    response = requests.get(f'{BASE_URL}/api/v1/users/profile', headers=headers)
    pprint(response.json())


def test_words_endpoints(headers):
    """Тест эндпоинтов для работы со словами"""
    print('\n=== Тестирование words endpoints ===')

    # Получение списка слов с пагинацией
    print('\n--- Список слов с пагинацией ---')
    response = requests.get(
        f'{BASE_URL}/api/v1/words/',
        params={'page': 1, 'page_size': 5},
        headers=headers,
    )
    pprint(response.json())

    # Получение всех слов
    print('\n--- Все слова ---')
    response = requests.get(f'{BASE_URL}/api/v1/words/all')
    words = response.json()
    print(f'Получено слов: {len(words)}')
    if words:
        print('Пример слова:')
        pprint(words[0])

        # Тест избранного для первого слова
        word_id = words[0]['id']

        print('\n--- Статус избранного ---')
        response = requests.get(
            f'{BASE_URL}/api/v1/words/favorite/{word_id}', headers=headers
        )
        pprint(response.json())

        print('\n--- Добавление в избранное ---')
        response = requests.post(
            f'{BASE_URL}/api/v1/words/favorite',
            params={'word_id': word_id, 'state': True},
            headers=headers,
        )
        pprint(response.json())


def test_terms_endpoints(headers):
    """Тест эндпоинтов для работы с терминами"""
    print('\n=== Тестирование terms endpoints ===')

    # Получение списка терминов с пагинацией
    print('\n--- Список терминов с пагинацией ---')
    response = requests.get(
        f'{BASE_URL}/api/v1/terms/',
        params={'page': 1, 'page_size': 5},
        headers=headers,
    )
    pprint(response.json())

    # Получение всех терминов
    print('\n--- Все термины ---')
    response = requests.get(f'{BASE_URL}/api/v1/terms/all')
    terms = response.json()
    print(f'Получено терминов: {len(terms)}')
    if terms:
        print('Пример термина:')
        pprint(terms[0])

        # Тест избранного для первого термина
        term_id = terms[0]['id']

        print('\n--- Статус избранного ---')
        response = requests.get(
            f'{BASE_URL}/api/v1/terms/favorite/{term_id}', headers=headers
        )
        pprint(response.json())

        print('\n--- Добавление в избранное ---')
        response = requests.post(
            f'{BASE_URL}/api/v1/terms/favorite',
            params={'term_id': term_id, 'state': True},
            headers=headers,
        )
        pprint(response.json())


def test_audio_endpoints():
    """Тест эндпоинтов для работы с аудио"""
    print('\n=== Тестирование audio endpoints ===')

    # Получение аудио термина
    print('\n--- Аудио термина ---')
    response = requests.get(f'{BASE_URL}/api/v1/audio/terms/1')
    print(f'Статус код: {response.status_code}')
    print(f'Content-Type: {response.headers.get("content-type")}')

    # Получение аудио слова
    print('\n--- Аудио слова ---')
    response = requests.get(f'{BASE_URL}/api/v1/audio/words/1')
    print(f'Статус код: {response.status_code}')
    print(f'Content-Type: {response.headers.get("content-type")}')

    # Перегенерация аудио
    print('\n--- Перегенерация аудио ---')
    response = requests.post(f'{BASE_URL}/api/v1/audio/regenerate/word/1')
    print(f'Статус код: {response.status_code}')
    print(f'Content-Type: {response.headers.get("content-type")}')


def test_tasks_generation(headers):
    """Тест генерации различных типов заданий"""
    print('\n=== Тестирование генерации заданий ===')

    # Получение информации о заданиях
    print('\n--- Информация о заданиях ---')
    response = requests.get(f'{BASE_URL}/api/v1/tasks/info')
    pprint(response.json())

    # Генерация word matching
    print('\n--- Генерация word matching ---')
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
        f'{BASE_URL}/api/v1/tasks/generate/word-matching',
        headers=headers,
        json=task_data,
    )
    pprint(response.json())

    # Генерация term definition
    print('\n--- Генерация term definition ---')
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
        f'{BASE_URL}/api/v1/tasks/generate/term-definition',
        headers=headers,
        json=task_data,
    )
    pprint(response.json())

    # Генерация word translation
    print('\n--- Генерация word translation ---')
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
        f'{BASE_URL}/api/v1/tasks/generate/word-translation',
        headers=headers,
        json=task_data,
    )
    pprint(response.json())


def test_achievements(headers):
    """Тест эндпоинтов достижений"""
    print('\n=== Тестирование achievements endpoints ===')
    response = requests.get(
        f'{BASE_URL}/api/v1/achievements/stats', headers=headers
    )
    pprint(response.json())


def main():
    """Основная функция для запуска всех тестов"""
    try:
        # Базовые тесты
        test_health()

        # Тесты с аутентификацией
        headers = test_auth_flow()
        test_user_profile(headers)
        test_words_endpoints(headers)
        test_terms_endpoints(headers)
        test_audio_endpoints()
        test_tasks_generation(headers)
        test_achievements(headers)

        print('\n✅ Все тесты выполнены успешно!')

    except requests.exceptions.RequestException as e:
        print(f'\n❌ Ошибка при выполнении запроса: {e}')
    except Exception as e:
        print(f'\n❌ Неожиданная ошибка: {e}')


if __name__ == '__main__':
    main()
