"""
Structured logging configuration for CloudPulse Monitor
Provides centralized logging setup with proper formatting and handlers
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path

from .config import settings


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs
    Includes timestamp, level, logger name, message, and additional context
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields from the log record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
                'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage'
            }:
                extra_fields[key] = value
        
        if extra_fields:
            log_data["extra"] = extra_fields
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Console formatter with color coding for different log levels
    Used for development and debugging
    """
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console output"""
        
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build formatted message
        formatted = (
            f"{color}[{timestamp}] {record.levelname:8s}{reset} "
            f"{record.name}:{record.lineno} - {record.getMessage()}"
        )
        
        # Add exception information if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging() -> None:
    """
    Configure application logging based on environment settings
    Sets up both console and file handlers with appropriate formatters
    """
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if settings.DEBUG:
        console_formatter = ColoredConsoleFormatter()
    else:
        console_formatter = StructuredFormatter()
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Try to set up file logging if possible
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Test if we can write to the logs directory
        test_file = log_dir / "test_write.tmp"
        test_file.touch()
        test_file.unlink()
        
        # File handler with structured JSON output
        file_handler = logging.FileHandler(log_dir / "cloudpulse.log")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
        
        # Error file handler for errors and above
        error_handler = logging.FileHandler(log_dir / "cloudpulse_errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)
        
    except (PermissionError, OSError) as e:
        # If file logging fails, just use console logging
        print(f"Warning: Could not set up file logging: {e}. Using console logging only.")
        pass
    
    # Configure specific loggers
    configure_logger_levels()
    
    # Log configuration completion
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration completed", extra={
        "log_level": settings.LOG_LEVEL,
        "debug_mode": settings.DEBUG,
        "handlers": ["console", "file", "error_file"]
    })


def configure_logger_levels() -> None:
    """Configure log levels for specific loggers"""
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Set application loggers to appropriate levels
    logging.getLogger("app").setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    logging.getLogger("app.database").setLevel(logging.INFO)
    logging.getLogger("app.routes").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request_info(
    method: str,
    url: str,
    status_code: int,
    response_time: float,
    user_agent: str = None,
    client_ip: str = None
) -> None:
    """
    Log HTTP request information
    
    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        response_time: Response time in seconds
        user_agent: User agent string
        client_ip: Client IP address
    """
    logger = get_logger("app.requests")
    
    extra_data = {
        "request_method": method,
        "request_url": url,
        "response_status": status_code,
        "response_time_ms": round(response_time * 1000, 2),
    }
    
    if user_agent:
        extra_data["user_agent"] = user_agent
    
    if client_ip:
        extra_data["client_ip"] = client_ip
    
    logger.info(f"{method} {url} - {status_code} ({response_time:.3f}s)", extra=extra_data)


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    success: bool = True,
    error: str = None
) -> None:
    """
    Log database operation information
    
    Args:
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration: Operation duration in seconds
        success: Whether operation was successful
        error: Error message if operation failed
    """
    logger = get_logger("app.database")
    
    extra_data = {
        "db_operation": operation,
        "db_table": table,
        "duration_ms": round(duration * 1000, 2),
        "success": success
    }
    
    if error:
        extra_data["error"] = error
    
    if success:
        logger.info(f"DB {operation} on {table} completed ({duration:.3f}s)", extra=extra_data)
    else:
        logger.error(f"DB {operation} on {table} failed: {error}", extra=extra_data)


def log_background_task(
    task_name: str,
    duration: float,
    success: bool = True,
    error: str = None,
    **kwargs
) -> None:
    """
    Log background task execution
    
    Args:
        task_name: Name of the background task
        duration: Task duration in seconds
        success: Whether task was successful
        error: Error message if task failed
        **kwargs: Additional task-specific data
    """
    logger = get_logger("app.background_tasks")
    
    extra_data = {
        "task_name": task_name,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
        **kwargs
    }
    
    if error:
        extra_data["error"] = error
    
    if success:
        logger.info(f"Background task '{task_name}' completed ({duration:.3f}s)", extra=extra_data)
    else:
        logger.error(f"Background task '{task_name}' failed: {error}", extra=extra_data)