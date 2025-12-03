"""
Database initialization script for CloudPulse Monitor
Creates tables and optionally seeds initial data
"""

import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from .database import engine, SessionLocal, create_tables, check_database_connection
from .models import Service, Log, Metric
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_initial_services():
    """Create initial services for monitoring"""
    initial_services = [
        {
            "id": "api-gateway",
            "name": "API Gateway",
            "status": "online",
            "uptime": 99.95
        },
        {
            "id": "user-service",
            "name": "User Service",
            "status": "online",
            "uptime": 99.87
        },
        {
            "id": "notification-service",
            "name": "Notification Service",
            "status": "degraded",
            "uptime": 95.23
        },
        {
            "id": "payment-service",
            "name": "Payment Service",
            "status": "online",
            "uptime": 99.99
        },
        {
            "id": "analytics-service",
            "name": "Analytics Service",
            "status": "offline",
            "uptime": 0.0
        }
    ]
    
    db = SessionLocal()
    try:
        for service_data in initial_services:
            # Check if service already exists
            existing_service = db.query(Service).filter(Service.id == service_data["id"]).first()
            if not existing_service:
                service = Service(**service_data)
                db.add(service)
                logger.info(f"Created service: {service_data['name']}")
        
        db.commit()
        logger.info("Initial services created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating initial services: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_logs():
    """Create sample log entries for testing"""
    sample_logs = [
        {
            "level": "info",
            "message": "Service started successfully",
            "service_name": "api-gateway"
        },
        {
            "level": "warning",
            "message": "High memory usage detected",
            "service_name": "user-service"
        },
        {
            "level": "error",
            "message": "Database connection timeout",
            "service_name": "notification-service"
        },
        {
            "level": "info",
            "message": "Payment processed successfully",
            "service_name": "payment-service"
        },
        {
            "level": "error",
            "message": "Service unavailable",
            "service_name": "analytics-service"
        }
    ]
    
    db = SessionLocal()
    try:
        for log_data in sample_logs:
            log = Log(**log_data)
            db.add(log)
        
        db.commit()
        logger.info("Sample logs created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating sample logs: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_metrics():
    """Create sample metrics for testing"""
    sample_metrics = [
        {"metric_name": "cpu_usage", "value": 45.2, "unit": "%"},
        {"metric_name": "memory_usage", "value": 68.7, "unit": "%"},
        {"metric_name": "network_traffic", "value": 342.5, "unit": "MB/s"},
        {"metric_name": "disk_usage", "value": 78.3, "unit": "%"},
        {"metric_name": "response_time", "value": 125.4, "unit": "ms"}
    ]
    
    db = SessionLocal()
    try:
        for metric_data in sample_metrics:
            metric = Metric(**metric_data)
            db.add(metric)
        
        db.commit()
        logger.info("Sample metrics created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating sample metrics: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_database(create_sample_data: bool = True):
    """
    Initialize the database with tables and optional sample data
    
    Args:
        create_sample_data: Whether to create sample data for testing
    """
    logger.info("Starting database initialization...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot connect to database. Please check your configuration.")
        return False
    
    try:
        # Create all tables
        logger.info("Creating database tables...")
        create_tables()
        
        if create_sample_data:
            logger.info("Creating sample data...")
            create_initial_services()
            create_sample_logs()
            create_sample_metrics()
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def reset_database():
    """
    Reset the database by dropping and recreating all tables
    WARNING: This will delete all data!
    """
    logger.warning("Resetting database - this will delete all data!")
    
    from .database import drop_tables
    
    try:
        # Drop all tables
        drop_tables()
        logger.info("All tables dropped")
        
        # Recreate tables and sample data
        return init_database(create_sample_data=True)
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


if __name__ == "__main__":
    # Run database initialization when script is executed directly
    init_database(create_sample_data=True)