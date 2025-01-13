from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.piper_tts import PiperTTS
from backend.core.config import settings
from backend.core.exceptions import NotFoundError
from backend.db.models import TermORM, WordORM


class AudioService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tts = PiperTTS(
            piper_path=settings.PIPER_PATH,
            output_base_path=settings.PIPER_AUDIO_PATH,
        )

    async def get_term_audio(
        self, term_id: int, type: Optional[str] = None
    ) -> Tuple[Path, str]:
        """
        Получает или генерирует аудио для термина

        Returns:
            Tuple[Path, str]: (путь к файлу, имя файла)
        """
        # Получаем термин
        term = await self.session.get(TermORM, term_id)
        if not term:
            raise NotFoundError('Term not found')

        # Определяем имя файла и текст
        if type == 'def':
            filename = f'term_{term_id}_def'
            text = term.definition_en
        else:
            filename = f'term_{term_id}'
            text = term.term

        # Генерируем если нужно
        if not self.tts.audio_exists(filename):
            await self.tts.generate_audio(text=text, filename=filename)

        audio_path = self.tts.get_audio_path(filename)
        return audio_path, f'{filename}.wav'

    async def get_word_audio(
        self, word_id: int, type: Optional[str] = None
    ) -> Tuple[Path, str]:
        """
        Получает или генерирует аудио для слова

        Returns:
            Tuple[Path, str]: (путь к файлу, имя файла)
        """
        # Получаем слово
        word = await self.session.get(WordORM, word_id)
        if not word:
            raise NotFoundError('Word not found')

        # Определяем имя файла и текст
        if type == 'context' and word.context:
            filename = f'word_{word_id}_context'
            text = word.context
        else:
            filename = f'word_{word_id}'
            text = word.word

        # Генерируем если нужно
        if not self.tts.audio_exists(filename):
            await self.tts.generate_audio(text=text, filename=filename)

        audio_path = self.tts.get_audio_path(filename)
        return audio_path, f'{filename}.wav'

    async def regenerate_audio(
        self, item_type: str, item_id: int, type: Optional[str] = None
    ) -> Tuple[Path, str]:
        """Принудительная перегенерация аудио"""
        if item_type == 'term':
            return await self.get_term_audio(term_id=item_id, type=type)
        elif item_type == 'word':
            return await self.get_word_audio(word_id=item_id, type=type)
        else:
            raise ValueError('Invalid item type')
