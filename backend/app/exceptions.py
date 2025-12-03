"""
Custom exceptions and error handling for CloudPulse Monitor
Defines application-specific exceptions and error response models
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime


class CloudPulseException(Exception):
    """Base exception class for CloudPulse Monitor"""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(CloudPulseException):
    """Raised when database connection fails"""
    
    def __init__(self, message: str = "Database connection failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class DatabaseOperationError(CloudPulseException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_OPERATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ValidationError(CloudPulseException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        validation_details = details or {}
        if field:
            validation_details["field"] = field
            
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=validation_details
        )


class ResourceNotFoundError(CloudPulseException):
    """Raised when requested resource is not found"""
    
    def __init__(self, resource: str, identifier: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} with identifier '{identifier}' not found"
        resource_details = details or {}
        resource_details.update({
            "resource": resource,
            "identifier": identifier
        })
        
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=resource_details
        )


class ServiceUnavailableError(CloudPulseException):
    """Raised when a service is temporarily unavailable"""
    
    def __init__(self, service: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_message = message or f"{service} service is temporarily unavailable"
        service_details = details or {}
        service_details["service"] = service
        
        super().__init__(
            message=error_message,
            code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=service_details
        )


class RateLimitExceededError(CloudPulseException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str, details: Optional[Dict[str, Any]] = None):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        rate_details = details or {}
        rate_details.update({
            "limit": limit,
            "window": window
        })
        
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=rate_details
        )


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        code: Error code identifier
        message: Human-readable error message
        details: Additional error details
        timestamp: Error timestamp (defaults to current time)
    
    Returns:
        Standardized error response dictionary
    """
    error_data = {
        "code": code,
        "message": message,
        "timestamp": (timestamp or datetime.utcnow()).isoformat()
    }
    
    if details:
        error_data["details"] = details
    
    return {"error": error_data}