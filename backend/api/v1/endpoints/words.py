from math import ceil
from typing import Optional

from api.deps import get_current_user_id, get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from logger import setup_logger
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db.models import (  # Добавлены импорты
    ItemType,
    UserWordStatus,
    WordORM,
)

logger = setup_logger(__name__)

router = APIRouter()


@router.get('/')
async def get_words(
    page: int = 1,
    page_size: int = 20,
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    word_type: Optional[str] = Query(None),
    favorites_only: bool = Query(False),
    db: AsyncSession = Depends(get_session),
    user_id: Optional[int] = Depends(get_current_user_id),
):
    offset = (page - 1) * page_size
    query = select(WordORM)

    # Применяем фильтры
    if difficulty:
        query = query.filter(WordORM.difficulty == difficulty)

    if word_type:
        query = query.filter(WordORM.word_type == word_type)

    if search:
        search_filter = (
            WordORM.word.ilike(f'%{search}%')
            | WordORM.translation.ilike(f'%{search}%')
            | WordORM.context.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    if favorites_only and user_id:
        # Подзапрос для получения избранных слов
        favorites_subquery = select(UserWordStatus.item_id).filter(
            UserWordStatus.user_id == user_id,
            UserWordStatus.item_type == ItemType.WORD,
            UserWordStatus.is_favorite,
        )
        query = query.filter(WordORM.id.in_(favorites_subquery))

    # Добавляем пагинацию
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    words = result.scalars().all()

    # Получаем общее количество записей для пагинации
    total_query = select(func.count()).select_from(WordORM)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    return {
        'items': words,
        'total': total_items,
        'page': page,
        'page_size': page_size,
        'total_pages': ceil(total_items / page_size),
    }


@router.get('/all')
async def get_all_words(db: AsyncSession = Depends(get_session)):
    query = select(WordORM)
    result = await db.execute(query)
    words = result.scalars().all()
    response = [
        {
            'id': word.id,
            'word': word.word,
            'translation': word.translation,
            'word_type': word.word_type,
            'difficulty': word.difficulty,
        }
        for word in words
    ]
    return response


@router.get('/favorite/{word_id}')
async def get_word_favorite_status(
    word_id: int,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    # Получение статуса избранного для слова
    result = await db.execute(
        select(UserWordStatus.is_favorite).filter_by(
            user_id=user_id, item_id=word_id, item_type=ItemType.WORD
        )
    )
    status = result.scalars().first()
    return {'is_favorite': status if status is not None else False}


@router.post('/favorite')
async def add_word_to_favorites(
    word_id: int,
    state: bool,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    # Проверка существования слова
    word = await db.get(WordORM, word_id)
    if not word:
        raise HTTPException(status_code=404, detail='Word not found')

    # Получение статуса пользователя для слова
    result = await db.execute(
        select(UserWordStatus).filter_by(
            user_id=user_id, item_id=word_id, item_type=ItemType.WORD
        )
    )
    status = result.scalars().first()

    if status:
        status.is_favorite = state
    else:
        status = UserWordStatus(
            user_id=user_id,
            item_id=word_id,
            item_type=ItemType.WORD,
            is_favorite=state,
        )
        db.add(status)

    await db.commit()
    return {'message': 'Word added to favorites'}
