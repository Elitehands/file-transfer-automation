"""Centralized logging configuration"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup centralized logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        logging.Logger: Configured logger
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    log_file = log_dir / f"transfer_automation_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
