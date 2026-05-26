"""
Logging and error handling utilities
"""
import logging
import sys
from typing import Any, Dict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config import settings


def setup_logging():
    """Configure application logging"""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(console_handler)

    # Set third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    return root_logger


logger = setup_logging()


async def log_request(request: Request, call_next):
    """Log incoming requests"""
    import time
    
    start_time = time.time()
    response = await call_next(request)
    
    process_time = time.time() - start_time
    log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
    
    logger.log(
        log_level,
        f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = "ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error"""
    
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")


class NotFoundError(AppException):
    """Resource not found error"""
    
    def __init__(self, resource: str = "Resource"):
        message = f"{resource} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND, "NOT_FOUND")


class AuthenticationError(AppException):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, "AUTHENTICATION_ERROR")


class DatabaseError(AppException):
    """Database error"""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, "DATABASE_ERROR")


async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger.error(f"{exc.error_code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    errors: list[Dict[str, Any]] = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": errors,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.LOG_LEVEL == "DEBUG":
        detail = str(exc)
    else:
        detail = "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )
