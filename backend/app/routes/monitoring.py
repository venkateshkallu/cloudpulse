"""
Monitoring API route handlers for external endpoint monitoring
Provides endpoints for managing monitoring targets and viewing results
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import httpx
import socket
import asyncio

from ..database import get_db
from ..schemas import (
    MonitoringTargetCreate, MonitoringTargetUpdate, MonitoringTargetResponse,
    MonitoringResultResponse, MonitoringResultListResponse, TargetWithLatestResult
)
from ..models import MonitoringTarget, MonitoringResult

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


async def check_http_target(target: MonitoringTarget) -> dict:
    """Check HTTP/HTTPS endpoint availability"""
    try:
        async with httpx.AsyncClient(timeout=target.timeout) as client:
            start_time = datetime.utcnow()
            response = await client.get(target.target_url, follow_redirects=True)
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "is_up": 1 if response.status_code < 500 else 0,
                "error_message": None,
                "dns_resolution": None
            }
    except httpx.TimeoutException:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": "Request timeout",
            "dns_resolution": None
        }
    except httpx.RequestError as e:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": str(e),
            "dns_resolution": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": str(e),
            "dns_resolution": None
        }


async def check_ping_target(target: MonitoringTarget) -> dict:
    """Check ICMP ping availability (simulated via socket connect)"""
    try:
        # Extract host from URL
        url = target.target_url
        if "://" in url:
            host = url.split("://")[1].split("/")[0].split(":")[0]
        else:
            host = url.split("/")[0].split(":")[0]
        
        # Try to resolve DNS
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            return {
                "status_code": None,
                "response_time_ms": None,
                "is_up": 0,
                "error_message": f"DNS resolution failed for {host}",
                "dns_resolution": None
            }
        
        # Try TCP connection to common ports (80, 443, 22)
        start_time = datetime.utcnow()
        ports = [80, 443, 22]
        connected = False
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(target.timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    connected = True
                    break
            except:
                continue
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "status_code": 200 if connected else None,
            "response_time_ms": round(response_time, 2) if connected else None,
            "is_up": 1 if connected else 0,
            "error_message": None if connected else "No open ports found",
            "dns_resolution": ip
        }
    except Exception as e:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": str(e),
            "dns_resolution": None
        }


async def check_dns_target(target: MonitoringTarget) -> dict:
    """Check DNS resolution"""
    try:
        # Extract domain from URL
        url = target.target_url
        if "://" in url:
            domain = url.split("://")[1].split("/")[0]
        else:
            domain = url.split("/")[0]
        
        start_time = datetime.utcnow()
        ip = socket.gethostbyname(domain)
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "status_code": 200,
            "response_time_ms": round(response_time, 2),
            "is_up": 1,
            "error_message": None,
            "dns_resolution": ip
        }
    except socket.gaierror as e:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": f"DNS resolution failed: {e}",
            "dns_resolution": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": str(e),
            "dns_resolution": None
        }


async def check_target(target: MonitoringTarget) -> dict:
    """Route to appropriate check function based on target type"""
    if target.target_type in ("http", "https"):
        return await check_http_target(target)
    elif target.target_type == "ping":
        return await check_ping_target(target)
    elif target.target_type == "dns":
        return await check_dns_target(target)
    else:
        return {
            "status_code": None,
            "response_time_ms": None,
            "is_up": 0,
            "error_message": f"Unknown target type: {target.target_type}",
            "dns_resolution": None
        }


# Target CRUD endpoints
@router.post("/targets", response_model=MonitoringTargetResponse)
async def create_target(target: MonitoringTargetCreate, db: Session = Depends(get_db)):
    """Create a new monitoring target"""
    db_target = MonitoringTarget(
        name=target.name,
        target_url=target.target_url,
        target_type=target.target_type,
        check_interval=target.check_interval,
        timeout=target.timeout,
        is_active=1 if target.is_active else 0
    )
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    
    # Run initial check
    result = await check_target(db_target)
    db_result = MonitoringResult(
        target_id=db_target.id,
        status_code=result["status_code"],
        response_time_ms=result["response_time_ms"],
        is_up=result["is_up"],
        error_message=result["error_message"],
        dns_resolution=result["dns_resolution"]
    )
    db.add(db_result)
    db.commit()
    
    return MonitoringTargetResponse(
        id=db_target.id,
        name=db_target.name,
        target_url=db_target.target_url,
        target_type=db_target.target_type,
        check_interval=db_target.check_interval,
        timeout=db_target.timeout,
        is_active=db_target.is_active == 1,
        created_at=db_target.created_at,
        updated_at=db_target.updated_at
    )


@router.get("/targets", response_model=List[MonitoringTargetResponse])
async def get_targets(
    active_only: bool = Query(False, description="Show only active targets"),
    db: Session = Depends(get_db)
):
    """Get all monitoring targets"""
    query = db.query(MonitoringTarget)
    if active_only:
        query = query.filter(MonitoringTarget.is_active == 1)
    
    targets = query.order_by(MonitoringTarget.created_at.desc()).all()
    
    return [
        MonitoringTargetResponse(
            id=t.id,
            name=t.name,
            target_url=t.target_url,
            target_type=t.target_type,
            check_interval=t.check_interval,
            timeout=t.timeout,
            is_active=t.is_active == 1,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in targets
    ]


@router.get("/targets/with-results", response_model=List[TargetWithLatestResult])
async def get_targets_with_results(db: Session = Depends(get_db)):
    """Get all targets with their latest results and uptime"""
    targets = db.query(MonitoringTarget).filter(MonitoringTarget.is_active == 1).all()
    
    result_list = []
    for target in targets:
        # Get latest result
        latest = db.query(MonitoringResult).filter(
            MonitoringResult.target_id == target.id
        ).order_by(MonitoringResult.timestamp.desc()).first()
        
        # Calculate uptime for last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)
        results_24h = db.query(MonitoringResult).filter(
            MonitoringResult.target_id == target.id,
            MonitoringResult.timestamp >= yesterday
        ).all()
        
        uptime = None
        if results_24h:
            up_count = sum(1 for r in results_24h if r.is_up == 1)
            uptime = round((up_count / len(results_24h)) * 100, 2)
        
        result_list.append(TargetWithLatestResult(
            target=MonitoringTargetResponse(
                id=target.id,
                name=target.name,
                target_url=target.target_url,
                target_type=target.target_type,
                check_interval=target.check_interval,
                timeout=target.timeout,
                is_active=target.is_active == 1,
                created_at=target.created_at,
                updated_at=target.updated_at
            ),
            latest_result=MonitoringResultResponse(
                id=latest.id,
                target_id=latest.target_id,
                status_code=latest.status_code,
                response_time_ms=float(latest.response_time_ms) if latest.response_time_ms else None,
                is_up=latest.is_up == 1,
                error_message=latest.error_message,
                dns_resolution=latest.dns_resolution,
                timestamp=latest.timestamp
            ) if latest else None,
            uptime_percentage=uptime
        ))
    
    return result_list


@router.get("/targets/{target_id}", response_model=MonitoringTargetResponse)
async def get_target(target_id: int, db: Session = Depends(get_db)):
    """Get a specific monitoring target"""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    return MonitoringTargetResponse(
        id=target.id,
        name=target.name,
        target_url=target.target_url,
        target_type=target.target_type,
        check_interval=target.check_interval,
        timeout=target.timeout,
        is_active=target.is_active == 1,
        created_at=target.created_at,
        updated_at=target.updated_at
    )


@router.put("/targets/{target_id}", response_model=MonitoringTargetResponse)
async def update_target(
    target_id: int,
    target_update: MonitoringTargetUpdate,
    db: Session = Depends(get_db)
):
    """Update a monitoring target"""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    if target_update.name is not None:
        target.name = target_update.name
    if target_update.target_url is not None:
        target.target_url = target_update.target_url
    if target_update.target_type is not None:
        target.target_type = target_update.target_type
    if target_update.check_interval is not None:
        target.check_interval = target_update.check_interval
    if target_update.timeout is not None:
        target.timeout = target_update.timeout
    if target_update.is_active is not None:
        target.is_active = 1 if target_update.is_active else 0
    
    db.commit()
    db.refresh(target)
    
    return MonitoringTargetResponse(
        id=target.id,
        name=target.name,
        target_url=target.target_url,
        target_type=target.target_type,
        check_interval=target.check_interval,
        timeout=target.timeout,
        is_active=target.is_active == 1,
        created_at=target.created_at,
        updated_at=target.updated_at
    )


@router.delete("/targets/{target_id}")
async def delete_target(target_id: int, db: Session = Depends(get_db)):
    """Delete a monitoring target and its results"""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Delete associated results first
    db.query(MonitoringResult).filter(MonitoringResult.target_id == target_id).delete()
    db.delete(target)
    db.commit()
    
    return {"message": "Target deleted successfully"}


@router.post("/targets/{target_id}/check")
async def trigger_check(target_id: int, db: Session = Depends(get_db)):
    """Manually trigger a check for a specific target"""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    result = await check_target(target)
    
    db_result = MonitoringResult(
        target_id=target.id,
        status_code=result["status_code"],
        response_time_ms=result["response_time_ms"],
        is_up=result["is_up"],
        error_message=result["error_message"],
        dns_resolution=result["dns_resolution"]
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return MonitoringResultResponse(
        id=db_result.id,
        target_id=db_result.target_id,
        status_code=db_result.status_code,
        response_time_ms=float(db_result.response_time_ms) if db_result.response_time_ms else None,
        is_up=db_result.is_up == 1,
        error_message=db_result.error_message,
        dns_resolution=db_result.dns_resolution,
        timestamp=db_result.timestamp
    )


# Results endpoints
@router.get("/results", response_model=MonitoringResultListResponse)
async def get_results(
    target_id: Optional[int] = Query(None, description="Filter by target ID"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get monitoring results with optional filtering"""
    query = db.query(MonitoringResult)
    
    if target_id:
        query = query.filter(MonitoringResult.target_id == target_id)
    
    total = query.count()
    results = query.order_by(MonitoringResult.timestamp.desc()).limit(limit).all()
    
    return MonitoringResultListResponse(
        results=[
            MonitoringResultResponse(
                id=r.id,
                target_id=r.target_id,
                status_code=r.status_code,
                response_time_ms=float(r.response_time_ms) if r.response_time_ms else None,
                is_up=r.is_up == 1,
                error_message=r.error_message,
                dns_resolution=r.dns_resolution,
                timestamp=r.timestamp
            )
            for r in results
        ],
        total=total
    )


@router.get("/targets/{target_id}/results", response_model=MonitoringResultListResponse)
async def get_target_results(
    target_id: int,
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get results for a specific target"""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    results = db.query(MonitoringResult).filter(
        MonitoringResult.target_id == target_id
    ).order_by(MonitoringResult.timestamp.desc()).limit(limit).all()
    
    return MonitoringResultListResponse(
        results=[
            MonitoringResultResponse(
                id=r.id,
                target_id=r.target_id,
                status_code=r.status_code,
                response_time_ms=float(r.response_time_ms) if r.response_time_ms else None,
                is_up=r.is_up == 1,
                error_message=r.error_message,
                dns_resolution=r.dns_resolution,
                timestamp=r.timestamp
            )
            for r in results
        ],
        total=len(results)
    )