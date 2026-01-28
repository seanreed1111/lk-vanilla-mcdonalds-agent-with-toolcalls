"""Logging configuration for the drive-thru agent.

Configures loguru to:
- Log to console (INFO level)
- Log to rotating files in ./logs directory (DEBUG level)
- Rotate files every 4 hours
- Delete logs older than 2 days
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_dir: str = "logs") -> None:
    """Configure loguru logging with file rotation.

    Args:
        log_dir: Directory for log files (default: "logs")
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add console handler (INFO level and above)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    # Add file handler with rotation and retention (DEBUG level and above)
    logger.add(
        log_path / "agent_{time:YYYY-MM-DD_HH-mm-ss}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="4 hours",  # Rotate every 4 hours
        retention="2 days",  # Keep logs for 2 days
        compression="zip",  # Compress rotated logs
        enqueue=True,  # Thread-safe logging
        backtrace=True,
        diagnose=True,

    )

    logger.info(f"Logging configured: console (INFO), files in {log_path} (DEBUG)")
    logger.debug(
        f"File rotation: every 4 hours, retention: 2 days, compression: enabled"
    )
