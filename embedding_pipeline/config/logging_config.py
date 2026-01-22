"""Logging configuration for the embedding pipeline service."""

import logging
from logging import Formatter, StreamHandler
import sys

formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)

def setup_logging(log_level: int = logging.INFO):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure uvicorn loggers to use the same handler
    uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]
    for logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.addHandler(handler)
        uvicorn_logger.setLevel(log_level)
        uvicorn_logger.propagate = False
    
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger
