import logging
import os
import sys
from datetime import datetime


class BriefFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, max_length=500):
        super().__init__(fmt, datefmt)
        self.max_length = max_length

    def format(self, record):
        # Сначала получаем отформатированное сообщение
        message = super().format(record)

        # Обрезаем если слишком длинное
        if len(message) > self.max_length:
            return message[: self.max_length] + '... [truncated]'
        return message


def setup_logger(name: str, log_dir: str = 'logs') -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Создаем форматтер с ограничением длины
    formatter = BriefFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        max_length=500,
    )

    # Файловый логгер
    log_file = os.path.join(
        log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Консольный логгер
    console_handler = logging.StreamHandler(sys.__stderr__)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger
