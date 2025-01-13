from abc import ABC, abstractmethod
from typing import Any, Dict

from logger import setup_logger

from .gemini import GeminiServiceSinglethon as GeminiService

logger = setup_logger(__name__)


class BaseOperation(ABC):
    def __init__(self):
        logger.debug(f'__init__ called in {__name__} with args: ()')
        self.gemini_service = GeminiService
        logger.debug(f'__init__ completed in {__name__} with return value: None')

    @abstractmethod
    def execute(self, input_data: Dict) -> Dict[str, Any]:
        logger.debug(
            f'execute called in {__name__} with args: input_data={input_data}'
        )
        logger.debug(f'execute completed in {__name__} with return value: None')
        pass


class ActivityName(BaseOperation):
    async def execute(self, input_data: Dict) -> Dict[str, Any]:
        try:
            response = await self.gemini_service.execute_prompt(
                'activity_name', input_data
            )
            return response
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            raise


class ChatDialog(BaseOperation):
    async def execute(self, input_data: Dict) -> Dict[str, Any]:
        try:
            response = await self.gemini_service.execute_prompt(
                'chat_dialog', input_data
            )
            return response
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            raise


class EmailStructure(BaseOperation):
    async def execute(self, input_data: Dict) -> Dict[str, Any]:
        try:
            response = await self.gemini_service.execute_prompt(
                'email_structure', input_data
            )
            return response
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            raise


logger.info('Program completed successfully.')
