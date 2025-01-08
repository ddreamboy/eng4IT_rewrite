from api.deps import get_auth_service
from api.v1.schemas.auth import Token, UserCreate, UserLogin
from api.v1.schemas.user import UserResponse
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from services.auth import AuthService

router = APIRouter()


@router.post('/register', response_model=UserResponse)
async def register(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Регистрация нового пользователя.
    """
    user = await auth_service.register_user(user_data)
    return user


@router.post('/login', response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Аутентификация пользователя и получение токена.
    """
    login_data = UserLogin(email=form_data.username, password=form_data.password)

    user, access_token, refresh_token = await auth_service.authenticate_user(
        login_data
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post('/refresh', response_model=Token)
async def refresh_token(
    current_user_id: int = Depends(get_auth_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Обновление токенов доступа.
    """
    access_token, refresh_token = await auth_service.refresh_tokens(
        current_user_id
    )

    return Token(access_token=access_token, refresh_token=refresh_token)
