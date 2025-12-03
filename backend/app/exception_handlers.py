"""
Exception handlers for CloudPulse Monitor FastAPI application
Provides centralized error handling and response formatting
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from pydantic import ValidationError as PydanticValidationError
from datetime import datetime
import logging
from typing import Union

from .exceptions import (
    CloudPulseException,
    DatabaseConnectionError,
    DatabaseOperationError,
    ValidationError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    RateLimitExceededError,
    create_error_response
)
from .schemas import (
    ErrorResponse,
    ValidationErrorResponse,
    ValidationErrorDetail,
    DatabaseErrorResponse
)
from .logging_config import get_logger

logger = get_logger(__name__)


async def cloudpulse_exception_handler(request: Request, exc: CloudPulseException) -> JSONResponse:
    """
    Handle custom CloudPulse exceptions
    
    Args:
        request: FastAPI request object
        exc: CloudPulse exception instance
    
    Returns:
        JSON response with error details
    """
    logger.error(
        f"CloudPulse exception: {exc.code}",
        extra={
            "error_code": exc.code,
            "error_message": exc.message,
            "error_details": exc.details,
            "request_url": str(request.url),
            "request_method": request.method
        },
        exc_info=True
    )
    
    # Create appropriate response based on exception type
    if isinstance(exc, DatabaseConnectionError):
        response = DatabaseErrorResponse.create(
            message=exc.message,
            fallback_data={"status": "degraded", "message": "Using cached data"}
        )
    else:
        response = ErrorResponse.create(
            code=exc.code,
            message=exc.message,
            details=exc.details
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions
    
    Args:
        request: FastAPI request object
        exc: HTTP exception instance
    
    Returns:
        JSON response with error details
    """
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_url": str(request.url),
            "request_method": request.method
        }
    )
    
    # Map HTTP status codes to error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    response = ErrorResponse.create(
        code=error_code,
        message=str(exc.detail),
        details={"status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI request validation errors
    
    Args:
        request: FastAPI request object
        exc: Request validation error instance
    
    Returns:
        JSON response with validation error details
    """
    logger.warning(
        "Request validation error",
        extra={
            "validation_errors": exc.errors(),
            "request_url": str(request.url),
            "request_method": request.method,
            "request_body": exc.body if hasattr(exc, 'body') else None
        }
    )
    
    # Convert FastAPI validation errors to our format
    validation_errors = []
    for error in exc.errors():
        validation_errors.append(ValidationErrorDetail(
            loc=[str(loc) for loc in error.get("loc", [])],
            msg=error.get("msg", "Validation error"),
            type=error.get("type", "value_error"),
            input=str(error.get("input", "")) if error.get("input") is not None else None
        ))
    
    response = ValidationErrorResponse.create(
        message="Request validation failed",
        validation_errors=validation_errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.dict()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database errors
    
    Args:
        request: FastAPI request object
        exc: SQLAlchemy error instance
    
    Returns:
        JSON response with database error details
    """
    logger.error(
        f"Database error: {type(exc).__name__}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "request_url": str(request.url),
            "request_method": request.method
        },
        exc_info=True
    )
    
    # Determine error type and response
    if isinstance(exc, OperationalError):
        # Database connection or operational issues
        error_code = "DATABASE_CONNECTION_ERROR"
        message = "Database connection failed"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Provide fallback data for critical endpoints
        fallback_data = None
        if "metrics" in str(request.url):
            fallback_data = {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "network_traffic": 0.0,
                "container_count": 0,
                "overall_health": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "degraded"
            }
        elif "services" in str(request.url):
            fallback_data = {
                "services": [],
                "status": "degraded",
                "message": "Service data unavailable"
            }
        
        response = DatabaseErrorResponse.create(
            message=message,
            fallback_data=fallback_data
        )
        
    elif isinstance(exc, IntegrityError):
        # Data integrity violations
        error_code = "DATA_INTEGRITY_ERROR"
        message = "Data integrity constraint violation"
        status_code = status.HTTP_409_CONFLICT
        
        response = ErrorResponse.create(
            code=error_code,
            message=message,
            details={"constraint_violation": True}
        )
        
    else:
        # Generic database error
        error_code = "DATABASE_ERROR"
        message = "Database operation failed"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        response = ErrorResponse.create(
            code=error_code,
            message=message,
            details={"error_type": type(exc).__name__}
        )
    
    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions
    
    Args:
        request: FastAPI request object
        exc: Generic exception instance
    
    Returns:
        JSON response with generic error details
    """
    logger.error(
        f"Unexpected error: {type(exc).__name__}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "request_url": str(request.url),
            "request_method": request.method
        },
        exc_info=True
    )
    
    response = ErrorResponse.create(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details={
            "error_type": type(exc).__name__,
            "debug_mode": False  # Never expose internal details in production
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.dict()
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Custom CloudPulse exceptions
    app.add_exception_handler(CloudPulseException, cloudpulse_exception_handler)
    
    # FastAPI built-in exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Database exceptions
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered successfully")