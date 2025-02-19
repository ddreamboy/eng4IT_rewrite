# backend/api/v1/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings

from .endpoints import auth, tasks, users


def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения"""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version='1.0.0',
        description='API для системы изучения технического английского',
        docs_url='/docs',  # Добавляем явно
        redoc_url='/redoc',  # Добавляем явно
    )

    app.swagger_ui_init_oauth = {
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': '',
        'clientSecret': '',
    }

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # Подключаем роутеры
    app.include_router(
        auth.router, prefix=f'{settings.API_V1_STR}/auth', tags=['auth']
    )
    app.include_router(
        tasks.tasks_router.router,
        prefix=f'{settings.API_V1_STR}/tasks',
        tags=['tasks'],
    )
    app.include_router(
        users.router, prefix=f'{settings.API_V1_STR}/users', tags=['users']
    )

    return app
