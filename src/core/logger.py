import logging
import sys
from typing import Union
from functools import wraps

from src.config import LOG_FILEPATH


class AsyncLogger(logging.Logger):
    def __init__(self, name: str, level: Union[int, str] = logging.NOTSET):
        super().__init__(name, level)

    async def async_log(self, level: int, msg: str, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    async def async_debug(self, msg: str, *args, **kwargs):
        await self.async_log(logging.DEBUG, msg, *args, **kwargs)

    async def async_info(self, msg: str, *args, **kwargs):
        await self.async_log(logging.INFO, msg, *args, **kwargs)

    async def async_warning(self, msg: str, *args, **kwargs):
        await self.async_log(logging.WARNING, msg, *args, **kwargs)

    async def async_error(self, msg: str, *args, **kwargs):
        await self.async_log(logging.ERROR, msg, *args, **kwargs)

    async def async_critical(self, msg: str, *args, **kwargs):
        await self.async_log(logging.CRITICAL, msg, *args, **kwargs)


def get_logger(name: str) -> AsyncLogger:
    logger = AsyncLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to the lowest level, handlers will filter

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # File Handler
    file_handler = logging.FileHandler(LOG_FILEPATH)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_async(level: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            log_method = getattr(logger, f"async_{level.lower()}")
            await log_method(f"Calling {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                await log_method(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                await logger.async_error(f"Error in {func.__name__}: {str(e)}")
                raise

        return wrapper

    return decorator
