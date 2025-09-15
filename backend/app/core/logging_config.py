"""
Comprehensive logging and error handling configuration.

This module provides structured logging, error tracking, and monitoring capabilities.
"""

import logging
import logging.config
import sys
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable, Type, Union
import types
from pathlib import Path
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

from app.core.config import settings


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        logger = logging.getLogger("api.requests")

        # Extract client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "headers": dict(request.headers) if settings.debug else {},
            }
        )

        try:
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                }
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "process_time_ms": round(process_time * 1000, 2),
                    "traceback": traceback.format_exc() if settings.debug else None,
                }
            )
            raise


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if they exist
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id

        # Add any extra data from the log record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'message', 'exc_info',
                          'exc_text', 'stack_info']:
                log_data[key] = value

        # Format as JSON in production, human-readable in development
        if settings.environment == "production":
            import json
            return json.dumps(log_data, default=str)
        else:
            # Human-readable format for development
            base_msg = f"{log_data['timestamp']} [{log_data['level']}] {log_data['logger']}: {log_data['message']}"

            if 'request_id' in log_data:
                request_id = str(log_data['request_id'])
                base_msg += f" [req:{request_id[:8]}]"

            if len(log_data) > 8:  # More than base fields
                extra_fields = {k: v for k, v in log_data.items()
                              if k not in ['timestamp', 'level', 'logger', 'message', 'module', 'function', 'line', 'request_id']}
                if extra_fields:
                    base_msg += f" | {extra_fields}"

            return base_msg


def setup_logging() -> None:
    """Configure application logging."""

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Determine log level
    log_level = "DEBUG" if settings.debug else "INFO"

    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            },
            "simple": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "structured",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "structured",
                "filename": str(log_dir / "app.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "structured",
                "filename": str(log_dir / "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            # Application loggers
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "api.requests": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "api.auth": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "api.errors": {
                "level": "ERROR",
                "handlers": ["console", "error_file"],
                "propagate": False
            },
            # Third-party loggers
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            }
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"]
        }
    }

    logging.config.dictConfig(logging_config)

    # Set up exception logging
    def handle_exception(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Optional[types.TracebackType]) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_logger = logging.getLogger("api.errors")
        error_logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={
                "error_type": exc_type.__name__,
                "error_message": str(exc_value)
            }
        )

    sys.excepthook = handle_exception


class APIError(Exception):
    """Base class for API errors with structured logging."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERR_{status_code}"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, "VALIDATION_ERROR", details)


class AuthenticationError(APIError):
    """Authentication error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, "AUTHENTICATION_ERROR", details)


class AuthorizationError(APIError):
    """Authorization error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, "AUTHORIZATION_ERROR", details)


class ResourceNotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, "RESOURCE_NOT_FOUND", details)


class ConflictError(APIError):
    """Resource conflict error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 409, "RESOURCE_CONFLICT", details)


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED", details)


class ServiceUnavailableError(APIError):
    """Service unavailable error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 503, "SERVICE_UNAVAILABLE", details)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Global API error handler."""
    error_logger = logging.getLogger("api.errors")

    request_id = getattr(request.state, 'request_id', None)

    error_logger.error(
        f"API Error: {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "url": str(request.url),
            "method": request.method,
        }
    )

    error_response = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "request_id": request_id
        }
    }

    # Add details in development
    if settings.debug and exc.details:
        error_response["error"]["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    error_logger = logging.getLogger("api.errors")
    request_id = getattr(request.state, 'request_id', None)

    error_logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "request_id": request_id
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    error_logger = logging.getLogger("api.errors")
    request_id = getattr(request.state, 'request_id', None)

    error_logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "url": str(request.url),
            "method": request.method,
        }
    )

    # Don't expose internal error details in production
    message = "Internal server error" if settings.environment == "production" else str(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": message,
                "request_id": request_id
            }
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)


# Convenience loggers
app_logger = get_logger("app")
auth_logger = get_logger("api.auth")
request_logger = get_logger("api.requests")
error_logger = get_logger("api.errors")