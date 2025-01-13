from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.piper_tts import TTSError
from backend.api.deps import get_session
from backend.core.exceptions import NotFoundError
from backend.services.audio import AudioService

router = APIRouter()


async def get_audio_service(
    session: AsyncSession = Depends(get_session),
) -> AudioService:
    """Dependency для получения сервиса"""
    return AudioService(session)


@router.get('/terms/{term_id}')
async def get_term_audio(
    term_id: int,
    type: Optional[str] = None,
    audio_service: AudioService = Depends(get_audio_service),
):
    """Получение аудио для термина"""
    try:
        audio_path, filename = await audio_service.get_term_audio(term_id, type)
        return FileResponse(
            path=audio_path, media_type='audio/wav', filename=filename
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TTSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get('/words/{word_id}')
async def get_word_audio(
    word_id: int,
    type: Optional[str] = None,
    audio_service: AudioService = Depends(get_audio_service),
):
    """Получение аудио для слова"""
    try:
        audio_path, filename = await audio_service.get_word_audio(word_id, type)
        return FileResponse(
            path=audio_path, media_type='audio/wav', filename=filename
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TTSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post('/regenerate/{item_type}/{item_id}')
async def regenerate_audio(
    item_type: str,
    item_id: int,
    type: Optional[str] = None,
    audio_service: AudioService = Depends(get_audio_service),
):
    """Принудительная перегенерация аудио"""
    try:
        audio_path, filename = await audio_service.regenerate_audio(
            item_type, item_id, type
        )
        return FileResponse(
            path=audio_path, media_type='audio/wav', filename=filename
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (NotFoundError, TTSError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
