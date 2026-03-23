"""
Agents API route handlers
Provides endpoints for remote agent registration and metrics collection
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from ..database import get_db
from ..schemas import (
    AgentCreate, AgentResponse, AgentListResponse,
    AgentMetricsSubmit, AgentMetricsResponse, AgentMetricsListResponse
)
from ..models import Agent, AgentMetrics, Event

router = APIRouter(prefix="/api/agents", tags=["agents"])


def verify_api_key(api_key: str, db: Session) -> Optional[Agent]:
    """Verify API key and return agent if valid"""
    return db.query(Agent).filter(Agent.api_key == api_key, Agent.is_active == 1).first()


def get_agent_from_header(api_key: str = Header(...), db: Session = Depends(get_db)) -> Agent:
    """Dependency to get agent from API key header"""
    agent = verify_api_key(api_key, db)
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return agent


@router.post("/register", response_model=AgentResponse)
async def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """
    Register a new agent
    Returns API key that agent will use for authentication
    """
    # Generate unique API key
    api_key = secrets.token_hex(32)
    
    db_agent = Agent(
        name=agent_data.name,
        hostname=agent_data.hostname,
        ip_address=agent_data.ip_address,
        os_type=agent_data.os_type,
        api_key=api_key,
        status="online",
        last_heartbeat=datetime.utcnow()
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return AgentResponse(
        id=db_agent.id,
        name=db_agent.name,
        hostname=db_agent.hostname,
        ip_address=db_agent.ip_address,
        os_type=db_agent.os_type,
        status=db_agent.status,
        api_key=api_key,  # Only returned on creation
        last_heartbeat=db_agent.last_heartbeat,
        is_active=db_agent.is_active == 1,
        created_at=db_agent.created_at,
        updated_at=db_agent.updated_at
    )


@router.get("", response_model=AgentListResponse)
async def get_agents(
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all registered agents"""
    query = db.query(Agent)
    if active_only:
        query = query.filter(Agent.is_active == 1)
    
    agents = query.order_by(Agent.created_at.desc()).all()
    
    return AgentListResponse(
        agents=[AgentResponse(
            id=a.id,
            name=a.name,
            hostname=a.hostname,
            ip_address=a.ip_address,
            os_type=a.os_type,
            status=a.status,
            api_key="***",  # Hide API key in list
            last_heartbeat=a.last_heartbeat,
            is_active=a.is_active == 1,
            created_at=a.created_at,
            updated_at=a.updated_at
        ) for a in agents],
        total=len(agents)
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get specific agent details"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        hostname=agent.hostname,
        ip_address=agent.ip_address,
        os_type=agent.os_type,
        status=agent.status,
        api_key="***",
        last_heartbeat=agent.last_heartbeat,
        is_active=agent.is_active == 1,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )


@router.post("/heartbeat")
async def agent_heartbeat(
    agent: Agent = Depends(get_agent_from_header),
    db: Session = Depends(get_db)
):
    """Agent sends heartbeat to indicate it's alive"""
    agent.last_heartbeat = datetime.utcnow()
    agent.status = "online"
    db.commit()
    
    return {"status": "ok", "message": "Heartbeat received"}


@router.post("/{agent_id}/metrics")
async def submit_agent_metrics(
    agent_id: int,
    metrics: AgentMetricsSubmit,
    agent: Agent = Depends(get_agent_from_header),
    db: Session = Depends(get_db)
):
    """Agent submits metrics data"""
    # Verify agent owns this ID
    if agent.id != agent_id:
        raise HTTPException(status_code=403, detail="Agent ID mismatch")
    
    # Update agent info if provided
    if metrics.hostname:
        agent.hostname = metrics.hostname
    if metrics.ip_address:
        agent.ip_address = metrics.ip_address
    if metrics.os_type:
        agent.os_type = metrics.os_type
    agent.last_heartbeat = datetime.utcnow()
    agent.status = "online"
    
    # Store metrics
    db_metrics = AgentMetrics(
        agent_id=agent_id,
        cpu_percent=metrics.cpu_percent,
        memory_percent=metrics.memory_percent,
        memory_used_mb=metrics.memory_used_mb,
        memory_total_mb=metrics.memory_total_mb,
        disk_percent=metrics.disk_percent,
        disk_used_gb=metrics.disk_used_gb,
        disk_total_gb=metrics.disk_total_gb,
        network_sent_rate=metrics.network_sent_rate,
        network_recv_rate=metrics.network_recv_rate,
        load_avg=metrics.load_avg
    )
    db.add(db_metrics)
    db.commit()
    
    # Check thresholds and create events
    if metrics.cpu_percent and metrics.cpu_percent > 80:
        event = Event(
            event_type="HIGH_CPU_AGENT",
            message=f"Agent {agent.name}: CPU at {metrics.cpu_percent}%",
            severity="warning" if metrics.cpu_percent < 90 else "critical",
            source="agent"
        )
        db.add(event)
        db.commit()
    
    if metrics.memory_percent and metrics.memory_percent > 85:
        event = Event(
            event_type="HIGH_MEMORY_AGENT",
            message=f"Agent {agent.name}: Memory at {metrics.memory_percent}%",
            severity="warning" if metrics.memory_percent < 95 else "critical",
            source="agent"
        )
        db.add(event)
        db.commit()
    
    return {"status": "ok", "message": "Metrics received"}


@router.get("/{agent_id}/metrics", response_model=AgentMetricsListResponse)
async def get_agent_metrics(
    agent_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get metrics history for an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    metrics = db.query(AgentMetrics).filter(
        AgentMetrics.agent_id == agent_id
    ).order_by(AgentMetrics.timestamp.desc()).limit(limit).all()
    
    return AgentMetricsListResponse(
        metrics=[AgentMetricsResponse(
            id=m.id,
            agent_id=m.agent_id,
            cpu_percent=float(m.cpu_percent) if m.cpu_percent else None,
            memory_percent=float(m.memory_percent) if m.memory_percent else None,
            memory_used_mb=float(m.memory_used_mb) if m.memory_used_mb else None,
            memory_total_mb=float(m.memory_total_mb) if m.memory_total_mb else None,
            disk_percent=float(m.disk_percent) if m.disk_percent else None,
            disk_used_gb=float(m.disk_used_gb) if m.disk_used_gb else None,
            disk_total_gb=float(m.disk_total_gb) if m.disk_total_gb else None,
            network_sent_rate=float(m.network_sent_rate) if m.network_sent_rate else None,
            network_recv_rate=float(m.network_recv_rate) if m.network_recv_rate else None,
            load_avg=float(m.load_avg) if m.load_avg else None,
            timestamp=m.timestamp
        ) for m in metrics],
        total=len(metrics)
    )


@router.get("/{agent_id}/latest")
async def get_agent_latest_metrics(agent_id: int, db: Session = Depends(get_db)):
    """Get latest metrics for an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    latest = db.query(AgentMetrics).filter(
        AgentMetrics.agent_id == agent_id
    ).order_by(AgentMetrics.timestamp.desc()).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No metrics found for agent")
    
    return {
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status,
            "last_heartbeat": agent.last_heartbeat
        },
        "metrics": {
            "cpu_percent": float(latest.cpu_percent) if latest.cpu_percent else None,
            "memory_percent": float(latest.memory_percent) if latest.memory_percent else None,
            "disk_percent": float(latest.disk_percent) if latest.disk_percent else None,
            "network_sent_rate": float(latest.network_sent_rate) if latest.network_sent_rate else None,
            "network_recv_rate": float(latest.network_recv_rate) if latest.network_recv_rate else None,
            "load_avg": float(latest.load_avg) if latest.load_avg else None,
            "timestamp": latest.timestamp
        }
    }


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete an agent and its metrics"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Delete metrics first
    db.query(AgentMetrics).filter(AgentMetrics.agent_id == agent_id).delete()
    db.delete(agent)
    db.commit()
    
    return {"message": "Agent deleted"}


@router.post("/{agent_id}/toggle")
async def toggle_agent(agent_id: int, db: Session = Depends(get_db)):
    """Activate/deactivate an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_active = 0 if agent.is_active == 1 else 1
    db.commit()
    
    return {"message": f"Agent {'deactivated' if agent.is_active == 0 else 'activated'}"}


# Public endpoint for agents (no auth required, uses API key in body)
@router.post("/submit-metrics")
async def submit_metrics_public(
    api_key: str = Query(...),
    metrics: AgentMetricsSubmit,
    db: Session = Depends(get_db)
):
    """Public endpoint for agents to submit metrics using API key"""
    agent = verify_api_key(api_key, db)
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Update agent info
    if metrics.hostname:
        agent.hostname = metrics.hostname
    if metrics.ip_address:
        agent.ip_address = metrics.ip_address
    if metrics.os_type:
        agent.os_type = metrics.os_type
    agent.last_heartbeat = datetime.utcnow()
    agent.status = "online"
    
    # Store metrics
    db_metrics = AgentMetrics(
        agent_id=agent.id,
        cpu_percent=metrics.cpu_percent,
        memory_percent=metrics.memory_percent,
        memory_used_mb=metrics.memory_used_mb,
        memory_total_mb=metrics.memory_total_mb,
        disk_percent=metrics.disk_percent,
        disk_used_gb=metrics.disk_used_gb,
        disk_total_gb=metrics.disk_total_gb,
        network_sent_rate=metrics.network_sent_rate,
        network_recv_rate=metrics.network_recv_rate,
        load_avg=metrics.load_avg
    )
    db.add(db_metrics)
    db.commit()
    
    return {"status": "ok"}