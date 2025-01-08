import os
from typing import Dict, Optional

import yaml
from pydantic import BaseModel

from logger import setup_logger

logger = setup_logger(__name__)


class PromptTemplate(BaseModel):
    prompt: str


class PromptLoader:
    def __init__(self, prompts_path: str = None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompts_path = prompts_path or os.path.join(current_dir, 'prompts')
        self.templates: Dict[str, PromptTemplate] = {}
        try:
            self.templates = self._load_prompts()
        except Exception as e:
            logger.error(
                f'Error initializing PromptLoader: {type(e).__name__}: {e}',
                exc_info=True,
            )
            raise

    def _load_prompts(self) -> Dict[str, PromptTemplate]:
        logger.debug(f'Entering _load_prompts with path: {self.prompts_path}')
        templates = {}
        duplicate_names = set()

        for filename in os.listdir(self.prompts_path):
            if filename.endswith('.yml'):
                file_path = os.path.join(self.prompts_path, filename)
                logger.info(f'Processing file: {file_path}')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        logger.info(f'Loaded data from {filename}')

                    for name, content in data.items():
                        if name in templates:
                            duplicate_names.add(name)
                            logger.warning(
                                f"Duplicate prompt name '{name}' found in {filename}"
                            )
                        else:
                            templates[name] = PromptTemplate(prompt=content)
                            logger.info(f"Added template '{name}' from {filename}")
                except Exception as e:
                    logger.error(
                        f'Failed to load prompts from {file_path}: {type(e).__name__}: {e}',
                        exc_info=True,
                    )

        if duplicate_names:
            logger.error(
                f"Found duplicate prompt names: {', '.join(duplicate_names)}"
            )
            raise RuntimeError(
                f"Duplicate prompt names found: {', '.join(duplicate_names)}"
            )

        logger.debug('Completed loading all prompts.')
        return templates

    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        logger.debug(f'Entering get_template with template_name: {template_name}')
        template = self.templates.get(template_name)
        if template is None:
            logger.error(f"Prompt template '{template_name}' not found")
            raise KeyError(f"Prompt template '{template_name}' not found")
        return template

    def list_templates(self) -> list[str]:
        logger.debug('Entering list_templates')
        template_keys = list(self.templates.keys())
        logger.info(f'Available templates: {template_keys}')
        logger.debug(f'Exiting list_templates with return value: {template_keys}')
        return template_keys


logger.info(f'{__name__} module loaded successfully.')
