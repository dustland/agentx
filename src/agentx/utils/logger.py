"""
Simple streaming-aware logging for AgentX.
"""

import logging
import sys
import warnings
from typing import Optional
import os
from pathlib import Path

# Suppress noisy loggers immediately
logging.getLogger("browser_use.telemetry.service").setLevel(logging.ERROR)
logging.getLogger("browser_use.telemetry").setLevel(logging.ERROR)
logging.getLogger("browser_use").setLevel(logging.ERROR)

# Global state
_streaming_mode = False
_task_file_handler = None


def set_streaming_mode(enabled: bool):
    """Enable/disable streaming mode to control console output."""
    global _streaming_mode
    _streaming_mode = enabled


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Simple rule:
    - If streaming mode is active: AgentX loggers go to file only, others suppressed
    - If streaming mode is off: All loggers go to both console and file

    Args:
        name: Logger name (usually __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        global _task_file_handler

        # Always add file handler if available
        if _task_file_handler and name.startswith('agentx'):
            logger.addHandler(_task_file_handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False

        # Add console handler only if not in streaming mode OR for important messages
        if not _streaming_mode or not name.startswith('agentx'):
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            log_level = level or _get_default_log_level()
            logger.setLevel(getattr(logging, log_level.upper()))
            logger.propagate = False

    return logger


def setup_task_file_logging(log_file_path: str) -> None:
    """
    Set up file logging for a specific task.

    Args:
        log_file_path: Path to the log file
    """
    try:
        log_file = Path(log_file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        # Store globally
        global _task_file_handler
        _task_file_handler = file_handler

        # Add file handler to all existing AgentX loggers
        for logger_name in logging.Logger.manager.loggerDict:
            if logger_name.startswith('agentx'):
                logger = logging.getLogger(logger_name)
                if file_handler not in logger.handlers:
                    logger.addHandler(file_handler)
                    logger.setLevel(logging.INFO)

        # Test that it works with a sample log
        test_logger = logging.getLogger('agentx.core.task')
        test_logger.info("Task file logging initialized successfully")

        print(f"Task file logging initialized: {log_file}")

    except Exception as e:
        print(f"Failed to setup task file logging: {e}")


def setup_clean_chat_logging():
    """Configure logging for clean chat experience."""
    verbose = _is_verbose_mode()

    if verbose:
        configure_logging(level="INFO")
    else:
        configure_logging(level="INFO")
        _suppress_noisy_loggers(level="ERROR")
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


def configure_logging(level: str = "INFO", format_string: Optional[str] = None):
    """Configure global logging settings."""
    log_format = format_string or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )


def _suppress_noisy_loggers(level: str = "ERROR"):
    """Suppress specific noisy loggers."""
    noisy_loggers = [
        "LiteLLM", "litellm", "browser_use.telemetry.service",
        "browser_use.telemetry", "browser_use", "httpx",
        "urllib3.connectionpool", "urllib3", "requests.packages.urllib3",
        "selenium", "asyncio", "httpcore", "openai", "anthropic"
    ]

    log_level = getattr(logging, level.upper())
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(log_level)


def _get_default_log_level() -> str:
    """Get default log level based on environment."""
    return "INFO" if _is_verbose_mode() else "WARNING"


def _is_verbose_mode() -> bool:
    """Check if verbose mode is enabled via environment variable."""
    return os.getenv("AGENTX_VERBOSE", "").lower() in ("1", "true", "yes")


# Legacy functions for backward compatibility
def set_log_level(level: str):
    """Set log level for the entire application."""
    configure_logging(level=level)
    if level.upper() != 'DEBUG':
        _suppress_noisy_loggers()
