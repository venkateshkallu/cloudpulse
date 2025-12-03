"""
Status API route handlers
Provides endpoints for overall system status and health monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from typing import Dict, Any

from ..database import get_db
from ..schemas import SystemStatus
from ..models import Service, Log

router = APIRouter(prefix="/api/status", tags=["status"])


def calculate_system_health(services_data: list, recent_errors: int) -> tuple[str, float]:
    """
    Calculate overall system health based on service status and recent errors
    Returns (status_string, health_score)
    """
    if not services_data:
        return "warning", 50.0
    
    # Count services by status
    online_count = sum(1 for svc in services_data if svc.get("status") == "online")
    degraded_count = sum(1 for svc in services_data if svc.get("status") == "degraded")
    offline_count = sum(1 for svc in services_data if svc.get("status") == "offline")
    total_services = len(services_data)
    
    # Calculate base health score from service status
    service_health = (online_count * 100 + degraded_count * 50) / total_services
    
    # Reduce health based on recent errors
    error_penalty = min(recent_errors * 2, 30)  # Max 30 point penalty
    health_score = max(0, service_health - error_penalty)
    
    # Determine status based on health score and critical services
    if offline_count > 0 or health_score < 50:
        status = "critical"
    elif degraded_count > 0 or health_score < 80 or recent_errors > 10:
        status = "warning"
    else:
        status = "healthy"
    
    return status, round(health_score, 1)


def get_default_services_status() -> list:
    """
    Get default services status for simulation
    """
    services = [
        {"id": "api-gateway", "name": "API Gateway", "status": "online"},
        {"id": "user-service", "name": "User Service", "status": "online"},
        {"id": "auth-service", "name": "Authentication Service", "status": "online"},
        {"id": "notification-service", "name": "Notification Service", "status": "online"},
        {"id": "database", "name": "PostgreSQL Database", "status": "online"},
        {"id": "redis-cache", "name": "Redis Cache", "status": "online"}
    ]
    
    # Simulate occasional service issues
    for service in services:
        random_factor = random.random()
        if random_factor < 0.05:  # 5% chance of being offline
            service["status"] = "offline"
        elif random_factor < 0.15:  # 10% chance of being degraded
            service["status"] = "degraded"
    
    return services


@router.get("/", response_model=SystemStatus)
async def get_system_status(db: Session = Depends(get_db)):
    """
    Get overall system status
    Returns aggregated health information for all monitored services
    """
    try:
        # Get services status
        services = db.query(Service).all()
        
        if not services:
            # Use default services if none in database
            services_data = get_default_services_status()
        else:
            services_data = [
                {
                    "id": svc.id,
                    "name": svc.name,
                    "status": svc.status
                }
                for svc in services
            ]
        
        # Count services by status
        services_online = sum(1 for svc in services_data if svc["status"] == "online")
        services_total = len(services_data)
        
        # Count recent critical errors (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_errors = db.query(Log).filter(
            Log.level == "error",
            Log.timestamp >= one_hour_ago
        ).count()
        
        # If no logs in database, simulate error count
        if recent_errors == 0 and not db.query(Log).first():
            recent_errors = random.randint(0, 5)
        
        # Calculate overall system health
        overall_status, health_score = calculate_system_health(services_data, recent_errors)
        
        return SystemStatus(
            overall_status=overall_status,
            services_online=services_online,
            services_total=services_total,
            critical_alerts=recent_errors,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system status: {str(e)}"
        )


@router.get("/health")
async def get_health_check():
    """
    Simple health check endpoint
    Returns basic service availability information
    """
    try:
        return {
            "status": "healthy",
            "service": "cloudpulse-api",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "uptime_seconds": random.randint(3600, 86400)  # Simulated uptime
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/detailed")
async def get_detailed_status(db: Session = Depends(get_db)):
    """
    Get detailed system status with component breakdown
    Returns comprehensive health information for all system components
    """
    try:
        # Get services status
        services = db.query(Service).all()
        
        if not services:
            services_data = get_default_services_status()
        else:
            services_data = [
                {
                    "id": svc.id,
                    "name": svc.name,
                    "status": svc.status,
                    "uptime": float(svc.uptime),
                    "last_checked": svc.last_checked
                }
                for svc in services
            ]
        
        # Get recent log statistics
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        recent_logs = {
            "last_hour": {
                "total": 0,
                "errors": 0,
                "warnings": 0
            },
            "last_24_hours": {
                "total": 0,
                "errors": 0,
                "warnings": 0
            }
        }
        
        # Query actual logs if available
        if db.query(Log).first():
            # Last hour
            recent_logs["last_hour"]["total"] = db.query(Log).filter(Log.timestamp >= one_hour_ago).count()
            recent_logs["last_hour"]["errors"] = db.query(Log).filter(
                Log.timestamp >= one_hour_ago, Log.level == "error"
            ).count()
            recent_logs["last_hour"]["warnings"] = db.query(Log).filter(
                Log.timestamp >= one_hour_ago, Log.level == "warning"
            ).count()
            
            # Last 24 hours
            recent_logs["last_24_hours"]["total"] = db.query(Log).filter(Log.timestamp >= twenty_four_hours_ago).count()
            recent_logs["last_24_hours"]["errors"] = db.query(Log).filter(
                Log.timestamp >= twenty_four_hours_ago, Log.level == "error"
            ).count()
            recent_logs["last_24_hours"]["warnings"] = db.query(Log).filter(
                Log.timestamp >= twenty_four_hours_ago, Log.level == "warning"
            ).count()
        else:
            # Simulate log statistics
            recent_logs["last_hour"] = {
                "total": random.randint(10, 50),
                "errors": random.randint(0, 5),
                "warnings": random.randint(1, 10)
            }
            recent_logs["last_24_hours"] = {
                "total": random.randint(200, 1000),
                "errors": random.randint(5, 30),
                "warnings": random.randint(20, 100)
            }
        
        # Calculate system metrics
        services_online = sum(1 for svc in services_data if svc["status"] == "online")
        services_degraded = sum(1 for svc in services_data if svc["status"] == "degraded")
        services_offline = sum(1 for svc in services_data if svc["status"] == "offline")
        services_total = len(services_data)
        
        # Calculate overall health
        overall_status, health_score = calculate_system_health(
            services_data, 
            recent_logs["last_hour"]["errors"]
        )
        
        # System performance metrics (simulated)
        performance_metrics = {
            "cpu_usage": round(random.uniform(20, 80), 1),
            "memory_usage": round(random.uniform(30, 85), 1),
            "disk_usage": round(random.uniform(40, 90), 1),
            "network_latency_ms": round(random.uniform(10, 100), 2),
            "active_connections": random.randint(50, 500)
        }
        
        return {
            "overall_status": overall_status,
            "health_score": health_score,
            "last_updated": datetime.utcnow(),
            "services": {
                "total": services_total,
                "online": services_online,
                "degraded": services_degraded,
                "offline": services_offline,
                "details": services_data
            },
            "logs": recent_logs,
            "performance": performance_metrics,
            "alerts": {
                "critical": recent_logs["last_hour"]["errors"],
                "warning": recent_logs["last_hour"]["warnings"],
                "total_active": recent_logs["last_hour"]["errors"] + recent_logs["last_hour"]["warnings"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve detailed status: {str(e)}"
        )


@router.get("/uptime")
async def get_system_uptime():
    """
    Get system uptime information
    Returns uptime statistics and availability metrics
    """
    try:
        # Simulate uptime data
        current_uptime_seconds = random.randint(86400, 2592000)  # 1 day to 30 days
        current_uptime_hours = current_uptime_seconds / 3600
        
        # Calculate uptime percentage (simulate high availability)
        uptime_percentage = random.uniform(99.5, 99.99)
        
        return {
            "current_uptime": {
                "seconds": current_uptime_seconds,
                "hours": round(current_uptime_hours, 2),
                "days": round(current_uptime_hours / 24, 2)
            },
            "availability": {
                "last_30_days": round(uptime_percentage, 2),
                "last_7_days": round(min(uptime_percentage + random.uniform(0, 0.5), 100), 2),
                "last_24_hours": round(min(uptime_percentage + random.uniform(0, 1), 100), 2)
            },
            "last_restart": datetime.utcnow() - timedelta(seconds=current_uptime_seconds),
            "restart_reason": "Scheduled maintenance" if random.random() < 0.3 else "System update"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve uptime information: {str(e)}"
        )