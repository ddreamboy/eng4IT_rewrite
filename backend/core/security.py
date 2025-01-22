# core/security.py

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .exceptions import AuthError

# Настраиваем контекст для хеширования паролей
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_password_hash(password: str) -> str:
    """Создает хеш пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT access token.

    Args:
        subject: Идентификатор пользователя (обычно user_id)
        expires_delta: Время жизни токена
    """
    if expires_delta is None:
        expires_delta = settings.ACCESS_TOKEN_EXPIRE_DELTA

    expire = datetime.utcnow() + expires_delta

    to_encode = {'exp': expire, 'sub': str(subject), 'type': 'access'}

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT refresh token.

    Args:
        subject: Идентификатор пользователя (обычно user_id)
        expires_delta: Время жизни токена
    """
    if expires_delta is None:
        expires_delta = settings.REFRESH_TOKEN_EXPIRE_DELTA

    expire = datetime.utcnow() + expires_delta

    to_encode = {'exp': expire, 'sub': str(subject), 'type': 'refresh'}

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: str = 'access') -> str:
    """
    Проверяет JWT токен и возвращает user_id.

    Args:
        token: JWT токен
        token_type: Тип токена ("access" или "refresh")

    Raises:
        AuthError: Если токен недействителен
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Проверяем тип токена
        if payload.get('type') != token_type:
            raise AuthError('Invalid token type')

        user_id: str = payload.get('sub')
        if user_id is None:
            raise AuthError('Token missing user identifier')

        return user_id

    except JWTError:
        raise AuthError('Invalid token')


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Проверяет надежность пароля.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < settings.MINIMUM_PASSWORD_LENGTH:
        return (
            False,
            f'Password must be at least {settings.MINIMUM_PASSWORD_LENGTH} characters long',
        )

    if not any(char.isupper() for char in password):
        return False, 'Password must contain at least one uppercase letter'

    if not any(char.islower() for char in password):
        return False, 'Password must contain at least one lowercase letter'

    if not any(char.isdigit() for char in password):
        return False, 'Password must contain at least one number'

    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    if not any(char in special_chars for char in password):
        return False, 'Password must contain at least one special character'

    return True, ''
