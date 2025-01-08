import asyncio
import base64
import json
import os
import re
import uuid
from collections import deque
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Optional

import google.generativeai as genai

from config import settings
from logger import setup_logger
from prompt_loader import PromptLoader

logger = setup_logger(__name__)


class RateLimiter:
    def __init__(self, requests_per_minute: int = 15, min_interval: float = 1.0):
        logger.info(
            f'RateLimiter initialized: {requests_per_minute} rpm, {min_interval}s interval'
        )
        self.requests_per_minute = requests_per_minute
        self.min_interval = min_interval
        self.requests = deque()
        self.lock = asyncio.Lock()
        self.last_request_time: Optional[datetime] = None

    async def acquire(self, request_type: str):
        logger.debug(
            f'Acquiring rate limiter: {self.requests_per_minute} rpm, {self.min_interval}s min interval for {request_type}'
        )
        try:
            async with self.lock:
                logger.debug(f'Acquired lock for {request_type}')
                now = datetime.now()
                logger.debug(f'Current time: {now}')

                # Очистка старых запросов (старше минуты)
                logger.debug('Clearing old requests')
                while self.requests and (now - self.requests[0]) > timedelta(
                    minutes=1
                ):
                    removed = self.requests.popleft()
                    logger.debug(f'Removed old request timestamp: {removed}')

                # Проверка количества запросов в минуту
                logger.debug(f'Current request count: {len(self.requests)}')
                if len(self.requests) >= self.requests_per_minute:
                    oldest_request = self.requests[0]
                    wait_time = (
                        oldest_request + timedelta(minutes=1) - now
                    ).total_seconds()
                    logger.info(
                        f'Rate limit reached for {request_type}, waiting {wait_time:.2f}s'
                    )
                    await asyncio.sleep(wait_time)
                    now = datetime.now()
                    logger.debug(f'Woke up from sleep, current time: {now}')

                # Проверка минимального интервала между запросами
                if self.last_request_time:
                    time_since_last = (
                        now - self.last_request_time
                    ).total_seconds()
                    logger.debug(
                        f'Time since last request: {time_since_last:.2f}s'
                    )
                    if time_since_last < self.min_interval:
                        wait_time = self.min_interval - time_since_last
                        logger.info(
                            f'Enforcing min interval for {request_type}, waiting {wait_time:.2f}s'
                        )
                        await asyncio.sleep(wait_time)
                        now = datetime.now()
                        logger.debug(
                            f'Woke up from min interval sleep, current time: {now}'
                        )

                self.requests.append(now)
                self.last_request_time = now
                logger.debug(
                    f'Request permitted for {request_type}: {len(self.requests)}/{self.requests_per_minute} rpm'
                )
        except Exception as e:
            logger.error(f'Exception in RateLimiter.acquire: {e}', exc_info=True)
        finally:
            logger.debug(f'Release lock for {request_type}')


class GeminiServiceError(Exception):
    def __init__(self, message: str, raw_response: str = None):
        self.message = message
        self.raw_response = raw_response
        super().__init__(self.message)


class GeminiService:
    def __init__(self):
        logger.info('Initializing GeminiService')
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.prompt_loader = PromptLoader()
            self.model = self._create_model_with_system_instruction()
            self.rate_limiter = RateLimiter(
                requests_per_minute=settings.REQUESTS_PER_MINUTE,
                min_interval=settings.MIN_REQUEST_INTERVAL,
            )
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            logger.info('GeminiService initialized successfully')
        except Exception as e:
            logger.error(f'Error initializing GeminiService: {e}', exc_info=True)

    def _create_model_with_system_instruction(self):
        system_template = self.prompt_loader.get_template('system_instruction')
        system_instruction = system_template.prompt if system_template else ''
        return genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL_NAME,
            system_instruction=system_instruction,
        )

    def _clean_json_string(self, json_str: str) -> str:
        logger.debug(f'_clean_json_string called with: {json_str}')
        try:
            json_str = re.sub(r',(\s*})', r'\1', json_str)
            logger.info('Removed trailing commas before }')
            json_str = re.sub(r',(\s*])', r'\1', json_str)
            logger.info('Removed trailing commas before ]')
            logger.debug(f'Cleaned JSON string: {json_str}')
            return json_str
        except Exception as e:
            logger.error(f'Exception in _clean_json_string: {e}', exc_info=True)
            return json_str

    def _extract_json_from_response(self, response_text: str) -> Dict:
        try:
            logger.debug(f'Raw response from Gemini: {response_text[:100]}')

            if not response_text or response_text.isspace():
                logger.info('Empty response received')
                raise GeminiServiceError('Empty response from model')

            cleaned_response = response_text.strip()
            logger.debug(f'Cleaned response: {cleaned_response}')

            if '```json' in cleaned_response:
                parts = cleaned_response.split('```json')
                logger.debug(f'Split response into parts: {parts}')
                if len(parts) < 2:
                    logger.error('Malformed JSON block in response')
                    raise GeminiServiceError('Malformed JSON block in response')
                json_str = parts[1].split('```')[0].strip()
                logger.info('Extracted JSON from ```json block')
            elif '```' in cleaned_response:
                parts = cleaned_response.split('```')
                logger.debug(f'Split response into parts: {parts}')
                if len(parts) < 3:
                    logger.error('Malformed code block in response')
                    raise GeminiServiceError('Malformed code block in response')
                json_str = parts[1].strip()
                logger.info('Extracted JSON from ``` block')
            else:
                json_str = cleaned_response
                logger.info('Extracted JSON from plain text')

            logger.debug(f'Extracted JSON string before cleaning: {json_str[:100]}')

            json_str = self._clean_json_string(json_str)
            logger.debug(f'Cleaned JSON string: {json_str}')

            try:
                parsed_json = json.loads(json_str)
                logger.info('Parsed JSON successfully')
                if not isinstance(parsed_json, dict):
                    logger.error('Response is not a JSON object')
                    raise GeminiServiceError('Response is not a JSON object')
                logger.debug(f'Parsed JSON: {parsed_json}')
                return parsed_json
            except json.JSONDecodeError as e:
                logger.error(f'JSON decode error: {e}', exc_info=True)
                raise GeminiServiceError(
                    f'Invalid JSON format: {str(e)}', raw_response=response_text
                )

        except GeminiServiceError as e:
            logger.error(f'GeminiServiceError: {e.message}', exc_info=True)
            raise
        except Exception as e:
            logger.error(f'Error extracting JSON: {e}', exc_info=True)
            raise GeminiServiceError(
                f'Failed to parse response: {str(e)}', raw_response=response_text
            )

    async def execute_prompt(
        self,
        template_name: str,
        input_data: Dict,
    ) -> Dict:
        try:
            await self.rate_limiter.acquire('execute_prompt')

            template = self.prompt_loader.get_template(template_name)
            prompt = template.prompt.format_map(input_data)

            generation_parts = []

            generation_parts.append(prompt)

            generation_config = genai.types.GenerationConfig(
                temperature=settings.DEFAULT_TEMPERATURE,
                top_p=settings.DEFAULT_TOP_P,
            )
            logger.debug(f'Generation parts length: {len(generation_parts)} and types: {[type(element) for element in generation_parts]}')
            response = await self.model.generate_content_async(
                generation_parts, generation_config=generation_config
            )

            if not response or not response.text:
                raise GeminiServiceError('Empty response from Gemini')

            result = self._extract_json_from_response(response.text)
            return result

        except Exception as e:
            logger.error(f'Error in execute_prompt: {e}', exc_info=True)
            raise


GeminiServiceSinglethon = GeminiService()
