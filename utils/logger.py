# utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
from core.config import settings
import os

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# This will store already-created loggers to avoid duplicates
_logger_cache = {}

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with specified name and shared formatting.
    """
    if name in _logger_cache:
        return _logger_cache[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Prevent double logging

    formatter = logging.Formatter(
        settings.LOG_FORMAT,
        settings.LOG_DATEFORMAT
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    logger.addHandler(console_handler)

    # File Handler
    if settings.LOG_TO_FILE:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE_PATH,
            maxBytes=1024 * 1024,  # 1 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        logger.addHandler(file_handler)

    # Cache it
    _logger_cache[name] = logger
    return logger
