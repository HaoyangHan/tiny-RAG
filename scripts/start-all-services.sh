#!/bin/bash

# TinyRAG v1.4.1 Complete Service Startup Script
# This script starts all TinyRAG services in the correct order

set -e

echo "🚀 Starting TinyRAG v1.4.1 Complete Stack..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Change to project root
cd "$(dirname "$0")/.."

# Step 1: Start Database Services
print_info "Step 1: Starting database services..."
cd rag-memo-api
docker-compose up -d tinyrag-mongodb tinyrag-redis tinyrag-qdrant
print_status "Database services started"

# Step 2: Wait for databases to be healthy
print_info "Step 2: Waiting for databases to be healthy..."
sleep 10
docker-compose ps | grep healthy
print_status "Databases are healthy"

# Step 3: Start API Service
print_info "Step 3: Starting API service..."
docker-compose up -d tinyrag-api
print_status "API service started"

# Step 4: Wait for API to be healthy
print_info "Step 4: Waiting for API to be healthy..."
sleep 30
API_STATUS=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "unhealthy")
if [[ "$API_STATUS" == *"healthy"* ]]; then
    print_status "API is healthy"
else
    print_error "API is not healthy, but continuing..."
fi

# Step 5: Start Frontend (Manual for now due to Docker build issues)
print_info "Step 5: Starting frontend service..."
cd ../rag-memo-ui

# Kill any existing dev server
pkill -f "npm run dev" || true
sleep 2

# Start frontend in background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
print_status "Frontend service started (PID: $FRONTEND_PID)"

# Step 6: Wait for frontend to be ready
print_info "Step 6: Waiting for frontend to be ready..."
sleep 15

# Test frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [[ "$FRONTEND_STATUS" == "200" ]]; then
    print_status "Frontend is ready"
else
    print_warning "Frontend may still be starting..."
fi

# Step 7: Final Status Check
print_info "Step 7: Final status check..."
echo ""
echo "🔍 Service Status:"
echo "=================="

# Check API
API_HEALTH=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo "error")
if [[ "$API_HEALTH" == "healthy" ]]; then
    print_status "API: Healthy (http://localhost:8000)"
else
    print_warning "API: May need more time to start"
fi

# Check Frontend
FRONTEND_RESPONSE=$(curl -s http://localhost:3000 | grep -o "TinyRAG\|Create Next App" | head -1 2>/dev/null || echo "error")
if [[ "$FRONTEND_RESPONSE" != "error" ]]; then
    print_status "Frontend: Ready (http://localhost:3000)"
else
    print_warning "Frontend: Still starting up"
fi

# Check Docker Services
echo ""
echo "📊 Docker Services:"
cd ../rag-memo-api
docker-compose ps

echo ""
echo "🎉 TinyRAG v1.4.1 Startup Complete!"
echo "===================================="
echo "📊 API Dashboard: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs" 
echo "🌐 Frontend Application: http://localhost:3000"
echo "📈 API Health Check: http://localhost:8000/health"
echo ""
print_info "All services are now running. Check the logs if any issues occur."
print_info "Frontend logs: logs/frontend.log"
print_info "Docker logs: docker-compose logs [service-name]" 