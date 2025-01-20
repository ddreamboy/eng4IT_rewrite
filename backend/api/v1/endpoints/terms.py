from math import ceil
from typing import Optional

from api.deps import get_current_user_id, get_session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,  # Новый импорт для обработки ошибок
)
from logger import setup_logger
from sqlalchemy import func
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
    page: int = 1,
    page_size: int = 20,
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    category_main: Optional[str] = Query(None),
    favorites_only: bool = Query(False),
    db: AsyncSession = Depends(get_session),
    user_id: Optional[int] = Depends(get_current_user_id),
):
    offset = (page - 1) * page_size
    query = select(TermORM)

    # Применяем фильтры
    if difficulty:
        query = query.filter(TermORM.difficulty == difficulty)

    if category_main:
        query = query.filter(TermORM.category_main == category_main)

    if search:
        search_filter = (
            TermORM.term.ilike(f'%{search}%')
            | TermORM.primary_translation.ilike(f'%{search}%')
            | TermORM.definition_ru.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    if favorites_only and user_id:
        # Подзапрос для получения избранных терминов
        favorites_subquery = select(UserWordStatus.item_id).filter(
            UserWordStatus.user_id == user_id,
            UserWordStatus.item_type == ItemType.TERM,
            UserWordStatus.is_favorite,
        )
        query = query.filter(TermORM.id.in_(favorites_subquery))

    # Добавляем пагинацию
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    terms = result.scalars().all()

    # Получаем общее количество записей для пагинации
    total_query = select(func.count()).select_from(TermORM)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    return {
        'items': terms,
        'total': total_items,
        'page': page,
        'page_size': page_size,
        'total_pages': ceil(total_items / page_size),
    }
    
@router.get('/all')
async def get_all_terms(db: AsyncSession = Depends(get_session)):
    query = select(TermORM)
    result = await db.execute(query)
    terms = result.scalars().all()
    response = [
        {
            'id': term.id,
            'term': term.term,
            'definition_en': term.definition_en,
            'definition_ru': term.definition_ru,
            'category_main': term.category_main,
            'category_additional': term.category_sub,
            'difficulty': term.difficulty,
        }
        for term in terms
    ]
    return response


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
