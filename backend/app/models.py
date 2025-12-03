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