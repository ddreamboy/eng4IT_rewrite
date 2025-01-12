from api.deps import get_auth_service, oauth2_scheme
from api.v1.schemas.auth import Token, UserCreate, UserLogin
from api.v1.schemas.user import UserResponse
from fastapi import APIRouter, Depends, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from services.auth import AuthService

from backend.core.exceptions import AuthError
from backend.core.security import verify_token

router = APIRouter()


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя',
    description="""
    Регистрация нового пользователя в системе.
    
    - **username**: имя пользователя (3-50 символов)
    - **email**: действующий email адрес
    - **password**: надежный пароль (минимум 8 символов)
    
    После успешной регистрации возвращается информация о созданном пользователе.
    """,
)
async def register(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
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


@router.post(
    '/refresh',
    response_model=Token,
)
async def refresh_token(
    current_token: str = Security(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Обновление токенов доступа.
    """
    try:
        user_id = verify_token(current_token, token_type='refresh')
        access_token, refresh_token = await auth_service.refresh_tokens(
            int(user_id)
        )
        return Token(access_token=access_token, refresh_token=refresh_token)
    except Exception:
        raise AuthError('Could not refresh token')
