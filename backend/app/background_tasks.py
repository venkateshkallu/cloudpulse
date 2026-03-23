"""
Background task scheduler for periodic endpoint monitoring and metrics collection
"""

import asyncio
from datetime import datetime
from typing import List

from .database import SessionLocal
from .models import MonitoringTarget, MonitoringResult
from .routes.monitoring import check_target
from .metrics_collector import collect_and_store_metrics


async def check_all_targets():
    """Check all active monitoring targets"""
    db = SessionLocal()
    try:
        targets = db.query(MonitoringTarget).filter(MonitoringTarget.is_active == 1).all()
        
        for target in targets:
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
    except Exception as e:
        print(f"Background check error: {e}")
    finally:
        db.close()


async def metrics_scheduler():
    """Run metrics collection every 10 seconds"""
    while True:
        try:
            collect_and_store_metrics()
        except Exception as e:
            print(f"Metrics collection error: {e}")
        await asyncio.sleep(10)  # Collect every 10 seconds


async def monitoring_scheduler():
    """Run endpoint monitoring every 60 seconds"""
    while True:
        try:
            await check_all_targets()
        except Exception as e:
            print(f"Monitoring check error: {e}")
        await asyncio.sleep(60)  # Check every 60 seconds


def start_background_scheduler():
    """Start the background schedulers"""
    # Start metrics collection (every 10 seconds)
    asyncio.create_task(metrics_scheduler())
    # Start endpoint monitoring (every 60 seconds)
    asyncio.create_task(monitoring_scheduler())
    print("Background schedulers started: metrics (10s), monitoring (60s)")