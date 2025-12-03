# CloudPulse Monitor - Docker Compose Management
# Usage: make [target]

.PHONY: help build up down restart logs clean dev prod test

# Default target
help: ## Show this help message
	@echo "CloudPulse Monitor - Docker Compose Commands"
	@echo "==========================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development commands
dev: ## Start development environment
	docker compose up -d
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev-build: ## Build and start development environment
	docker compose up -d --build
	@echo "Development environment built and started!"

dev-logs: ## Show development logs
	docker compose logs -f

dev-stop: ## Stop development environment
	docker compose down

# Production commands
prod: ## Start production environment
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production environment started!"

prod-build: ## Build and start production environment
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
	@echo "Production environment built and started!"

prod-logs: ## Show production logs
	docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-stop: ## Stop production environment
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# General commands
build: ## Build all services
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Show logs for all services
	docker compose logs -f

# Service-specific commands
logs-frontend: ## Show frontend logs
	docker compose logs -f frontend

logs-backend: ## Show backend logs
	docker compose logs -f backend

logs-postgres: ## Show postgres logs
	docker compose logs -f postgres

# Database commands
db-shell: ## Connect to PostgreSQL shell
	docker compose exec postgres psql -U postgres -d cloudpulse

db-reset: ## Reset database (WARNING: destroys all data)
	docker compose down -v
	docker volume rm cloudpulse_postgres_data 2>/dev/null || true
	docker compose up -d postgres
	@echo "Database reset complete!"

# Maintenance commands
clean: ## Clean up containers, networks, and volumes
	docker compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup complete!"

clean-all: ## Clean up everything including images
	docker compose down -v --remove-orphans --rmi all
	docker system prune -af
	@echo "Full cleanup complete!"

# Health checks
health: ## Check service health
	@echo "Checking service health..."
	@docker compose ps
	@echo ""
	@echo "Frontend health:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 || echo "Frontend not responding"
	@echo ""
	@echo "Backend health:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/status || echo "Backend not responding"

# Testing
test: ## Run tests in containers
	docker compose exec backend python -m pytest
	@echo "Backend tests completed!"

# Development utilities
shell-backend: ## Open shell in backend container
	docker compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend /bin/sh

shell-postgres: ## Open shell in postgres container
	docker compose exec postgres /bin/bash

# Quick setup
setup: ## Initial setup for new developers
	@echo "Setting up CloudPulse Monitor development environment..."
	@cp .env .env.local 2>/dev/null || echo ".env.local already exists"
	@echo "Building and starting services..."
	@make dev-build
	@echo ""
	@echo "Setup complete! Services are starting..."
	@echo "Frontend: http://localhost:5173"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Use 'make logs' to see startup logs"
	@echo "Use 'make help' to see all available commands"