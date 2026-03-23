"""
SQLAlchemy models for CloudPulse Monitor
Defines database tables for logs, services, and metrics
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Index
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from .database import Base


class Log(Base):
    """
    Log entries table for storing application and system logs
    """
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    level = Column(String(20), nullable=False, index=True)  # info, warning, error
    message = Column(Text, nullable=False)
    service_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Composite indexes for efficient querying
    __table_args__ = (
        Index('idx_timestamp_desc', timestamp.desc()),
        Index('idx_service_level', service_name, level),
        Index('idx_service_timestamp', service_name, timestamp.desc()),
    )

    def __repr__(self):
        return f"<Log(id={self.id}, level={self.level}, service={self.service_name})>"


class Service(Base):
    """
    Services table for tracking monitored services and their status
    """
    __tablename__ = "services"

    id = Column(String(50), primary_key=True, index=True)  # e.g., "api-gateway"
    name = Column(String(100), nullable=False)  # e.g., "API Gateway"
    status = Column(String(20), nullable=False, default="offline")  # online, degraded, offline
    uptime = Column(Numeric(5, 2), default=0.0, nullable=False)  # Percentage uptime
    last_checked = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_status', status),
        Index('idx_last_checked', last_checked.desc()),
    )

    def __repr__(self):
        return f"<Service(id={self.id}, name={self.name}, status={self.status})>"


class Metric(Base):
    """
    Metrics table for storing historical performance metrics
    """
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    metric_name = Column(String(50), nullable=False, index=True)  # cpu_usage, memory_usage, etc.
    value = Column(Numeric(10, 2), nullable=False)  # Metric value
    unit = Column(String(20), nullable=True)  # %, MB, GB, etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Composite indexes for efficient time-series queries
    __table_args__ = (
        Index('idx_metric_timestamp', metric_name, timestamp.desc()),
        Index('idx_timestamp_desc', timestamp.desc()),
    )

    def __repr__(self):
        return f"<Metric(id={self.id}, name={self.metric_name}, value={self.value})>"


class MonitoringTarget(Base):
    """
    Targets for external endpoint monitoring (URLs, IPs, domains)
    """
    __tablename__ = "monitoring_targets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Display name
    target_url = Column(String(500), nullable=False)  # URL or IP to monitor
    target_type = Column(String(20), nullable=False, default="http")  # http, https, ping, dns
    check_interval = Column(Integer, default=60)  # Check interval in seconds
    timeout = Column(Integer, default=10)  # Timeout in seconds
    is_active = Column(Integer, default=1)  # 1 = active, 0 = paused
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_target_active', is_active),
    )

    def __repr__(self):
        return f"<MonitoringTarget(id={self.id}, name={self.name}, url={self.target_url})>"


class MonitoringResult(Base):
    """
    Results from endpoint monitoring checks
    """
    __tablename__ = "monitoring_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    target_id = Column(Integer, nullable=False, index=True)  # Reference to MonitoringTarget
    status_code = Column(Integer, nullable=True)  # HTTP status code (null if failed)
    response_time_ms = Column(Numeric(10, 2), nullable=True)  # Response time in milliseconds
    is_up = Column(Integer, nullable=False)  # 1 = up, 0 = down
    error_message = Column(Text, nullable=True)  # Error details if failed
    dns_resolution = Column(String(100), nullable=True)  # DNS resolved IP (for DNS checks)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_target_timestamp', target_id, timestamp.desc()),
        Index('idx_timestamp_desc', timestamp.desc()),
    )

    def __repr__(self):
        return f"<MonitoringResult(id={self.id}, target_id={self.target_id}, is_up={self.is_up})>"


class SystemMetricsSnapshot(Base):
    """
    Time-series storage for real system metrics
    Stores CPU, memory, disk, network metrics at regular intervals
    """
    __tablename__ = "system_metrics_snapshots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cpu_percent = Column(Numeric(5, 2), nullable=False)
    memory_percent = Column(Numeric(5, 2), nullable=False)
    memory_used_mb = Column(Numeric(10, 2), nullable=True)
    memory_total_mb = Column(Numeric(10, 2), nullable=True)
    disk_percent = Column(Numeric(5, 2), nullable=True)
    disk_used_gb = Column(Numeric(10, 2), nullable=True)
    disk_total_gb = Column(Numeric(10, 2), nullable=True)
    bytes_sent = Column(Numeric(15, 2), nullable=True)  # Cumulative bytes sent
    bytes_recv = Column(Numeric(15, 2), nullable=True)  # Cumulative bytes received
    network_sent_rate = Column(Numeric(15, 2), nullable=True)  # bytes/sec
    network_recv_rate = Column(Numeric(15, 2), nullable=True)  # bytes/sec
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_metrics_timestamp_desc', timestamp.desc()),
    )

    def __repr__(self):
        return f"<SystemMetricsSnapshot(id={self.id}, cpu={self.cpu_percent}%, memory={self.memory_percent}%)>"


class Event(Base):
    """
    Events table for storing alerts and threshold violations
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)  # HIGH_CPU, SERVICE_DOWN, etc.
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # info, warning, critical
    source = Column(String(50), nullable=True)  # system, monitoring, metrics
    metadata = Column(Text, nullable=True)  # JSON string with additional data
    is_resolved = Column(Integer, default=0)  # 0 = active, 1 = resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_event_severity', severity),
        Index('idx_event_type', event_type),
        Index('idx_event_created_desc', created_at.desc()),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, severity={self.severity})>"


class Agent(Base):
    """
    Remote monitoring agents that collect metrics from different machines
    """
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    hostname = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    os_type = Column(String(50), nullable=True)  # linux, windows, darwin
    status = Column(String(20), nullable=False, default="offline")  # online, offline
    api_key = Column(String(64), nullable=False, unique=True)  # Unique key for agent authentication
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_agent_status', status),
        Index('idx_agent_active', is_active),
    )

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, status={self.status})>"


class AgentMetrics(Base):
    """
    Metrics received from remote agents
    """
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_id = Column(Integer, nullable=False, index=True)
    cpu_percent = Column(Numeric(5, 2), nullable=True)
    memory_percent = Column(Numeric(5, 2), nullable=True)
    memory_used_mb = Column(Numeric(10, 2), nullable=True)
    memory_total_mb = Column(Numeric(10, 2), nullable=True)
    disk_percent = Column(Numeric(5, 2), nullable=True)
    disk_used_gb = Column(Numeric(10, 2), nullable=True)
    disk_total_gb = Column(Numeric(10, 2), nullable=True)
    network_sent_rate = Column(Numeric(15, 2), nullable=True)
    network_recv_rate = Column(Numeric(15, 2), nullable=True)
    load_avg = Column(Numeric(10, 4), nullable=True)  # System load average
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_agent_metrics_timestamp', agent_id, timestamp.desc()),
        Index('idx_agent_metrics_desc', timestamp.desc()),
    )

    def __repr__(self):
        return f"<AgentMetrics(id={self.id}, agent_id={self.agent_id}, cpu={self.cpu_percent}%)>"