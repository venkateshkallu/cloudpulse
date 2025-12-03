"""
Pydantic schemas for CloudPulse Monitor API
Defines request/response models for data validation and serialization
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional, Literal
from decimal import Decimal


# Base schemas with common fields
class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields"""
    timestamp: datetime = Field(..., description="Timestamp of the record")


class CreatedUpdatedMixin(BaseModel):
    """Mixin for models with created/updated timestamps"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


# Log schemas
class LogBase(BaseModel):
    """Base log schema with common fields"""
    level: Literal["info", "warning", "error"] = Field(..., description="Log level")
    message: str = Field(..., min_length=1, max_length=1000, description="Log message")
    service_name: str = Field(..., min_length=1, max_length=100, description="Service name")


class LogCreate(LogBase):
    """Schema for creating new log entries"""
    timestamp: Optional[datetime] = Field(None, description="Log timestamp (defaults to now)")


class LogResponse(LogBase, TimestampMixin):
    """Schema for log API responses"""
    id: int = Field(..., description="Unique log ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class LogsListResponse(BaseModel):
    """Schema for paginated logs list response"""
    logs: List[LogResponse] = Field(..., description="List of log entries")
    total: int = Field(..., ge=0, description="Total number of logs")
    limit: int = Field(..., ge=1, le=1000, description="Number of logs per page")
    offset: int = Field(..., ge=0, description="Offset for pagination")


# Service schemas
class ServiceBase(BaseModel):
    """Base service schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Service display name")
    status: Literal["online", "degraded", "offline"] = Field(..., description="Service status")
    uptime: Decimal = Field(..., ge=0, le=100, description="Service uptime percentage")


class ServiceCreate(ServiceBase):
    """Schema for creating new services"""
    id: str = Field(..., min_length=1, max_length=50, description="Unique service identifier")


class ServiceUpdate(BaseModel):
    """Schema for updating existing services"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Service display name")
    status: Optional[Literal["online", "degraded", "offline"]] = Field(None, description="Service status")
    uptime: Optional[Decimal] = Field(None, ge=0, le=100, description="Service uptime percentage")


class ServiceResponse(ServiceBase):
    """Schema for service API responses"""
    id: str = Field(..., description="Unique service identifier")
    last_checked: datetime = Field(..., description="Last health check timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Metric schemas
class MetricBase(BaseModel):
    """Base metric schema with common fields"""
    metric_name: str = Field(..., min_length=1, max_length=50, description="Metric name")
    value: Decimal = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, max_length=20, description="Metric unit")


class MetricCreate(MetricBase):
    """Schema for creating new metrics"""
    timestamp: Optional[datetime] = Field(None, description="Metric timestamp (defaults to now)")


class MetricResponse(MetricBase, TimestampMixin):
    """Schema for metric API responses"""
    id: int = Field(..., description="Unique metric ID")

    class Config:
        from_attributes = True


class MetricsListResponse(BaseModel):
    """Schema for metrics list response"""
    metrics: List[MetricResponse] = Field(..., description="List of metrics")
    total: int = Field(..., ge=0, description="Total number of metrics")


# Dashboard and aggregated data schemas
class SystemMetrics(BaseModel):
    """Schema for current system metrics"""
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    network_traffic: float = Field(..., ge=0, description="Network traffic in MB/s")
    container_count: int = Field(..., ge=0, description="Number of running containers")
    overall_health: float = Field(..., ge=0, le=100, description="Overall system health score")
    timestamp: datetime = Field(..., description="Metrics timestamp")


class SystemStatus(BaseModel):
    """Schema for overall system status"""
    overall_status: Literal["healthy", "warning", "critical"] = Field(..., description="Overall system status")
    services_online: int = Field(..., ge=0, description="Number of online services")
    services_total: int = Field(..., ge=0, description="Total number of services")
    critical_alerts: int = Field(..., ge=0, description="Number of critical alerts")
    last_updated: datetime = Field(..., description="Last status update timestamp")


# Query parameter schemas
class LogsQueryParams(BaseModel):
    """Schema for logs query parameters"""
    limit: int = Field(50, ge=1, le=1000, description="Number of logs to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    level: Optional[Literal["info", "warning", "error"]] = Field(None, description="Filter by log level")
    service: Optional[str] = Field(None, max_length=100, description="Filter by service name")
    start_time: Optional[datetime] = Field(None, description="Filter logs after this time")
    end_time: Optional[datetime] = Field(None, description="Filter logs before this time")

    @validator('end_time')
    def validate_time_range(cls, v, values):
        """Ensure end_time is after start_time"""
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('end_time must be after start_time')
        return v


class MetricsQueryParams(BaseModel):
    """Schema for metrics query parameters"""
    metric_name: Optional[str] = Field(None, max_length=50, description="Filter by metric name")
    start_time: Optional[datetime] = Field(None, description="Filter metrics after this time")
    end_time: Optional[datetime] = Field(None, description="Filter metrics before this time")
    limit: int = Field(100, ge=1, le=1000, description="Number of metrics to return")

    @validator('end_time')
    def validate_time_range(cls, v, values):
        """Ensure end_time is after start_time"""
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('end_time must be after start_time')
        return v


# Error response schemas
class ErrorDetail(BaseModel):
    """Schema for detailed error information"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    issue: str = Field(..., description="Description of the issue")
    value: Optional[str] = Field(None, description="Invalid value that caused the error")


class ValidationErrorDetail(BaseModel):
    """Schema for validation error details"""
    loc: List[str] = Field(..., description="Location of the validation error")
    msg: str = Field(..., description="Validation error message")
    type: str = Field(..., description="Type of validation error")
    input: Optional[str] = Field(None, description="Input value that caused the error")


class ErrorInfo(BaseModel):
    """Schema for error information"""
    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for standardized API error responses"""
    error: ErrorInfo = Field(..., description="Error information")
    
    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: Optional[dict] = None,
        timestamp: Optional[datetime] = None
    ):
        """Create a standardized error response"""
        error_info = ErrorInfo(
            code=code,
            message=message,
            timestamp=timestamp or datetime.utcnow(),
            details=details
        )
        return cls(error=error_info)


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""
    error: ErrorInfo = Field(..., description="Error information")
    validation_errors: List[ValidationErrorDetail] = Field(..., description="Detailed validation errors")
    
    @classmethod
    def create(
        cls,
        message: str = "Validation failed",
        validation_errors: List[ValidationErrorDetail] = None,
        timestamp: Optional[datetime] = None
    ):
        """Create a validation error response"""
        error_info = ErrorInfo(
            code="VALIDATION_ERROR",
            message=message,
            timestamp=timestamp or datetime.utcnow(),
            details={"validation_error_count": len(validation_errors or [])}
        )
        return cls(error=error_info, validation_errors=validation_errors or [])


class DatabaseErrorResponse(BaseModel):
    """Schema for database error responses"""
    error: ErrorInfo = Field(..., description="Error information")
    fallback_data: Optional[dict] = Field(None, description="Fallback data when database is unavailable")
    
    @classmethod
    def create(
        cls,
        message: str = "Database operation failed",
        fallback_data: Optional[dict] = None,
        timestamp: Optional[datetime] = None
    ):
        """Create a database error response with optional fallback data"""
        error_info = ErrorInfo(
            code="DATABASE_ERROR",
            message=message,
            timestamp=timestamp or datetime.utcnow(),
            details={"has_fallback": fallback_data is not None}
        )
        return cls(error=error_info, fallback_data=fallback_data)