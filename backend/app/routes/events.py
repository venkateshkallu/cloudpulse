"""
Events API route handlers
Provides endpoints for viewing and managing events/alerts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from ..database import get_db
from ..schemas import EventResponse, EventsListResponse, EventCreate
from ..models import Event

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=EventsListResponse)
async def get_events(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    unresolved_only: bool = Query(False, description="Show only unresolved events"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering"""
    query = db.query(Event)
    
    if severity:
        query = query.filter(Event.severity == severity)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if unresolved_only:
        query = query.filter(Event.is_resolved == 0)
    
    total = query.count()
    events = query.order_by(Event.created_at.desc()).limit(limit).all()
    
    return EventsListResponse(
        events=[EventResponse(
            id=e.id,
            event_type=e.event_type,
            message=e.message,
            severity=e.severity,
            source=e.source,
            metadata=e.metadata,
            is_resolved=e.is_resolved == 1,
            created_at=e.created_at,
            resolved_at=e.resolved_at
        ) for e in events],
        total=total
    )


@router.get("/recent", response_model=EventsListResponse)
async def get_recent_events(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get recent events within specified hours"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    events = db.query(Event).filter(
        Event.created_at >= start_time
    ).order_by(Event.created_at.desc()).limit(limit).all()
    
    return EventsListResponse(
        events=[EventResponse(
            id=e.id,
            event_type=e.event_type,
            message=e.message,
            severity=e.severity,
            source=e.source,
            metadata=e.metadata,
            is_resolved=e.is_resolved == 1,
            created_at=e.created_at,
            resolved_at=e.resolved_at
        ) for e in events],
        total=len(events)
    )


@router.get("/counts")
async def get_event_counts(db: Session = Depends(get_db)):
    """Get event counts by severity and type"""
    from sqlalchemy import func
    
    # Total counts
    total = db.query(Event).count()
    unresolved = db.query(Event).filter(Event.is_resolved == 0).count()
    
    # By severity
    severity_counts = db.query(
        Event.severity,
        func.count(Event.id)
    ).group_by(Event.severity).all()
    
    severity_dict = {s[0]: s[1] for s in severity_counts}
    
    # By type
    type_counts = db.query(
        Event.event_type,
        func.count(Event.id)
    ).group_by(Event.event_type).all()
    
    type_dict = {t[0]: t[1] for t in type_counts}
    
    return {
        "total": total,
        "unresolved": unresolved,
        "by_severity": severity_dict,
        "by_type": type_dict
    }


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return EventResponse(
        id=event.id,
        event_type=event.event_type,
        message=event.message,
        severity=event.severity,
        source=event.source,
        metadata=event.metadata,
        is_resolved=event.is_resolved == 1,
        created_at=event.created_at,
        resolved_at=event.resolved_at
    )


@router.post("/{event_id}/resolve")
async def resolve_event(event_id: int, db: Session = Depends(get_db)):
    """Mark an event as resolved"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.is_resolved = 1
    event.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    
    return {"message": "Event resolved", "event_id": event_id}


@router.post("/resolve-all")
async def resolve_all_events(db: Session = Depends(get_db)):
    """Mark all unresolved events as resolved"""
    db.query(Event).filter(Event.is_resolved == 0).update({
        Event.is_resolved: 1,
        Event.resolved_at: datetime.utcnow()
    })
    db.commit()
    
    return {"message": "All events resolved"}


@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted"}