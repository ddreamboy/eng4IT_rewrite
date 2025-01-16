from api.deps import get_current_user_id, get_session
from fastapi import APIRouter, Depends, HTTPException
from logger import setup_logger
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
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * page_size
    query = select(WordORM).offset(offset).limit(page_size)
    result = await db.execute(query)
    words = result.scalars().all()
    logger.debug(
        f'Fetched {len(words)} words'
    )  # Логирование количества полученных слов
    return words


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
