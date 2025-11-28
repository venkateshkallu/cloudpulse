# CloudPulse Monitor

A real-time cloud monitoring dashboard built with React, FastAPI, and PostgreSQL.

## Overview

CloudPulse Monitor is a comprehensive full-stack monitoring application that provides real-time insights into your cloud infrastructure. It features a modern React frontend with a FastAPI backend and PostgreSQL database for persistent data storage.

## Features

- **Real-time Metrics**: Monitor CPU usage, memory consumption, network traffic, and container status
- **Service Monitoring**: Track service uptime, status, and health checks
- **Log Management**: View and filter system logs with different severity levels
- **Dashboard Analytics**: Visual charts and performance indicators
- **Responsive Design**: Modern UI built with Tailwind CSS and shadcn/ui components

## Architecture

```
cloudpulse-monitor/
├── frontend/          # React + Vite + TypeScript frontend
├── backend/           # FastAPI backend with PostgreSQL
├── docker-compose.yml # Container orchestration
└── README.md
```

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **React Query** for data fetching
- **React Router** for navigation
- **Recharts** for data visualization

### Backend
- **FastAPI** for high-performance API
- **SQLAlchemy** for database ORM
- **PostgreSQL** for data persistence
- **Pydantic** for data validation
- **Background Tasks** for real-time simulation

### Infrastructure
- **Docker** for containerization
- **Docker Compose** for local development
- **AWS ECS** ready for production deployment

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cloudpulse-monitor
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
   The API will be available at http://localhost:8000

### Docker Development

```bash
docker-compose up --build
```

This will start:
- Frontend at http://localhost:5173
- Backend API at http://localhost:8000
- PostgreSQL database at localhost:5432

## API Endpoints

- `GET /api/metrics` - System performance metrics
- `GET /api/services` - Service status and uptime
- `GET /api/logs` - System logs with filtering
- `GET /api/status` - Overall system health

## Development

### Project Structure
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── layouts/       # Layout components
│   ├── hooks/         # Custom React hooks
│   ├── utils/         # Utility functions
│   ├── types/         # TypeScript type definitions
│   └── assets/        # Static assets
├── public/            # Public assets
└── package.json

backend/
├── app/
│   ├── routes/        # API route handlers
│   ├── models.py      # Database models
│   ├── schemas.py     # Pydantic schemas
│   ├── database.py    # Database configuration
│   └── main.py        # FastAPI application
├── requirements.txt
└── Dockerfile
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://admin:admin@localhost:5432/cloudpulse
CORS_ORIGINS=http://localhost:5173
DEBUG=true
```

## Deployment

### AWS ECS Deployment

The application is designed to be deployed on AWS ECS with the following components:

- **Application Load Balancer** for traffic distribution
- **ECS Services** for frontend and backend containers
- **RDS PostgreSQL** for managed database
- **CloudWatch** for logging and monitoring

Refer to the deployment documentation for detailed ECS setup instructions.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.