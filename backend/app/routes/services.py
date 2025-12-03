"""
Services API route handlers
Provides endpoints for service monitoring and status management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
from typing import List

from ..database import get_db
from ..schemas import ServiceResponse, ServiceCreate, ServiceUpdate
from ..models import Service

router = APIRouter(prefix="/api/services", tags=["services"])


def get_default_services() -> List[dict]:
    """
    Get default services with simulated status
    In a real system, this would check actual service health
    """
    services = [
        {
            "id": "api-gateway",
            "name": "API Gateway",
            "base_uptime": 99.8
        },
        {
            "id": "user-service",
            "name": "User Service",
            "base_uptime": 99.5
        },
        {
            "id": "auth-service",
            "name": "Authentication Service",
            "base_uptime": 99.9
        },
        {
            "id": "notification-service",
            "name": "Notification Service",
            "base_uptime": 98.7
        },
        {
            "id": "database",
            "name": "PostgreSQL Database",
            "base_uptime": 99.95
        },
        {
            "id": "redis-cache",
            "name": "Redis Cache",
            "base_uptime": 99.2
        }
    ]
    
    # Simulate realistic service status
    for service in services:
        # Occasionally simulate service issues
        random_factor = random.random()
        
        if random_factor < 0.05:  # 5% chance of being offline
            service["status"] = "offline"
            service["uptime"] = max(0, service["base_uptime"] - random.uniform(5, 20))
        elif random_factor < 0.15:  # 10% chance of being degraded
            service["status"] = "degraded"
            service["uptime"] = max(0, service["base_uptime"] - random.uniform(1, 5))
        else:  # 85% chance of being online
            service["status"] = "online"
            service["uptime"] = min(100, service["base_uptime"] + random.uniform(0, 0.2))
        
        service["uptime"] = round(service["uptime"], 2)
        service["last_checked"] = datetime.utcnow()
    
    return services


@router.get("/", response_model=List[ServiceResponse])
async def get_services(db: Session = Depends(get_db)):
    """
    Get all monitored services with their current status
    Returns service health, uptime, and last check information
    """
    try:
        # Try to get services from database
        db_services = db.query(Service).all()
        
        if not db_services:
            # If no services in database, return default simulated services
            default_services = get_default_services()
            return [
                ServiceResponse(
                    id=svc["id"],
                    name=svc["name"],
                    status=svc["status"],
                    uptime=svc["uptime"],
                    last_checked=svc["last_checked"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                for svc in default_services
            ]
        
        # Update service status with simulation
        updated_services = []
        for service in db_services:
            # Simulate status changes
            random_factor = random.random()
            
            if random_factor < 0.05:  # 5% chance of status change
                if service.status == "online":
                    service.status = "degraded" if random.random() < 0.7 else "offline"
                elif service.status == "degraded":
                    service.status = "online" if random.random() < 0.6 else "offline"
                elif service.status == "offline":
                    service.status = "degraded" if random.random() < 0.8 else "online"
            
            # Update uptime based on status
            if service.status == "online":
                service.uptime = min(100, float(service.uptime) + random.uniform(0, 0.1))
            elif service.status == "degraded":
                service.uptime = max(0, float(service.uptime) - random.uniform(0, 0.5))
            else:  # offline
                service.uptime = max(0, float(service.uptime) - random.uniform(1, 5))
            
            service.uptime = round(float(service.uptime), 2)
            service.last_checked = datetime.utcnow()
            
            updated_services.append(service)
        
        # Commit changes to database
        db.commit()
        
        return [ServiceResponse.from_orm(service) for service in updated_services]
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve services: {str(e)}"
        )


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str, db: Session = Depends(get_db)):
    """
    Get a specific service by ID
    Returns detailed information about a single service
    """
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            # If service not found in database, check if it's a default service
            default_services = get_default_services()
            default_service = next((svc for svc in default_services if svc["id"] == service_id), None)
            
            if not default_service:
                raise HTTPException(
                    status_code=404,
                    detail=f"Service with id '{service_id}' not found"
                )
            
            return ServiceResponse(
                id=default_service["id"],
                name=default_service["name"],
                status=default_service["status"],
                uptime=default_service["uptime"],
                last_checked=default_service["last_checked"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        return ServiceResponse.from_orm(service)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve service: {str(e)}"
        )


@router.post("/", response_model=ServiceResponse)
async def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """
    Create a new service for monitoring
    Adds a new service to the monitoring system
    """
    try:
        # Check if service already exists
        existing_service = db.query(Service).filter(Service.id == service.id).first()
        if existing_service:
            raise HTTPException(
                status_code=400,
                detail=f"Service with id '{service.id}' already exists"
            )
        
        # Create new service
        db_service = Service(
            id=service.id,
            name=service.name,
            status=service.status,
            uptime=service.uptime,
            last_checked=datetime.utcnow()
        )
        
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        
        return ServiceResponse.from_orm(db_service)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create service: {str(e)}"
        )


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str, 
    service_update: ServiceUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing service
    Modifies service configuration and status
    """
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with id '{service_id}' not found"
            )
        
        # Update fields if provided
        if service_update.name is not None:
            service.name = service_update.name
        if service_update.status is not None:
            service.status = service_update.status
        if service_update.uptime is not None:
            service.uptime = service_update.uptime
        
        service.last_checked = datetime.utcnow()
        
        db.commit()
        db.refresh(service)
        
        return ServiceResponse.from_orm(service)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update service: {str(e)}"
        )


@router.get("/{service_id}/health")
async def check_service_health(service_id: str, db: Session = Depends(get_db)):
    """
    Perform a health check on a specific service
    Returns detailed health information and response time
    """
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with id '{service_id}' not found"
            )
        
        # Simulate health check
        response_time = random.uniform(10, 500)  # 10-500ms
        is_healthy = service.status == "online"
        
        # Simulate occasional health check failures
        if random.random() < 0.1:  # 10% chance of health check failure
            is_healthy = False
            response_time = 5000  # Timeout
        
        health_status = {
            "service_id": service_id,
            "service_name": service.name,
            "is_healthy": is_healthy,
            "status": service.status,
            "response_time_ms": round(response_time, 2),
            "uptime": float(service.uptime),
            "last_checked": datetime.utcnow(),
            "details": {
                "endpoint_reachable": is_healthy,
                "database_connected": is_healthy and random.random() > 0.05,
                "memory_usage": round(random.uniform(30, 80), 1),
                "cpu_usage": round(random.uniform(10, 60), 1)
            }
        }
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check service health: {str(e)}"
        )