"""
Database configuration and session management for CloudPulse Monitor
Handles SQLAlchemy setup, PostgreSQL connection, and session lifecycle
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
import time
from typing import Generator, Optional
from contextlib import contextmanager

from .config import settings
from .exceptions import DatabaseConnectionError, DatabaseOperationError
from .logging_config import get_logger, log_database_operation

# Configure logging
logger = get_logger(__name__)

# Database connection state
_database_available = None
_last_connection_check = 0
_connection_check_interval = 30  # Check every 30 seconds

# SQLAlchemy setup with enhanced error handling and environment-based configuration
try:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,                              # Verify connections before use
        pool_recycle=300,                                # Recycle connections every 5 minutes
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,    # Connection timeout from config
        pool_size=settings.DATABASE_POOL_SIZE,          # Connection pool size from config
        max_overflow=settings.DATABASE_MAX_OVERFLOW,    # Maximum overflow connections from config
        echo=settings.DEBUG,                             # Log SQL queries in debug mode
        connect_args={
            "connect_timeout": settings.DATABASE_HEALTH_CHECK_TIMEOUT,
            "application_name": f"cloudpulse-monitor-{settings.ENVIRONMENT}"
        }
    )
    logger.info("Database engine created successfully", extra={
        "database_host": settings.DATABASE_HOST,
        "database_name": settings.DATABASE_NAME,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "environment": settings.ENVIRONMENT
    })
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Base class for all models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Used with FastAPI's Depends() for automatic session management
    Includes comprehensive error handling and connection validation
    """
    if not SessionLocal:
        logger.error("Database session factory not available")
        raise DatabaseConnectionError("Database connection not initialized")
    
    # Check database availability before creating session
    if not is_database_available():
        logger.warning("Database not available, raising connection error")
        raise DatabaseConnectionError("Database is currently unavailable")
    
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Test the connection
        db.execute(text("SELECT 1"))
        yield db
        
    except OperationalError as e:
        logger.error(f"Database operational error: {e}")
        db.rollback()
        # Mark database as unavailable
        global _database_available
        _database_available = False
        raise DatabaseConnectionError(f"Database connection lost: {str(e)}")
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during session: {e}")
        db.rollback()
        raise DatabaseOperationError(f"Database operation failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected database session error: {e}")
        db.rollback()
        raise DatabaseOperationError(f"Unexpected database error: {str(e)}")
        
    finally:
        duration = time.time() - start_time
        log_database_operation("SESSION", "connection", duration, success=True)
        db.close()


def create_tables():
    """
    Create all database tables with comprehensive error handling
    Used for initial setup and testing
    """
    if not engine:
        raise DatabaseConnectionError("Database engine not available")
    
    start_time = time.time()
    try:
        Base.metadata.create_all(bind=engine)
        duration = time.time() - start_time
        log_database_operation("CREATE_TABLES", "all_tables", duration, success=True)
        logger.info("Database tables created successfully")
        
    except OperationalError as e:
        duration = time.time() - start_time
        log_database_operation("CREATE_TABLES", "all_tables", duration, success=False, error=str(e))
        logger.error(f"Database connection error while creating tables: {e}")
        raise DatabaseConnectionError(f"Cannot create tables: {str(e)}")
        
    except SQLAlchemyError as e:
        duration = time.time() - start_time
        log_database_operation("CREATE_TABLES", "all_tables", duration, success=False, error=str(e))
        logger.error(f"Database error while creating tables: {e}")
        raise DatabaseOperationError(f"Failed to create tables: {str(e)}")
        
    except Exception as e:
        duration = time.time() - start_time
        log_database_operation("CREATE_TABLES", "all_tables", duration, success=False, error=str(e))
        logger.error(f"Unexpected error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables with comprehensive error handling
    Used for testing and development reset
    """
    if not engine:
        raise DatabaseConnectionError("Database engine not available")
    
    start_time = time.time()
    try:
        Base.metadata.drop_all(bind=engine)
        duration = time.time() - start_time
        log_database_operation("DROP_TABLES", "all_tables", duration, success=True)
        logger.info("Database tables dropped successfully")
        
    except OperationalError as e:
        duration = time.time() - start_time
        log_database_operation("DROP_TABLES", "all_tables", duration, success=False, error=str(e))
        logger.error(f"Database connection error while dropping tables: {e}")
        raise DatabaseConnectionError(f"Cannot drop tables: {str(e)}")
        
    except SQLAlchemyError as e:
        duration = time.time() - start_time
        log_database_operation("DROP_TABLES", "all_tables", duration, success=False, error=str(e))
        logger.error(f"Database error while dropping tables: {e}")
        raise DatabaseOperationError(f"Failed to drop tables: {str(e)}")
        
    except Exception as e:
        duration = time.time() - start_time
        log_database_operation("DROP_TABLES", "all_tables", duration, success=False, error=str(e))
        logger.error(f"Unexpected error dropping database tables: {e}")
        raise


def check_database_connection() -> bool:
    """
    Check if database connection is working with detailed error logging
    Returns True if connection is successful, False otherwise
    """
    if not engine:
        logger.error("Database engine not available")
        return False
    
    start_time = time.time()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        duration = time.time() - start_time
        log_database_operation("HEALTH_CHECK", "connection", duration, success=True)
        logger.debug("Database connection health check successful")
        return True
        
    except OperationalError as e:
        duration = time.time() - start_time
        log_database_operation("HEALTH_CHECK", "connection", duration, success=False, error=str(e))
        logger.warning(f"Database connection failed: {e}")
        return False
        
    except Exception as e:
        duration = time.time() - start_time
        log_database_operation("HEALTH_CHECK", "connection", duration, success=False, error=str(e))
        logger.error(f"Unexpected error during database health check: {e}")
        return False


def is_database_available() -> bool:
    """
    Check database availability with caching to avoid frequent connection attempts
    Uses cached result for performance and to prevent connection spam
    
    Returns:
        True if database is available, False otherwise
    """
    global _database_available, _last_connection_check
    
    current_time = time.time()
    
    # Use cached result if recent
    if (_database_available is not None and 
        current_time - _last_connection_check < _connection_check_interval):
        return _database_available
    
    # Perform fresh connection check
    _database_available = check_database_connection()
    _last_connection_check = current_time
    
    return _database_available


@contextmanager
def get_db_session():
    """
    Context manager for database sessions with automatic cleanup
    Provides better error handling for direct database operations
    
    Yields:
        Database session
        
    Raises:
        DatabaseConnectionError: If database is not available
        DatabaseOperationError: If database operation fails
    """
    if not SessionLocal:
        raise DatabaseConnectionError("Database session factory not available")
    
    if not is_database_available():
        raise DatabaseConnectionError("Database is currently unavailable")
    
    session = SessionLocal()
    start_time = time.time()
    
    try:
        yield session
        session.commit()
        
    except OperationalError as e:
        session.rollback()
        # Mark database as unavailable
        global _database_available
        _database_available = False
        duration = time.time() - start_time
        log_database_operation("SESSION_CONTEXT", "transaction", duration, success=False, error=str(e))
        raise DatabaseConnectionError(f"Database connection lost: {str(e)}")
        
    except SQLAlchemyError as e:
        session.rollback()
        duration = time.time() - start_time
        log_database_operation("SESSION_CONTEXT", "transaction", duration, success=False, error=str(e))
        raise DatabaseOperationError(f"Database operation failed: {str(e)}")
        
    except Exception as e:
        session.rollback()
        duration = time.time() - start_time
        log_database_operation("SESSION_CONTEXT", "transaction", duration, success=False, error=str(e))
        raise DatabaseOperationError(f"Unexpected database error: {str(e)}")
        
    finally:
        duration = time.time() - start_time
        log_database_operation("SESSION_CONTEXT", "transaction", duration, success=True)
        session.close()


def reset_database_state():
    """
    Reset the cached database availability state
    Useful for testing or after known database maintenance
    """
    global _database_available, _last_connection_check
    _database_available = None
    _last_connection_check = 0
    logger.info("Database availability state reset")