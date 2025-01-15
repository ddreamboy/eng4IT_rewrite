from api.deps import get_current_user_id, get_session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,  # Новый импорт для обработки ошибок
)
from logger import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db.models import (
    ItemType,
    TermORM,
    UserWordStatus,  # Новый импорт модели
)

logger = setup_logger(__name__)

router = APIRouter()


@router.get('/')
async def get_terms(
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * page_size
    query = select(TermORM).offset(offset).limit(page_size)
    result = await db.execute(query)
    terms = result.scalars().all()
    logger.debug(
        f'Fetched {len(terms)} terms'
    )  # Логирование количества полученных терминов
    return terms


@router.get('/categories')
async def get_term_categories(db: AsyncSession = Depends(get_session)):
    query = select(TermORM.category_main).distinct()
    result = await db.execute(query)
    categories = result.scalars().all()
    return categories


@router.get('/favorite/{term_id}')
async def get_term_favorite_status(
    term_id: int,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    # Получение статуса избранного для термина
    result = await db.execute(
        select(UserWordStatus.is_favorite).filter_by(
            user_id=user_id, item_id=term_id, item_type=ItemType.TERM
        )
    )
    status = result.scalars().first()
    return {'is_favorite': status if status is not None else False}


@router.post('/favorite')
async def add_term_to_favorites(
    term_id: int,
    state: bool,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    # Проверка существования термина
    term = await db.get(TermORM, term_id)
    if not term:
        raise HTTPException(status_code=404, detail='Term not found')

    # Получение статуса пользователя для термина
    result = await db.execute(
        select(UserWordStatus).filter_by(
            user_id=user_id, item_id=term_id, item_type=ItemType.TERM
        )
    )
    status = result.scalars().first()

    if status:
        status.is_favorite = state
    else:
        status = UserWordStatus(
            user_id=user_id,
            item_id=term_id,
            item_type=ItemType.TERM,
            is_favorite=state,
        )
        db.add(status)

    await db.commit()

    if state:
        response = {'message': 'Term added to favorites'}
    else:
        response = {'message': 'Term removed from favorites'}

    return response
