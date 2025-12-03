"""
CloudPulse Monitor FastAPI Backend
Main application entry point with CORS configuration, error handling, and logging
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import time
import asyncio
from contextlib import asynccontextmanager

from .config import settings
from .database import check_database_connection, is_database_available, reset_database_state
from .init_db import init_database
from .routes import metrics, services, logs, status
from .logging_config import setup_logging, get_logger, log_request_info
from .exception_handlers import register_exception_handlers

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with comprehensive startup and shutdown handling
    Handles database initialization, health checks, and graceful degradation
    """
    # Startup
    logger.info("Starting CloudPulse Monitor API...", extra={
        "version": "1.0.0",
        "debug_mode": settings.DEBUG,
        "log_level": settings.LOG_LEVEL
    })
    
    # Reset database state on startup
    reset_database_state()
    
    # Check database connection with retry logic
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            if check_database_connection():
                logger.info("Database connection successful", extra={
                    "attempt": attempt + 1,
                    "database_host": settings.DATABASE_HOST,
                    "database_name": settings.DATABASE_NAME
                })
                
                # Initialize database tables if they don't exist
                try:
                    init_database(create_sample_data=False)
                    logger.info("Database initialization completed")
                except Exception as e:
                    logger.error(f"Database initialization failed: {e}", exc_info=True)
                    # Continue startup even if initialization fails
                
                break
            else:
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection failed, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Database connection failed after all retries - API will run with limited functionality")
                    
        except Exception as e:
            logger.error(f"Unexpected error during database connection (attempt {attempt + 1}): {e}", exc_info=True)
            if attempt == max_retries - 1:
                logger.error("Database setup failed completely - API will run in degraded mode")
    
    # Log startup completion
    logger.info("CloudPulse Monitor API startup completed", extra={
        "database_available": is_database_available(),
        "cors_origins": settings.CORS_ORIGINS,
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG
    })
    
    yield
    
    # Shutdown
    logger.info("Shutting down CloudPulse Monitor API...")
    logger.info("CloudPulse Monitor API shutdown completed")

# Create FastAPI application instance with environment-specific configuration
docs_config = settings.get_docs_config()
app = FastAPI(
    title=settings.API_TITLE,
    description="Backend API for CloudPulse monitoring system with comprehensive error handling",
    version=settings.API_VERSION,
    lifespan=lifespan,
    # Custom error responses
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"},
        429: {"description": "Rate Limit Exceeded"},
        500: {"description": "Internal Server Error"},
        503: {"description": "Service Unavailable"}
    },
    **docs_config
)

# Register exception handlers
register_exception_handlers(app)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else settings.ALLOWED_HOSTS
)

# Configure CORS middleware for frontend integration with environment-specific settings
cors_config = settings.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests with timing and error information
    """
    start_time = time.time()
    
    # Extract request information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log successful request
        log_request_info(
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            response_time=process_time,
            user_agent=user_agent,
            client_ip=client_ip
        )
        
        # Add response headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-API-Version"] = "1.0.0"
        
        return response
        
    except Exception as e:
        # Calculate response time for failed requests
        process_time = time.time() - start_time
        
        # Log failed request
        logger.error(
            f"Request failed: {request.method} {request.url}",
            extra={
                "request_method": request.method,
                "request_url": str(request.url),
                "response_time_ms": round(process_time * 1000, 2),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "error": str(e)
            },
            exc_info=True
        )
        
        # Re-raise the exception to be handled by exception handlers
        raise

@app.get("/")
async def root():
    """Root endpoint for basic health check"""
    return {
        "message": settings.API_TITLE,
        "status": "running",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for container orchestration
    Includes database status and service health information
    """
    start_time = time.time()
    
    try:
        # Check database availability
        db_available = is_database_available()
        db_status = "connected" if db_available else "disconnected"
        
        # Determine overall health status
        if db_available:
            overall_status = "healthy"
        else:
            overall_status = "degraded"  # API can still serve some endpoints
        
        health_data = {
            "status": overall_status,
            "service": "cloudpulse-api",
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": {
                "status": db_status,
                "available": db_available
            },
            "uptime": time.time() - start_time,
            "timestamp": time.time(),
            "checks": {
                "database": db_available,
                "api": True  # If we're responding, API is working
            }
        }
        
        # Return appropriate status code
        status_code = 200 if overall_status == "healthy" else 503
        
        logger.debug("Health check completed", extra={
            "overall_status": overall_status,
            "database_status": db_status,
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        })
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "service": "cloudpulse-api",
            "error": "Health check failed",
            "timestamp": time.time()
        }


@app.get("/readiness")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes/ECS
    Returns 200 only when service is ready to handle requests
    """
    try:
        # Service is ready if database is available or if we can run in degraded mode
        db_available = is_database_available()
        
        if db_available:
            return {"status": "ready", "database": "connected"}
        else:
            # Still ready for non-database endpoints
            return {"status": "ready", "database": "disconnected", "mode": "degraded"}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}", exc_info=True)
        return {"status": "not_ready", "error": str(e)}


# Include API route handlers
app.include_router(metrics.router)
app.include_router(services.router)
app.include_router(logs.router)
app.include_router(status.router)

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting CloudPulse Monitor API server...")
    
    try:
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise