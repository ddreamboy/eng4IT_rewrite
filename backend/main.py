# backend/main.py

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from logger import setup_logger

from backend.api.v1.endpoints import audio, auth, tasks, terms, users, words
from backend.api.v1.endpoints.tasks.handlers import register_handlers
from backend.core.config import settings
from backend.core.exceptions import AuthError, NotFoundError, ValidationError
from backend.db.database import init_db

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Контекст жизненного цикла приложения."""
    # Startup
    logger.info('Starting up FastAPI application')
    await init_db()
    register_handlers()  # Регистрируем обработчики при запуске
    yield
    # Shutdown
    logger.info('Shutting down FastAPI application')


# Инициализация FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version='1.0.0',
    description='API для системы изучения технического английского',
    lifespan=lifespan,
    docs_url=None,  # Отключаем стандартный Swagger UI
    redoc_url=None,  # Отключаем стандартный ReDoc
    openapi_tags=[
        {
            'name': 'auth',
            'description': 'Операции аутентификации и авторизации',
        },
        {
            'name': 'tasks',
            'description': 'Операции с заданиями',
        },
        {
            'name': 'audio',
            'description': 'Озвучивание текста',
        },
        {
            'name': 'users',
            'description': 'Операции с пользователями',
        },
        {
            'name': 'terms',
            'description': 'Операции с терминами',
        },
        {
            'name': 'words',
            'description': 'Операции с словами',
        },
    ],
    openapi_security=[
        {'bearerAuth': {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}}
    ],
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    + ['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Обработчики ошибок
@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    """Обработчик ошибок аутентификации."""
    logger.warning(f'Auth error: {exc.detail}')
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(
    request: Request, exc: NotFoundError
) -> JSONResponse:
    """Обработчик ошибок 404."""
    logger.warning(f'Not found error: {exc.detail}')
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # Логируем полную информацию об ошибке
    logger.error(f'Validation Error: {exc}')

    # Получаем тело запроса для детального анализа
    body = await request.json()
    logger.error(f'Request Body: {body}')

    return JSONResponse(
        status_code=422,
        content={
            'error': 'Validation Error',
            'details': str(exc),
            'request_body': body,
        },
    )


# Кастомный Swagger UI с дополнительными настройками
@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html() -> None:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f'{settings.PROJECT_NAME} - Swagger UI',
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url='https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.js',
        swagger_css_url='https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui.css',
        swagger_favicon_url='https://fastapi.tiangolo.com/img/favicon.png',
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version='1.0.0',
        description='API система для изучения технического английского',
        routes=app.routes,
    )

    # Настраиваем security schemes
    openapi_schema['components']['securitySchemes'] = {
        # 'OAuth2PasswordBearer': {
        #     'type': 'oauth2',
        #     'flows': {
        #         'password': {
        #             'tokenUrl': f'{settings.API_V1_STR}/auth/login',
        #             'scopes': {},
        #         }
        #     },
        # },
        'OAuth2PasswordBearer': {'type': 'http', 'scheme': 'bearer'},
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Подключение роутеров
app.include_router(
    auth.router, prefix=f'{settings.API_V1_STR}/auth', tags=['auth']
)
app.include_router(
    tasks.tasks_router.router,
    prefix=f'{settings.API_V1_STR}/tasks',
    tags=['tasks'],
)
app.include_router(
    audio.router, prefix=f'{settings.API_V1_STR}/audio', tags=['audio']
)
app.include_router(
    terms.router, prefix=f'{settings.API_V1_STR}/terms', tags=['terms']
)
app.include_router(
    words.router, prefix=f'{settings.API_V1_STR}/words', tags=['words']
)
app.include_router(
    users.router, prefix=f'{settings.API_V1_STR}/users', tags=['users']
)


# Health check
@app.get('/health', tags=['health'])
async def health_check() -> dict:
    """Проверка работоспособности API."""
    return {'status': 'ok', 'version': '1.0.0'}


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=7000, reload=True)
