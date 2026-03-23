"""
Pydantic schemas for CloudPulse Monitor API
Defines request/response models for data validation and serialization
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
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


# Monitoring target schemas
class MonitoringTargetBase(BaseModel):
    """Base schema for monitoring targets"""
    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    target_url: str = Field(..., min_length=1, max_length=500, description="URL or IP to monitor")
    target_type: Literal["http", "https", "ping", "dns"] = Field("http", description="Type of check")
    check_interval: int = Field(60, ge=10, le=3600, description="Check interval in seconds")
    timeout: int = Field(10, ge=1, le=60, description="Timeout in seconds")


class MonitoringTargetCreate(MonitoringTargetBase):
    """Schema for creating a monitoring target"""
    is_active: bool = Field(True, description="Whether monitoring is active")


class MonitoringTargetUpdate(BaseModel):
    """Schema for updating a monitoring target"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    target_url: Optional[str] = Field(None, min_length=1, max_length=500)
    target_type: Optional[Literal["http", "https", "ping", "dns"]] = None
    check_interval: Optional[int] = Field(None, ge=10, le=3600)
    timeout: Optional[int] = Field(None, ge=1, le=60)
    is_active: Optional[bool] = None


class MonitoringTargetResponse(MonitoringTargetBase):
    """Schema for monitoring target response"""
    id: int = Field(..., description="Target ID")
    is_active: bool = Field(..., description="Whether monitoring is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Monitoring result schemas
class MonitoringResultResponse(BaseModel):
    """Schema for monitoring result response"""
    id: int = Field(..., description="Result ID")
    target_id: int = Field(..., description="Target ID")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    response_time_ms: Optional[float] = Field(None, description="Response time in ms")
    is_up: bool = Field(..., description="Whether target is up")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    dns_resolution: Optional[str] = Field(None, description="DNS resolved IP")
    timestamp: datetime = Field(..., description="Check timestamp")

    class Config:
        from_attributes = True


class MonitoringResultListResponse(BaseModel):
    """Schema for monitoring results list"""
    results: List[MonitoringResultResponse] = Field(..., description="List of results")
    total: int = Field(..., ge=0, description="Total count")


class TargetWithLatestResult(BaseModel):
    """Schema for target with its latest result"""
    target: MonitoringTargetResponse
    latest_result: Optional[MonitoringResultResponse] = None
    uptime_percentage: Optional[float] = Field(None, description="Uptime percentage last 24h")


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

# System Metrics Snapshot schemas
class SystemMetricsSnapshotResponse(BaseModel):
    """Schema for system metrics snapshot response"""
    id: int = Field(..., description="Snapshot ID")
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used_mb: Optional[float] = Field(None, description="Memory used in MB")
    memory_total_mb: Optional[float] = Field(None, description="Total memory in MB")
    disk_percent: Optional[float] = Field(None, description="Disk usage percentage")
    disk_used_gb: Optional[float] = Field(None, description="Disk used in GB")
    disk_total_gb: Optional[float] = Field(None, description="Total disk in GB")
    bytes_sent: Optional[float] = Field(None, description="Total bytes sent")
    bytes_recv: Optional[float] = Field(None, description="Total bytes received")
    network_sent_rate: Optional[float] = Field(None, description="Network send rate (bytes/sec)")
    network_recv_rate: Optional[float] = Field(None, description="Network receive rate (bytes/sec)")
    timestamp: datetime = Field(..., description="Snapshot timestamp")

    class Config:
        from_attributes = True


class SystemMetricsSnapshotsListResponse(BaseModel):
    """Schema for metrics snapshots list"""
    snapshots: List[SystemMetricsSnapshotResponse] = Field(..., description="List of snapshots")
    total: int = Field(..., ge=0, description="Total count")


# Event schemas
class EventBase(BaseModel):
    """Base event schema"""
    event_type: str = Field(..., min_length=1, max_length=50, description="Event type")
    message: str = Field(..., min_length=1, max_length=1000, description="Event message")
    severity: Literal["info", "warning", "critical"] = Field(..., description="Event severity")
    source: Optional[str] = Field(None, max_length=50, description="Event source")
    metadata: Optional[str] = Field(None, description="Additional metadata as JSON")


class EventCreate(EventBase):
    """Schema for creating events"""
    pass


class EventResponse(EventBase):
    """Schema for event response"""
    id: int = Field(..., description="Event ID")
    is_resolved: bool = Field(..., description="Whether event is resolved")
    created_at: datetime = Field(..., description="Creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")

    class Config:
        from_attributes = True


class EventsListResponse(BaseModel):
    """Schema for events list response"""
    events: List[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., ge=0, description="Total count")


# Real-time system metrics (for /api/metrics/system endpoint)
class RealTimeSystemMetrics(BaseModel):
    """Schema for real-time system metrics"""
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    memory_used_mb: float = Field(..., description="Memory used in MB")
    memory_total_mb: float = Field(..., description="Total memory in MB")
    disk_percent: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    disk_used_gb: float = Field(..., description="Disk used in GB")
    disk_total_gb: float = Field(..., description="Total disk in GB")
    network_sent_rate: float = Field(..., ge=0, description="Network send rate (bytes/sec)")
    network_recv_rate: float = Field(..., ge=0, description="Network receive rate (bytes/sec)")
    timestamp: datetime = Field(..., description="Metrics timestamp")


# Health check response
class DetailedHealthResponse(BaseModel):
    """Schema for detailed health check"""
    status: Literal["healthy", "degraded", "critical"] = Field(..., description="Overall status")
    cpu: float = Field(..., description="Current CPU percentage")
    memory: float = Field(..., description="Current memory percentage")
    disk: float = Field(..., description="Current disk percentage")
    active_events: int = Field(..., ge=0, description="Number of active events")
    critical_events: int = Field(..., ge=0, description="Number of critical events")
    failing_services: int = Field(..., ge=0, description="Number of failing services")
    timestamp: datetime = Field(..., description="Check timestamp")

# Agent schemas
class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    hostname: Optional[str] = Field(None, max_length=100, description="Agent hostname")
    os_type: Optional[str] = Field(None, max_length=50, description="OS type")


class AgentCreate(AgentBase):
    """Schema for creating an agent"""
    pass


class AgentResponse(AgentBase):
    """Schema for agent response"""
    id: int = Field(..., description="Agent ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    status: str = Field(..., description="Agent status")
    api_key: str = Field(..., description="API key for agent")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat timestamp")
    is_active: bool = Field(..., description="Whether agent is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Schema for agent list response"""
    agents: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., ge=0, description="Total count")


class AgentMetricsBase(BaseModel):
    """Base agent metrics schema"""
    cpu_percent: Optional[float] = Field(None, ge=0, le=100)
    memory_percent: Optional[float] = Field(None, ge=0, le=100)
    memory_used_mb: Optional[float] = Field(None, ge=0)
    memory_total_mb: Optional[float] = Field(None, ge=0)
    disk_percent: Optional[float] = Field(None, ge=0, le=100)
    disk_used_gb: Optional[float] = Field(None, ge=0)
    disk_total_gb: Optional[float] = Field(None, ge=0)
    network_sent_rate: Optional[float] = Field(None, ge=0)
    network_recv_rate: Optional[float] = Field(None, ge=0)
    load_avg: Optional[float] = Field(None, ge=0)


class AgentMetricsSubmit(AgentMetricsBase):
    """Schema for agent to submit metrics"""
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os_type: Optional[str] = None


class AgentMetricsResponse(AgentMetricsBase):
    """Schema for agent metrics response"""
    id: int = Field(..., description="Metrics ID")
    agent_id: int = Field(..., description="Agent ID")
    timestamp: datetime = Field(..., description="Metrics timestamp")

    class Config:
        from_attributes = True


class AgentMetricsListResponse(BaseModel):
    """Schema for agent metrics list"""
    metrics: List[AgentMetricsResponse] = Field(..., description="List of metrics")
    total: int = Field(..., ge=0, description="Total count")


# Health scoring
class HealthScoreResponse(BaseModel):
    """Schema for health score response"""
    score: int = Field(..., ge=0, le=100, description="Health score 0-100")
    grade: str = Field(..., description="Letter grade A-F")
    factors: Dict[str, Any] = Field(..., description="Score factors breakdown")
    timestamp: datetime = Field(..., description="Score timestamp")