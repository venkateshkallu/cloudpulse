"""
Real metrics collector using psutil
Handles system metrics collection, network rate calculation, and event generation
"""

import psutil
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .models import SystemMetricsSnapshot, Event, MonitoringResult
from .database import SessionLocal
from .logging_config import get_logger

logger = get_logger(__name__)

# Thresholds for event generation
CPU_THRESHOLD = 80
MEM_THRESHOLD = 85
DISK_THRESHOLD = 90
RESPONSE_TIME_THRESHOLD = 2000  # ms

# Store previous network stats for rate calculation
_prev_net_stats: Optional[Dict[str, Any]] = None
_prev_net_time: Optional[float] = None


def get_real_system_metrics() -> Dict[str, Any]:
    """
    Collect real system metrics using psutil
    Returns dict with CPU, memory, disk, and network metrics
    """
    global _prev_net_stats, _prev_net_time
    
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)
        
        # Network - calculate rate
        net_io = psutil.net_io_counters()
        current_time = time.time()
        
        network_sent_rate = 0.0
        network_recv_rate = 0.0
        
        if _prev_net_stats is not None and _prev_net_time is not None:
            time_diff = current_time - _prev_net_time
            if time_diff > 0:
                network_sent_rate = (net_io.bytes_sent - _prev_net_stats['bytes_sent']) / time_diff
                network_recv_rate = (net_io.bytes_recv - _prev_net_stats['bytes_recv']) / time_diff
                # Ensure non-negative (in case of counter reset)
                network_sent_rate = max(0, network_sent_rate)
                network_recv_rate = max(0, network_recv_rate)
        
        # Store current values for next calculation
        _prev_net_stats = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        }
        _prev_net_time = current_time
        
        return {
            'cpu_percent': round(cpu_percent, 2),
            'memory_percent': round(memory_percent, 2),
            'memory_used_mb': round(memory_used_mb, 2),
            'memory_total_mb': round(memory_total_mb, 2),
            'disk_percent': round(disk_percent, 2),
            'disk_used_gb': round(disk_used_gb, 2),
            'disk_total_gb': round(disk_total_gb, 2),
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'network_sent_rate': round(network_sent_rate, 2),
            'network_recv_rate': round(network_recv_rate, 2),
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        raise


def store_metrics_snapshot(db: Session, metrics: Dict[str, Any]) -> SystemMetricsSnapshot:
    """
    Store metrics snapshot to database
    """
    snapshot = SystemMetricsSnapshot(
        cpu_percent=metrics['cpu_percent'],
        memory_percent=metrics['memory_percent'],
        memory_used_mb=metrics['memory_used_mb'],
        memory_total_mb=metrics['memory_total_mb'],
        disk_percent=metrics['disk_percent'],
        disk_used_gb=metrics['disk_used_gb'],
        disk_total_gb=metrics['disk_total_gb'],
        bytes_sent=metrics['bytes_sent'],
        bytes_recv=metrics['bytes_recv'],
        network_sent_rate=metrics['network_sent_rate'],
        network_recv_rate=metrics['network_recv_rate'],
        timestamp=metrics['timestamp']
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def create_event(
    db: Session,
    event_type: str,
    message: str,
    severity: str,
    source: str = "system",
    metadata: Optional[Dict[str, Any]] = None
) -> Event:
    """
    Create and store an event
    """
    import json
    
    event = Event(
        event_type=event_type,
        message=message,
        severity=severity,
        source=source,
        metadata=json.dumps(metadata) if metadata else None
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    logger.warning(f"Event created: {event_type} - {message}", extra={
        "severity": severity,
        "source": source
    })
    
    return event


def check_and_create_events(db: Session, metrics: Dict[str, Any], monitoring_results: list = None) -> list:
    """
    Check thresholds and create events if needed
    Returns list of created events
    """
    created_events = []
    
    # Check CPU threshold
    if metrics['cpu_percent'] > CPU_THRESHOLD:
        event = create_event(
            db,
            event_type="HIGH_CPU",
            message=f"CPU usage is {metrics['cpu_percent']}% (threshold: {CPU_THRESHOLD}%)",
            severity="warning" if metrics['cpu_percent'] < 90 else "critical",
            source="metrics",
            metadata={"cpu_percent": metrics['cpu_percent'], "threshold": CPU_THRESHOLD}
        )
        created_events.append(event)
    
    # Check memory threshold
    if metrics['memory_percent'] > MEM_THRESHOLD:
        event = create_event(
            db,
            event_type="HIGH_MEMORY",
            message=f"Memory usage is {metrics['memory_percent']}% (threshold: {MEM_THRESHOLD}%)",
            severity="warning" if metrics['memory_percent'] < 95 else "critical",
            source="metrics",
            metadata={"memory_percent": metrics['memory_percent'], "threshold": MEM_THRESHOLD}
        )
        created_events.append(event)
    
    # Check disk threshold
    if metrics['disk_percent'] > DISK_THRESHOLD:
        event = create_event(
            db,
            event_type="HIGH_DISK",
            message=f"Disk usage is {metrics['disk_percent']}% (threshold: {DISK_THRESHOLD}%)",
            severity="warning",
            source="metrics",
            metadata={"disk_percent": metrics['disk_percent'], "threshold": DISK_THRESHOLD}
        )
        created_events.append(event)
    
    # Check monitoring results for service failures and slow responses
    if monitoring_results:
        for result in monitoring_results:
            # Check for service down
            if result.is_up == 0:
                event = create_event(
                    db,
                    event_type="SERVICE_DOWN",
                    message=f"Service {result.target_id} is down: {result.error_message or 'No response'}",
                    severity="critical",
                    source="monitoring",
                    metadata={"target_id": result.target_id, "status_code": result.status_code}
                )
                created_events.append(event)
            
            # Check for slow response
            elif result.response_time_ms and result.response_time_ms > RESPONSE_TIME_THRESHOLD:
                event = create_event(
                    db,
                    event_type="SLOW_RESPONSE",
                    message=f"Service {result.target_id} slow response: {result.response_time_ms}ms",
                    severity="warning",
                    source="monitoring",
                    metadata={"target_id": result.target_id, "response_time_ms": result.response_time_ms}
                )
                created_events.append(event)
            
            # Check for 5xx errors
            elif result.status_code and result.status_code >= 500:
                event = create_event(
                    db,
                    event_type="SERVICE_ERROR",
                    message=f"Service {result.target_id} returned {result.status_code}",
                    severity="critical",
                    source="monitoring",
                    metadata={"target_id": result.target_id, "status_code": result.status_code}
                )
                created_events.append(event)
    
    # Correlation: High CPU + Slow responses
    if metrics['cpu_percent'] > CPU_THRESHOLD and monitoring_results:
        slow_results = [r for r in monitoring_results if r.response_time_ms and r.response_time_ms > RESPONSE_TIME_THRESHOLD]
        if slow_results:
            event = create_event(
                db,
                event_type="PERF_DEGRADATION",
                message=f"High CPU ({metrics['cpu_percent']}%) correlated with slow responses",
                severity="critical",
                source="correlation",
                metadata={
                    "cpu_percent": metrics['cpu_percent'],
                    "slow_response_count": len(slow_results)
                }
            )
            created_events.append(event)
    
    return created_events


def collect_and_store_metrics():
    """
    Main function to collect metrics, store to DB, and generate events
    Called by background scheduler
    """
    db = SessionLocal()
    try:
        # Collect real metrics
        metrics = get_real_system_metrics()
        
        # Store to database
        store_metrics_snapshot(db, metrics)
        
        # Get recent monitoring results for event correlation
        from datetime import timedelta
        recent_results = db.query(MonitoringResult).filter(
            MonitoringResult.timestamp >= datetime.utcnow() - timedelta(minutes=5)
        ).all()
        
        # Check thresholds and create events
        check_and_create_events(db, metrics, recent_results)
        
        logger.debug(f"Metrics collected and stored: CPU={metrics['cpu_percent']}%, Memory={metrics['memory_percent']}%")
        
    except Exception as e:
        logger.error(f"Error in collect_and_store_metrics: {e}")
    finally:
        db.close()


def get_recent_snapshots(db: Session, limit: int = 100) -> list:
    """Get recent metrics snapshots"""
    return db.query(SystemMetricsSnapshot).order_by(
        SystemMetricsSnapshot.timestamp.desc()
    ).limit(limit).all()


def get_metrics_aggregates(db: Session, hours: int = 24) -> Dict[str, Any]:
    """Get aggregated metrics over a time period"""
    from datetime import timedelta
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    snapshots = db.query(SystemMetricsSnapshot).filter(
        SystemMetricsSnapshot.timestamp >= start_time
    ).all()
    
    if not snapshots:
        return {
            "cpu": {"avg": 0, "min": 0, "max": 0},
            "memory": {"avg": 0, "min": 0, "max": 0},
            "disk": {"avg": 0, "min": 0, "max": 0},
            "network_sent_rate": {"avg": 0},
            "network_recv_rate": {"avg": 0}
        }
    
    cpu_values = [s.cpu_percent for s in snapshots]
    memory_values = [s.memory_percent for s in snapshots]
    disk_values = [s.disk_percent for s in snapshots]
    sent_values = [s.network_sent_rate for s in snapshots if s.network_sent_rate]
    recv_values = [s.network_recv_rate for s in snapshots if s.network_recv_rate]
    
    return {
        "cpu": {
            "avg": round(sum(cpu_values) / len(cpu_values), 2),
            "min": round(min(cpu_values), 2),
            "max": round(max(cpu_values), 2)
        },
        "memory": {
            "avg": round(sum(memory_values) / len(memory_values), 2),
            "min": round(min(memory_values), 2),
            "max": round(max(memory_values), 2)
        },
        "disk": {
            "avg": round(sum(disk_values) / len(disk_values), 2),
            "min": round(min(disk_values), 2),
            "max": round(max(disk_values), 2)
        },
        "network_sent_rate": {
            "avg": round(sum(sent_values) / len(sent_values), 2) if sent_values else 0
        },
        "network_recv_rate": {
            "avg": round(sum(recv_values) / len(recv_values), 2) if recv_values else 0
        }
    }
# Retention policy
def cleanup_old_metrics():
    """
    Clean up old metrics data based on retention policy
    - Keep raw metrics for 2 days
    - Delete older data to prevent DB bloat
    """
    from datetime import timedelta
    
    db = SessionLocal()
    try:
        # Delete metrics older than 2 days
        cutoff = datetime.utcnow() - timedelta(days=2)
        deleted = db.query(SystemMetricsSnapshot).filter(
            SystemMetricsSnapshot.timestamp < cutoff
        ).delete()
        db.commit()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old metrics snapshots")
        
        # Clean up old agent metrics (same policy)
        from .models import AgentMetrics
        deleted_agents = db.query(AgentMetrics).filter(
            AgentMetrics.timestamp < cutoff
        ).delete()
        db.commit()
        
        if deleted_agents > 0:
            logger.info(f"Cleaned up {deleted_agents} old agent metrics")
        
        # Clean up old events (keep for 7 days)
        events_cutoff = datetime.utcnow() - timedelta(days=7)
        from .models import Event
        deleted_events = db.query(Event).filter(
            Event.created_at < events_cutoff,
            Event.is_resolved == 1
        ).delete()
        db.commit()
        
        if deleted_events > 0:
            logger.info(f"Cleaned up {deleted_events} old resolved events")
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_metrics: {e}")
    finally:
        db.close()


# Anomaly detection
def detect_anomalies(db: Session, agent_id: int = None) -> list:
    """
    Detect anomalies by comparing current values to recent averages
    Simple deterministic approach: if current > 2x avg of last 10 minutes, it's anomalous
    """
    from datetime import timedelta
    
    anomalies = []
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    
    # Get recent snapshots
    query = db.query(SystemMetricsSnapshot).filter(
        SystemMetricsSnapshot.timestamp >= ten_minutes_ago
    )
    if agent_id:
        # For agent metrics
        from .models import AgentMetrics
        recent = db.query(AgentMetrics).filter(
            AgentMetrics.agent_id == agent_id,
            AgentMetrics.timestamp >= ten_minutes_ago
        ).all()
        
        if not recent:
            return anomalies
            
        cpu_values = [m.cpu_percent for m in recent if m.cpu_percent]
        mem_values = [m.memory_percent for m in recent if m.memory_percent]
        
        if cpu_values and len(cpu_values) >= 3:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            latest_cpu = cpu_values[0]
            if latest_cpu > avg_cpu * 2 and avg_cpu > 10:
                anomalies.append({
                    'type': 'CPU_SPIKE',
                    'message': f'CPU spike detected: {latest_cpu}% vs avg {avg_cpu:.1f}%',
                    'severity': 'warning'
                })
        
        if mem_values and len(mem_values) >= 3:
            avg_mem = sum(mem_values) / len(mem_values)
            latest_mem = mem_values[0]
            if latest_mem > avg_mem * 1.5 and avg_mem > 30:
                anomalies.append({
                    'type': 'MEMORY_SPIKE',
                    'message': f'Memory spike detected: {latest_mem}% vs avg {avg_mem:.1f}%',
                    'severity': 'warning'
                })
    else:
        # Local system metrics
        recent = query.all()
        
        if not recent:
            return anomalies
            
        cpu_values = [s.cpu_percent for s in recent if s.cpu_percent]
        mem_values = [s.memory_percent for s in recent if s.memory_percent]
        
        if cpu_values and len(cpu_values) >= 3:
            avg_cpu = sum(cpu_values) / len(cpu_values)
            latest_cpu = cpu_values[0]
            if latest_cpu > avg_cpu * 2 and avg_cpu > 10:
                anomalies.append({
                    'type': 'CPU_SPIKE',
                    'message': f'CPU spike: {latest_cpu}% (2x avg {avg_cpu:.1f}%)',
                    'severity': 'warning'
                })
        
        if mem_values and len(mem_values) >= 3:
            avg_mem = sum(mem_values) / len(mem_values)
            latest_mem = mem_values[0]
            if latest_mem > avg_mem * 1.5 and avg_mem > 30:
                anomalies.append({
                    'type': 'MEMORY_SPIKE',
                    'message': f'Memory spike: {latest_mem}% (1.5x avg {avg_mem:.1f}%)',
                    'severity': 'warning'
                })
    
    return anomalies
