from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from api.v1.endpoints import auth, tasks
from core.config import settings
from core.exceptions import AuthError, NotFoundError, ValidationError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Контекст жизненного цикла приложения."""
    # Startup
    logger.info('Starting up FastAPI application')
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
    ],
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
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
async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации."""
    logger.warning(f'Validation error: {exc.detail}')
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
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
    """Кастомная конфигурация OpenAPI."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version='1.0.0',
        description='API система для изучения технического английского',
        routes=app.routes,
    )

    # Добавляем дополнительную информацию
    openapi_schema['info']['x-logo'] = {
        'url': 'https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png'
    }

    # Настраиваем security schemes
    openapi_schema['components']['securitySchemes'] = {
        'bearerAuth': {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Подключение роутеров
app.include_router(
    auth.router, prefix=f'{settings.API_V1_STR}/auth', tags=['auth']
)
app.include_router(
    tasks.router, prefix=f'{settings.API_V1_STR}/tasks', tags=['tasks']
)


# Health check
@app.get('/health', tags=['health'])
async def health_check() -> dict:
    """Проверка работоспособности API."""
    return {'status': 'ok', 'version': '1.0.0'}


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
