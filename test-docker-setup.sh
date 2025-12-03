#!/bin/bash

# CloudPulse Monitor - Docker Setup Test Script
# This script tests that all services are running correctly

echo "🚀 Testing CloudPulse Monitor Docker Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo -n "Testing $name... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $status, expected $expected_status)"
        return 1
    fi
}

# Test service health
test_service_health() {
    local service=$1
    echo -n "Checking $service health... "
    
    health=$(docker compose ps --format json | jq -r ".[] | select(.Service==\"$service\") | .Health")
    
    if [ "$health" = "healthy" ]; then
        echo -e "${GREEN}✓ HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}✗ UNHEALTHY${NC} ($health)"
        return 1
    fi
}

# Check if Docker Compose is running
echo "Checking Docker Compose services..."
if ! docker compose ps >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker Compose services not running${NC}"
    echo "Run 'docker compose up -d' first"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose is running${NC}"
echo

# Test service health
echo "Testing service health..."
test_service_health "postgres"
test_service_health "backend" 
test_service_health "frontend"
echo

# Test endpoints
echo "Testing API endpoints..."
test_endpoint "Frontend" "http://localhost:5173" "200"
test_endpoint "Backend Status" "http://localhost:8000/api/status/" "200"
test_endpoint "Backend Metrics" "http://localhost:8000/api/metrics/" "200"
test_endpoint "Backend Services" "http://localhost:8000/api/services/" "200"
test_endpoint "Backend Logs" "http://localhost:8000/api/logs/" "200"
echo

# Test API responses
echo "Testing API response content..."

# Test status endpoint
echo -n "Status endpoint returns JSON... "
status_response=$(curl -s "http://localhost:8000/api/status/")
if echo "$status_response" | jq . >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

# Test metrics endpoint
echo -n "Metrics endpoint returns JSON... "
metrics_response=$(curl -s "http://localhost:8000/api/metrics/")
if echo "$metrics_response" | jq . >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

# Test services endpoint
echo -n "Services endpoint returns array... "
services_response=$(curl -s "http://localhost:8000/api/services/")
if echo "$services_response" | jq 'type == "array"' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo

# Test database connectivity
echo "Testing database connectivity..."
echo -n "Database connection... "
if docker compose exec -T postgres psql -U postgres -d cloudpulse -c "SELECT 1;" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo -n "Sample data exists... "
service_count=$(docker compose exec -T postgres psql -U postgres -d cloudpulse -t -c "SELECT COUNT(*) FROM services;" 2>/dev/null | tr -d ' \n')
if [ "$service_count" -gt "0" ] 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC} ($service_count services)"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo

# Summary
echo "=========================================="
echo "🎉 Docker Setup Test Complete!"
echo
echo "Access URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Database: localhost:5432"
echo
echo "Useful commands:"
echo "  docker compose logs -f          # View all logs"
echo "  docker compose ps               # Check service status"
echo "  make health                     # Run health checks"
echo "  make logs                       # View logs"
echo "  make db-shell                   # Connect to database"