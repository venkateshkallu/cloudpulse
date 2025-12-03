# CloudPulse Monitor - Docker Setup Guide

This guide covers the Docker containerization setup for CloudPulse Monitor, including development and production configurations.

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (optional, for convenience commands)

### Development Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd cloudpulse-monitor
   cp .env .env.local  # Optional: customize local settings
   ```

2. **Start development environment:**
   ```bash
   # Using Make (recommended)
   make setup

   # Or using Docker Compose directly
   docker compose up -d --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   PostgreSQL    │
│   (React)       │    │   (FastAPI)     │    │   Database      │
│   Port: 5173    │◄──►│   Port: 8000    │◄──►│   Port: 5432    │
│   Nginx         │    │   Python 3.11   │    │   Version 16    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Docker Compose Files

### 1. `docker-compose.yml` (Base Configuration)
- Defines all three services (frontend, backend, postgres)
- Development-friendly defaults
- Includes health checks and proper networking
- Exposes all ports for development access

### 2. `docker-compose.override.yml` (Development Overrides)
- Automatically loaded in development
- Enables hot reload for both frontend and backend
- Mounts source code as volumes
- Enables debug logging and API documentation

### 3. `docker-compose.prod.yml` (Production Configuration)
- Production-optimized settings
- Environment variable driven configuration
- Resource limits and security hardening
- Minimal port exposure

## Environment Configuration

### Development Environment Variables
The `.env` file contains development defaults:

```bash
# Database
DATABASE_NAME=cloudpulse
DATABASE_USER=postgres
DATABASE_PASSWORD=cloudpulse_dev_password

# Ports
FRONTEND_PORT=5173
BACKEND_PORT=8000

# Security (change in production!)
SECRET_KEY=dev-secret-key-change-in-production
```

### Production Environment Variables
For production, create a `.env.prod` file with secure values:

```bash
# Database (use strong passwords!)
DATABASE_PASSWORD=your-secure-password-here

# Security (generate secure keys!)
SECRET_KEY=your-secure-secret-key-here

# Network
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-domain.com

# Features
DOCS_ENABLED=false
DEBUG=false
```

## Service Details

### Frontend Service
- **Base Image:** nginx:alpine
- **Build:** Multi-stage build with Node.js 18
- **Port:** 5173
- **Health Check:** HTTP GET to /
- **Development:** Hot reload with volume mounts

### Backend Service
- **Base Image:** python:3.11-slim
- **Port:** 8000
- **Health Check:** HTTP GET to /api/status
- **Development:** Auto-reload with uvicorn
- **Dependencies:** FastAPI, SQLAlchemy, PostgreSQL drivers

### PostgreSQL Service
- **Image:** postgres:16-alpine
- **Port:** 5432 (exposed in development only)
- **Database:** cloudpulse
- **Initialization:** Automatic schema and sample data setup
- **Persistence:** Named volume for data storage

## Available Commands

### Using Make (Recommended)

```bash
# Development
make setup          # Initial setup for new developers
make dev            # Start development environment
make dev-build      # Build and start development environment
make dev-logs       # Show development logs
make dev-stop       # Stop development environment

# Production
make prod           # Start production environment
make prod-build     # Build and start production environment
make prod-logs      # Show production logs
make prod-stop      # Stop production environment

# Database
make db-shell       # Connect to PostgreSQL shell
make db-reset       # Reset database (destroys all data)

# Maintenance
make logs           # Show all service logs
make health         # Check service health
make clean          # Clean up containers and volumes
make clean-all      # Full cleanup including images

# Development utilities
make shell-backend  # Open shell in backend container
make shell-frontend # Open shell in frontend container
make test           # Run tests in containers
```

### Using Docker Compose Directly

```bash
# Development
docker compose up -d --build
docker compose logs -f
docker compose down

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# Service management
docker compose restart backend
docker compose exec backend /bin/bash
docker compose exec postgres psql -U postgres -d cloudpulse
```

## Networking

### Development Network
- **Network Name:** cloudpulse-network
- **Type:** Bridge network
- **Service Communication:** Internal DNS resolution
- **External Access:** All ports exposed to host

### Service Communication
Services communicate using Docker's internal DNS:
- Frontend → Backend: `http://backend:8000`
- Backend → Database: `postgres:5432`
- External → Frontend: `http://localhost:5173`
- External → Backend: `http://localhost:8000`

## Data Persistence

### Volumes
- **postgres_data:** PostgreSQL data directory
- **Backend logs:** Application logs (./backend/logs)

### Database Initialization
The PostgreSQL service automatically runs `backend/init-db.sql` on first startup:
- Creates required tables (logs, services, metrics)
- Sets up indexes for performance
- Inserts sample data for development
- Creates database functions and triggers

## Health Checks

All services include comprehensive health checks:

### Frontend Health Check
```bash
wget --no-verbose --tries=1 --spider http://127.0.0.1:5173/
```

### Backend Health Check
```bash
python -c "import requests; requests.get('http://localhost:8000/api/status', timeout=5)"
```

### PostgreSQL Health Check
```bash
pg_isready -U postgres -d cloudpulse
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the ports
   lsof -i :5173
   lsof -i :8000
   lsof -i :5432
   
   # Change ports in .env file if needed
   FRONTEND_PORT=3000
   BACKEND_PORT=8080
   ```

2. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Reset database
   make db-reset
   ```

3. **Build failures:**
   ```bash
   # Clean build cache
   docker compose build --no-cache
   
   # Full cleanup and rebuild
   make clean-all
   make dev-build
   ```

4. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   
   # Check Docker daemon
   sudo systemctl status docker
   ```

### Debugging

1. **Check service status:**
   ```bash
   docker compose ps
   make health
   ```

2. **View logs:**
   ```bash
   # All services
   make logs
   
   # Specific service
   make logs-backend
   make logs-frontend
   make logs-postgres
   ```

3. **Access service shells:**
   ```bash
   make shell-backend
   make shell-frontend
   make shell-postgres
   ```

4. **Database debugging:**
   ```bash
   # Connect to database
   make db-shell
   
   # Check tables
   \dt
   
   # Check sample data
   SELECT * FROM services;
   SELECT * FROM logs LIMIT 10;
   ```

## Production Deployment

### AWS ECS Compatibility
The Docker setup is designed for AWS ECS deployment:

1. **Task Definitions:** Each service can be deployed as separate ECS tasks
2. **Service Discovery:** Uses ECS service discovery for internal communication
3. **Load Balancing:** Frontend and backend can be behind Application Load Balancers
4. **Environment Variables:** Supports ECS parameter store integration
5. **Health Checks:** Compatible with ECS health check requirements

### Security Considerations

1. **Environment Variables:** Never commit sensitive values to version control
2. **Network Security:** Production setup minimizes exposed ports
3. **Resource Limits:** Production configuration includes CPU/memory limits
4. **User Permissions:** Backend runs as non-root user
5. **Database Security:** PostgreSQL configured with secure defaults

### Performance Optimization

1. **Multi-stage Builds:** Minimizes image sizes
2. **Layer Caching:** Optimized Dockerfile layer ordering
3. **Resource Limits:** Prevents resource exhaustion
4. **Health Checks:** Ensures service reliability
5. **Connection Pooling:** Database connection pooling configured

## Monitoring and Logging

### Log Management
- **Backend Logs:** Structured JSON logging to ./backend/logs
- **Container Logs:** Docker logs available via `docker compose logs`
- **Database Logs:** PostgreSQL logs for debugging

### Metrics Collection
- **Health Endpoints:** All services expose health check endpoints
- **Application Metrics:** Backend exposes custom metrics
- **Container Metrics:** Docker stats available for monitoring

This Docker setup provides a robust foundation for both development and production deployment of CloudPulse Monitor.