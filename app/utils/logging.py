"""Logging configuration utilities."""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console log formatter."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
    colored: bool = True,
) -> None:
    """Configure application logging."""
    # Convert level string to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if colored and sys.stdout.isatty():
        console_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        console_handler.setFormatter(ColoredFormatter(console_format))
    elif json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))

    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)

        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_format = "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s"
            file_handler.setFormatter(logging.Formatter(file_format))

        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding extra data to log records."""

    def __init__(self, logger: logging.Logger, **extra_data):
        self.logger = logger
        self.extra_data = extra_data
        self._old_factory = None

    def __enter__(self):
        self._old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self._old_factory(*args, **kwargs)
            record.extra_data = self.extra_data
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self._old_factory)


def log_function_call(logger: logging.Logger):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Calling {func_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed: {str(e)}")
                raise
        return wrapper
    return decorator


def create_audit_logger(log_dir: str = "output/logs") -> logging.Logger:
    """Create a dedicated audit logger for tracking important actions."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger('audit')
    logger.setLevel(logging.INFO)

    # Audit log file
    today = datetime.now().strftime('%Y-%m-%d')
    handler = logging.FileHandler(
        f"{log_dir}/audit_{today}.log",
        encoding='utf-8'
    )
    handler.setFormatter(JSONFormatter())

    logger.addHandler(handler)
    return logger


def log_api_call(
    logger: logging.Logger,
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    error: Optional[str] = None,
) -> None:
    """Log an API call with standard format."""
    log_data = {
        'type': 'api_call',
        'method': method,
        'url': url,
        'status_code': status_code,
        'duration_ms': duration_ms,
    }

    if error:
        log_data['error'] = error
        logger.error(f"API {method} {url} failed: {error}", extra={'extra_data': log_data})
    else:
        logger.info(f"API {method} {url} -> {status_code} ({duration_ms:.0f}ms)", extra={'extra_data': log_data})


def log_scrape_result(
    logger: logging.Logger,
    source: str,
    articles_found: int,
    duration_seconds: float,
    error: Optional[str] = None,
) -> None:
    """Log a scraping result with standard format."""
    log_data = {
        'type': 'scrape_result',
        'source': source,
        'articles_found': articles_found,
        'duration_seconds': duration_seconds,
    }

    if error:
        log_data['error'] = error
        logger.warning(f"Scrape {source} failed: {error}", extra={'extra_data': log_data})
    else:
        logger.info(f"Scraped {articles_found} articles from {source} in {duration_seconds:.1f}s", extra={'extra_data': log_data})
