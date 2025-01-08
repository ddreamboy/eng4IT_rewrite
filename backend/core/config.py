# core/config.py

from datetime import timedelta
from typing import Optional
from typing import Any

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Existing settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    GEMINI_API_KEY: str

    # API Settings
    API_V1_STR: str = '/api/v1'
    PROJECT_NAME: str = 'Eng4IT'

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @field_validator('BACKEND_CORS_ORIGINS')
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str  # для JWT
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis settings
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None

    # Security settings
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    MINIMUM_PASSWORD_LENGTH: int = 4

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def ACCESS_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def REFRESH_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def DB_URL_asyncpg(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
