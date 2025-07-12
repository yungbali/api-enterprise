"""
Logging Configuration
"""
import logging
import structlog
from typing import Any, Dict

from app.core.config import settings


def setup_logging():
    """Configure structured logging."""
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(message)s",
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.LOG_FORMAT == "console" else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_api_call(
    method: str,
    endpoint: str,
    user_id: str = None,
    request_id: str = None,
    **kwargs: Any,
):
    """Log API call with structured data."""
    logger = get_logger("api")
    logger.info(
        "API call",
        method=method,
        endpoint=endpoint,
        user_id=user_id,
        request_id=request_id,
        **kwargs,
    )


def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: str = None,
    request_id: str = None,
):
    """Log error with structured data."""
    logger = get_logger("error")
    logger.error(
        "Error occurred",
        error=str(error),
        error_type=type(error).__name__,
        context=context or {},
        user_id=user_id,
        request_id=request_id,
    )
