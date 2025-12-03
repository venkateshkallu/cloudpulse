"""
Logs API route handlers
Provides endpoints for log management and retrieval with filtering
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from typing import List, Optional

from ..database import get_db
from ..schemas import LogsListResponse, LogResponse, LogCreate, LogsQueryParams
from ..models import Log

router = APIRouter(prefix="/api/logs", tags=["logs"])


def generate_sample_logs(count: int = 50) -> List[dict]:
    """
    Generate sample log entries for demonstration
    In a real system, logs would come from actual application events
    """
    services = ["api-gateway", "user-service", "auth-service", "notification-service", "database", "redis-cache"]
    levels = ["info", "warning", "error"]
    level_weights = [0.7, 0.2, 0.1]  # 70% info, 20% warning, 10% error
    
    sample_messages = {
        "info": [
            "Request processed successfully",
            "User authentication completed",
            "Database connection established",
            "Cache hit for user data",
            "Background task completed",
            "Health check passed",
            "Configuration loaded",
            "Service started successfully"
        ],
        "warning": [
            "High memory usage detected",
            "Slow database query detected",
            "Rate limit approaching for user",
            "Cache miss rate increasing",
            "Connection pool nearly full",
            "Disk space running low",
            "Deprecated API endpoint used"
        ],
        "error": [
            "Database connection failed",
            "Authentication token expired",
            "Service unavailable",
            "Internal server error",
            "Failed to process request",
            "Connection timeout",
            "Invalid request format",
            "Permission denied"
        ]
    }
    
    logs = []
    base_time = datetime.utcnow()
    
    for i in range(count):
        # Generate timestamp (recent logs)
        minutes_ago = random.randint(0, 1440)  # Last 24 hours
        timestamp = base_time - timedelta(minutes=minutes_ago)
        
        # Select level based on weights
        level = random.choices(levels, weights=level_weights)[0]
        
        # Select service and message
        service = random.choice(services)
        message = random.choice(sample_messages[level])
        
        # Add some context to messages
        if "user" in message.lower():
            message += f" (user_id: {random.randint(1000, 9999)})"
        elif "request" in message.lower():
            message += f" (request_id: {random.randint(100000, 999999)})"
        
        logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "service_name": service
        })
    
    # Sort by timestamp (newest first)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return logs


@router.get("/", response_model=LogsListResponse)
async def get_logs(
    limit: int = Query(50, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    level: Optional[str] = Query(None, regex="^(info|warning|error)$", description="Filter by log level"),
    service: Optional[str] = Query(None, max_length=100, description="Filter by service name"),
    start_time: Optional[datetime] = Query(None, description="Filter logs after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter logs before this time"),
    db: Session = Depends(get_db)
):
    """
    Get logs with optional filtering
    Supports pagination and filtering by level, service, and time range
    """
    try:
        # Validate time range
        if start_time and end_time and end_time <= start_time:
            raise HTTPException(
                status_code=400,
                detail="end_time must be after start_time"
            )
        
        # Build query
        query = db.query(Log)
        
        # Apply filters
        if level:
            query = query.filter(Log.level == level)
            
        if service:
            query = query.filter(Log.service_name == service)
            
        if start_time:
            query = query.filter(Log.timestamp >= start_time)
            
        if end_time:
            query = query.filter(Log.timestamp <= end_time)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply ordering and pagination
        logs = query.order_by(Log.timestamp.desc()).offset(offset).limit(limit).all()
        
        # If no logs in database, return sample logs
        if not logs and offset == 0:
            sample_logs = generate_sample_logs(limit)
            
            # Apply filters to sample logs
            if level:
                sample_logs = [log for log in sample_logs if log["level"] == level]
            if service:
                sample_logs = [log for log in sample_logs if log["service_name"] == service]
            if start_time:
                sample_logs = [log for log in sample_logs if log["timestamp"] >= start_time]
            if end_time:
                sample_logs = [log for log in sample_logs if log["timestamp"] <= end_time]
            
            # Convert to response format
            log_responses = []
            for i, log in enumerate(sample_logs[:limit]):
                log_responses.append(LogResponse(
                    id=i + 1,
                    timestamp=log["timestamp"],
                    level=log["level"],
                    message=log["message"],
                    service_name=log["service_name"],
                    created_at=log["timestamp"]
                ))
            
            return LogsListResponse(
                logs=log_responses,
                total=len(sample_logs),
                limit=limit,
                offset=offset
            )
        
        return LogsListResponse(
            logs=[LogResponse.from_orm(log) for log in logs],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve logs: {str(e)}"
        )


@router.post("/", response_model=LogResponse)
async def create_log(log: LogCreate, db: Session = Depends(get_db)):
    """
    Create a new log entry
    Adds a log entry to the system
    """
    try:
        db_log = Log(
            timestamp=log.timestamp or datetime.utcnow(),
            level=log.level,
            message=log.message,
            service_name=log.service_name
        )
        
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        return LogResponse.from_orm(db_log)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create log entry: {str(e)}"
        )


@router.get("/levels")
async def get_log_levels():
    """
    Get available log levels
    Returns the list of supported log levels
    """
    return {
        "levels": ["info", "warning", "error"],
        "descriptions": {
            "info": "Informational messages about normal operations",
            "warning": "Warning messages about potential issues",
            "error": "Error messages about failures and problems"
        }
    }


@router.get("/services")
async def get_log_services(db: Session = Depends(get_db)):
    """
    Get list of services that have logged entries
    Returns unique service names from log entries
    """
    try:
        # Get distinct service names from logs
        services = db.query(Log.service_name).distinct().all()
        service_names = [service[0] for service in services]
        
        # If no services in database, return default services
        if not service_names:
            service_names = ["api-gateway", "user-service", "auth-service", 
                           "notification-service", "database", "redis-cache"]
        
        return {"services": sorted(service_names)}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log services: {str(e)}"
        )


@router.get("/stats")
async def get_log_stats(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get log statistics for the specified time period
    Returns counts by level and service
    """
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Query logs in time range
        logs_query = db.query(Log).filter(
            Log.timestamp >= start_time,
            Log.timestamp <= end_time
        )
        
        total_logs = logs_query.count()
        
        if total_logs == 0:
            # Return simulated stats if no logs in database
            return {
                "period_hours": hours,
                "start_time": start_time,
                "end_time": end_time,
                "total_logs": random.randint(100, 500),
                "by_level": {
                    "info": random.randint(70, 350),
                    "warning": random.randint(15, 100),
                    "error": random.randint(5, 50)
                },
                "by_service": {
                    "api-gateway": random.randint(20, 100),
                    "user-service": random.randint(15, 80),
                    "auth-service": random.randint(10, 60),
                    "notification-service": random.randint(5, 40),
                    "database": random.randint(8, 50),
                    "redis-cache": random.randint(3, 30)
                }
            }
        
        # Count by level
        level_counts = {}
        for level in ["info", "warning", "error"]:
            count = logs_query.filter(Log.level == level).count()
            level_counts[level] = count
        
        # Count by service
        service_counts = {}
        services = db.query(Log.service_name).distinct().all()
        for service in services:
            service_name = service[0]
            count = logs_query.filter(Log.service_name == service_name).count()
            service_counts[service_name] = count
        
        return {
            "period_hours": hours,
            "start_time": start_time,
            "end_time": end_time,
            "total_logs": total_logs,
            "by_level": level_counts,
            "by_service": service_counts
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log statistics: {str(e)}"
        )


@router.delete("/")
async def clear_logs(
    older_than_hours: int = Query(168, ge=1, description="Delete logs older than this many hours"),
    db: Session = Depends(get_db)
):
    """
    Clear old log entries
    Deletes logs older than the specified time period
    """
    try:
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        # Delete old logs
        deleted_count = db.query(Log).filter(Log.timestamp < cutoff_time).delete()
        db.commit()
        
        return {
            "deleted_count": deleted_count,
            "cutoff_time": cutoff_time,
            "message": f"Deleted {deleted_count} log entries older than {older_than_hours} hours"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear logs: {str(e)}"
        )