# services/auth.py

from datetime import datetime
from typing import Optional, Tuple

from api.v1.schemas.auth import UserCreate, UserLogin
from core.exceptions import AuthError, NotFoundError
from core.security import (
    create_access_token,
    create_password_hash,
    create_refresh_token,
    verify_password,
)
from db.models import UserORM
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, user_data: UserCreate) -> UserORM:
        """
        Регистрация нового пользователя.

        Args:
            user_data: Данные пользователя для регистрации

        Returns:
            UserORM: Созданный пользователь

        Raises:
            AuthError: Если email уже занят
        """
        try:
            # Создаем пользователя
            user = UserORM(
                username=user_data.username,
                email=user_data.email.lower(),
                password_hash=create_password_hash(user_data.password),
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
            )

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            return user

        except IntegrityError:
            await self.session.rollback()
            raise AuthError('Email already registered')

    async def authenticate_user(
        self, login_data: UserLogin
    ) -> Tuple[UserORM, str, str]:
        """Аутентификация пользователя."""
        # Получаем пользователя
        user = await self.get_user_by_email(login_data.email.lower())
        if not user:
            raise AuthError('Invalid email or password')

        # Проверяем пароль
        if not verify_password(login_data.password, user.password_hash):
            raise AuthError('Invalid email or password')

        if not user.is_active:
            raise AuthError('User is inactive')

        # Важно! Получаем id до любых изменений с объектом
        user_id = int(user.id)  # Явно конвертируем в int

        # Обновляем last_login через отдельный запрос
        await self.session.execute(
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.session.commit()

        # Создаем токены используя сохраненный id
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        return user, access_token, refresh_token

    async def get_user_by_email(self, email: str) -> Optional[UserORM]:
        """Получение пользователя по email."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[UserORM]:
        """Получение пользователя по ID."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        return result.scalar_one_or_none()

    async def refresh_tokens(self, user_id: int) -> Tuple[str, str]:
        """
        Обновление токенов пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Tuple[str, str]: (new_access_token, new_refresh_token)

        Raises:
            NotFoundError: Если пользователь не найден
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')

        if not user.is_active:
            raise AuthError('User is inactive')

        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        return access_token, refresh_token

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """
        Изменение пароля пользователя.

        Args:
            user_id: ID пользователя
            old_password: Текущий пароль
            new_password: Новый пароль

        Returns:
            bool: True если пароль успешно изменен

        Raises:
            AuthError: Если старый пароль неверный
            NotFoundError: Если пользователь не найден
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')

        if not verify_password(old_password, user.password_hash):
            raise AuthError('Invalid old password')

        user.password_hash = create_password_hash(new_password)
        await self.session.commit()

        return True
