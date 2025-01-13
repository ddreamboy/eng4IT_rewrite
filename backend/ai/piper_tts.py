import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union

from logger import setup_logger

logger = setup_logger(__name__)


class TTSError(Exception):
    """Базовый класс для ошибок TTS"""

    pass


class ModelNotFoundError(TTSError):
    """Ошибка при отсутствии модели"""

    pass


class AudioGenerationError(TTSError):
    """Ошибка при генерации аудио"""

    pass


class PiperTTS:
    """
    Класс для работы с Piper TTS, адаптированный для приложения изучения английского
    """

    VOICE_MODELS = {
        'rayn': {
            'model': 'en_US-ryan-high.onnx',
            'config': 'en_en_US_ryan_high_en_US-ryan-high.onnx.json',
        }
    }

    def __init__(
        self,
        piper_path: Optional[str] = None,
        output_base_path: Optional[str] = None,
    ):
        """
        Инициализация TTS

        Args:
            piper_path: Путь к директории с piper.exe и моделями
            output_base_path: Базовый путь для сохранения аудио файлов
        """
        logger.info('Initializing PiperTTS')
        logger.info(f'Piper path: {piper_path}')
        # Настройка пути к Piper
        self.piper_path = Path(piper_path) if piper_path else Path(os.getcwd())
        self.piper_exe = self.piper_path / 'piper.exe'

        if not self.piper_exe.exists():
            error_msg = f'piper.exe не найден по пути: {self.piper_exe}'
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Настройка путей для сохранения
        self.output_base_path = (
            Path(output_base_path) if output_base_path else Path('static/audio')
        )
        self._ensure_directories()

        logger.info(
            f'PiperTTS initialized with base path: {self.output_base_path}'
        )

    def _ensure_directories(self) -> None:
        """Создает необходимую структуру директорий для аудио файлов"""
        try:
            self.output_base_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f'Ensuring directory exists: {self.output_base_path}')
        except Exception as e:
            logger.error(f'Failed to create directories: {e}')
            raise TTSError(f'Failed to create audio directory: {e}')

    def _get_voice_paths(self, voice: str) -> Dict[str, Path]:
        """
        Получает пути к файлам модели и конфига для указанного голоса

        Args:
            voice: Ключ голоса из VOICE_MODELS

        Returns:
            Dict с путями к файлам модели и конфига

        Raises:
            ModelNotFoundError: если файлы модели не найдены
        """
        logger.debug(f'Getting voice paths for {voice}')

        if voice not in self.VOICE_MODELS:
            error_msg = f"Голос '{voice}' не найден. Доступные голоса: {list(self.VOICE_MODELS.keys())}"
            logger.error(error_msg)
            raise ModelNotFoundError(error_msg)

        try:
            model_filename = self.VOICE_MODELS[voice]['model']
            config_filename = self.VOICE_MODELS[voice]['config']

            model_path = self.piper_path / 'models' / model_filename
            config_path = self.piper_path / 'configs' / config_filename

            if not model_path.exists():
                raise ModelNotFoundError(f'Файл модели не найден: {model_path}')
            if not config_path.exists():
                raise ModelNotFoundError(f'Файл конфига не найден: {config_path}')

            return {'model': model_path, 'config': config_path}
        except Exception as e:
            logger.error(f'Error getting voice paths: {e}')
            raise

    def get_audio_path(self, filename: str) -> Path:
        """
        Формирует путь для сохранения аудио файла

        Args:
            filename: Имя файла

        Returns:
            Path: Путь к аудио файлу
        """
        return self.output_base_path / f'{filename}.wav'

    def audio_exists(self, filename: str) -> bool:
        """
        Проверяет существование аудио файла

        Args:
            filename: Имя файла

        Returns:
            bool: True если файл существует
        """
        audio_path = self.get_audio_path(filename)
        exists = audio_path.exists()
        logger.debug(
            f'Checking audio existence: {audio_path} - {"exists" if exists else "not found"}'
        )
        return exists

    async def generate_audio(
        self,
        text: str,
        filename: str,
        voice: str = 'rayn',
        force_regenerate: bool = False,
        rate: float = 0.1,
    ) -> Union[Path, None]:
        """
        Генерирует аудио файл для текста

        Args:
            text: Текст для озвучивания
            filename: Имя файла для сохранения
            voice: Ключ голоса из VOICE_MODELS
            force_regenerate: Принудительно перегенерировать, даже если файл существует

        Returns:
            Path: Путь к сгенерированному файлу или None в случае ошибки

        Raises:
            AudioGenerationError: при ошибке генерации
        """
        logger.info(f'Generating audio for filename={filename}')

        output_path = self.get_audio_path(filename)

        # Проверяем существование файла
        if not force_regenerate and output_path.exists():
            logger.info(f'Audio file already exists: {output_path}')
            return output_path

        try:
            paths = self._get_voice_paths(voice)

            # Формируем команду
            command = (
                f'echo "{text}" | "{self.piper_exe}" '
                f'-m "{paths["model"]}" '
                f'-c "{paths["config"]}" '
                f'--rate {rate} '
                f'-f "{output_path}"'
            )

            logger.debug(f'Executing command: {command}')
            process = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True
            )

            if process.returncode == 0:
                logger.info(f'Audio generated successfully: {output_path}')
                return output_path

            logger.error(f'Piper process failed: {process.stderr}')
            raise AudioGenerationError(f'Piper process failed: {process.stderr}')

        except subprocess.CalledProcessError as e:
            error_msg = f'Error executing Piper: {e.stderr}'
            logger.error(error_msg)
            raise AudioGenerationError(error_msg)
        except Exception as e:
            error_msg = f'Unexpected error during audio generation: {e}'
            logger.error(error_msg)
            raise AudioGenerationError(error_msg)


# Example usage:
if __name__ == '__main__':
    # Initialize with paths
    tts = PiperTTS(
        piper_path=r'C:\path\to\piper', output_base_path=r'C:\path\to\output'
    )

    # Generate audio
    import asyncio

    asyncio.run(tts.generate_audio(text='Hello, world!', filename='test_audio'))
