# Design Document

## Overview

The CloudPulse Monitor transformation involves converting a Lovable AI generated React frontend into a production-ready full-stack monitoring application. The design follows a clean separation of concerns with a React frontend, FastAPI backend, PostgreSQL database, and Docker containerization for consistent deployment.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend (React + Vite)"
        A[React App] --> B[Components]
        A --> C[Pages]
        A --> D[API Client]
    end
    
    subgraph "Backend (FastAPI)"
        E[FastAPI Server] --> F[Route Handlers]
        F --> G[Database Models]
        F --> H[Background Tasks]
    end
    
    subgraph "Database"
        I[PostgreSQL]
    end
    
    subgraph "Infrastructure"
        J[Docker Compose]
        K[Nginx (Future)]
    end
    
    D --> E
    G --> I
    J --> A
    J --> E
    J --> I
```

### Project Structure

```
cloudpulse-monitor/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MetricCard.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Services.tsx
│   │   │   ├── Logs.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── About.tsx
│   │   ├── layouts/
│   │   │   └── MainLayout.tsx
│   │   ├── assets/
│   │   │   └── logo.svg
│   │   ├── hooks/
│   │   │   ├── useApi.ts
│   │   │   └── useWebSocket.ts
│   │   ├── utils/
│   │   │   ├── api.ts
│   │   │   └── constants.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py
│   │   │   ├── services.py
│   │   │   ├── logs.py
│   │   │   └── status.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── background_tasks.py
│   │   └── config.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

## Components and Interfaces

### Frontend Components

#### API Client Layer
- **ApiClient**: Centralized HTTP client with error handling
- **WebSocket Client**: Real-time updates for metrics and logs
- **Custom Hooks**: useMetrics, useServices, useLogs for data fetching

#### UI Components
- **Layout Components**: Header, Sidebar, MainLayout
- **Data Display**: MetricCard, ServiceCard, LogEntry
- **Charts**: Performance charts using Recharts library
- **Status Indicators**: Health badges, trend indicators

#### Page Components
- **Dashboard**: Real-time metrics overview with charts
- **Services**: Service status monitoring and management
- **Logs**: Searchable log viewer with filtering
- **Settings**: Configuration management
- **About**: Application information and version

### Backend Components

#### FastAPI Application Structure
- **Main Application**: CORS configuration, middleware setup
- **Route Handlers**: RESTful API endpoints
- **Database Layer**: SQLAlchemy models and session management
- **Background Tasks**: Metric simulation and data generation
- **Configuration**: Environment-based settings management

#### API Endpoints Design

```python
# Metrics Endpoint
GET /api/metrics
Response: {
  "cpu_usage": 45.2,
  "memory_usage": 68.7,
  "network_traffic": 342.5,
  "container_count": 24,
  "overall_health": 92,
  "timestamp": "2024-01-15T10:30:00Z"
}

# Services Endpoint
GET /api/services
Response: [
  {
    "id": "api-gateway",
    "name": "API Gateway",
    "uptime": 99.98,
    "status": "online",
    "last_checked": "2024-01-15T10:29:30Z"
  }
]

# Logs Endpoint
GET /api/logs?limit=50&level=error&service=api-gateway
Response: [
  {
    "id": "log-123",
    "timestamp": "2024-01-15T10:25:00Z",
    "level": "error",
    "message": "Database connection timeout",
    "service_name": "api-gateway"
  }
]

# Status Endpoint
GET /api/status
Response: {
  "overall_status": "healthy",
  "services_online": 5,
  "services_total": 6,
  "critical_alerts": 0,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

## Data Models

### Database Schema

#### Logs Table
```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_timestamp (timestamp),
    INDEX idx_service_level (service_name, level)
);
```

#### Services Table
```sql
CREATE TABLE services (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    uptime DECIMAL(5,2) DEFAULT 0.0,
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Metrics Table (for historical data)
```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_metric_timestamp (metric_name, timestamp)
);
```

### TypeScript Interfaces

```typescript
// Shared types between frontend and backend
interface Metric {
  name: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  timestamp: string;
}

interface Service {
  id: string;
  name: string;
  uptime: number;
  status: 'online' | 'degraded' | 'offline';
  last_checked: string;
}

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  service_name: string;
}

interface SystemStatus {
  overall_status: 'healthy' | 'warning' | 'critical';
  services_online: number;
  services_total: number;
  critical_alerts: number;
  last_updated: string;
}
```

## Error Handling

### Frontend Error Handling
- **API Error Interceptor**: Centralized error handling for HTTP requests
- **Error Boundaries**: React error boundaries for component-level error catching
- **Toast Notifications**: User-friendly error messages using Sonner
- **Retry Logic**: Automatic retry for failed API requests with exponential backoff
- **Offline Detection**: Handle network connectivity issues gracefully

### Backend Error Handling
- **HTTP Exception Handlers**: Custom FastAPI exception handlers
- **Database Error Handling**: Connection pool management and retry logic
- **Validation Errors**: Pydantic model validation with detailed error messages
- **Logging**: Structured logging with different levels (DEBUG, INFO, WARNING, ERROR)
- **Health Check Endpoints**: `/health` endpoint for container orchestration

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "service_id",
      "issue": "Service ID must be a valid string"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Jest + React Testing Library for components
- **Integration Tests**: API integration testing with MSW (Mock Service Worker)
- **E2E Tests**: Playwright for critical user flows
- **Visual Regression**: Chromatic for UI component testing
- **Performance Tests**: Lighthouse CI for performance monitoring

### Backend Testing
- **Unit Tests**: pytest for individual functions and classes
- **Integration Tests**: FastAPI TestClient for API endpoint testing
- **Database Tests**: pytest-postgresql for database integration tests
- **Load Tests**: Locust for performance and scalability testing
- **Security Tests**: Bandit for security vulnerability scanning

### Test Coverage Goals
- Frontend: >80% code coverage
- Backend: >90% code coverage
- Critical paths: 100% coverage (authentication, data persistence)

### CI/CD Pipeline
```yaml
# GitHub Actions workflow
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
      - name: Build
        run: npm run build
  
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

## Performance Considerations

### Frontend Optimization
- **Code Splitting**: Route-based code splitting with React.lazy()
- **Bundle Optimization**: Vite's built-in optimizations and tree shaking
- **Caching Strategy**: Service worker for API response caching
- **Image Optimization**: WebP format with fallbacks
- **Lazy Loading**: Intersection Observer for charts and heavy components

### Backend Optimization
- **Database Connection Pooling**: SQLAlchemy connection pool configuration
- **Query Optimization**: Proper indexing and query analysis
- **Caching Layer**: Redis for frequently accessed data (future enhancement)
- **Background Tasks**: Celery for heavy processing (future enhancement)
- **Response Compression**: Gzip compression for API responses

### Monitoring and Observability
- **Application Metrics**: Custom metrics for business logic
- **Performance Monitoring**: Response time tracking
- **Error Tracking**: Sentry integration for error monitoring
- **Health Checks**: Kubernetes-style health and readiness probes

## Security Considerations

### Authentication and Authorization
- **JWT Tokens**: Stateless authentication (future enhancement)
- **CORS Configuration**: Proper origin restrictions
- **Rate Limiting**: API endpoint rate limiting
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM usage

### Data Protection
- **Environment Variables**: Sensitive data in environment variables
- **Database Encryption**: Encrypted database connections
- **HTTPS Only**: Force HTTPS in production
- **Security Headers**: Proper HTTP security headers
- **Dependency Scanning**: Regular security updates

## Deployment Architecture

### Docker Configuration
- **Multi-stage Builds**: Optimized Docker images
- **Health Checks**: Container health monitoring
- **Resource Limits**: Memory and CPU constraints
- **Non-root User**: Security best practices

### AWS ECS Compatibility
- **Task Definitions**: ECS-compatible container configurations
- **Service Discovery**: ECS service mesh integration
- **Load Balancing**: Application Load Balancer configuration
- **Auto Scaling**: ECS service auto-scaling policies
- **Logging**: CloudWatch logs integration

### Environment Management
- **Development**: Local Docker Compose setup
- **Staging**: ECS with reduced resources
- **Production**: ECS with high availability and monitoring
- **Configuration**: Environment-specific settings management