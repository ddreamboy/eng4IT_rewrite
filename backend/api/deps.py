from typing import AsyncGenerator, Optional

from core.security import verify_token
from db.database import get_session
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from services.auth import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.API_V1_STR}/auth/login')

async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> int:
    """
    Получение ID текущего пользователя из токена.

    Args:
        token: JWT токен
        session: Сессия БД

    Returns:
        int: ID пользователя
    """
    try:
        user_id = verify_token(token)
        return int(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AuthService, None]:
    """
    Зависимость для получения сервиса аутентификации.

    Args:
        session: Сессия БД
    """
    yield AuthService(session)


async def validate_content_length(
    content_length: Optional[str] = Header(None),
) -> None:
    """
    Проверка размера запроса.

    Args:
        content_length: Размер запроса в байтах
    """
    if content_length is not None:
        length = int(content_length)
        if length > 10_000_000:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail='Content too large',
            )
