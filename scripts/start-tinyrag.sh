#!/bin/bash

# TinyRAG v1.3 Startup Script
# This script starts all TinyRAG services with proper dependency management

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_docker() {
    log "Checking Docker installation..."
    
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Docker is installed and running"
}

# Function to check environment file
check_environment() {
    log "Checking environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from template..."
        
        if [ -f "$PROJECT_ROOT/env.example" ]; then
            cp "$PROJECT_ROOT/env.example" "$ENV_FILE"
            log_warning "Please edit .env file with your configuration before continuing."
            log_warning "Required: OPENAI_API_KEY, JWT_SECRET_KEY, database passwords"
            
            # Check if we should continue
            read -p "Continue with default values? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log "Please configure .env file and run again."
                exit 1
            fi
        else
            log_error "env.example file not found. Cannot create .env file."
            exit 1
        fi
    fi
    
    # Check for required environment variables
    source "$ENV_FILE"
    
    local missing_vars=()
    
    # Check critical variables
    [ -z "$OPENAI_API_KEY" ] && missing_vars+=("OPENAI_API_KEY")
    [ -z "$JWT_SECRET_KEY" ] && missing_vars+=("JWT_SECRET_KEY")
    [ -z "$MONGO_ROOT_PASSWORD" ] && missing_vars+=("MONGO_ROOT_PASSWORD")
    [ -z "$REDIS_PASSWORD" ] && missing_vars+=("REDIS_PASSWORD")
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            log_error "  - $var"
        done
        log_error "Please configure these variables in .env file"
        exit 1
    fi
    
    log_success "Environment configuration is valid"
}

# Function to create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    local dirs=(
        "$PROJECT_ROOT/data/uploads"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/logs/nginx"
        "$PROJECT_ROOT/nginx/ssl"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "Created directory: $dir"
        fi
    done
    
    log_success "Directories created successfully"
}

# Function to check and pull Docker images
pull_images() {
    log "Pulling Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Pull base images first
    docker pull mongo:7.0
    docker pull redis:7.2-alpine
    docker pull qdrant/qdrant:v1.7.0
    docker pull nginx:1.25-alpine
    
    log_success "Docker images pulled successfully"
}

# Function to build custom images
build_images() {
    log "Building custom Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build images in parallel where possible
    docker-compose build --parallel
    
    log_success "Custom images built successfully"
}

# Function to start services in order
start_services() {
    log "Starting TinyRAG services..."
    
    cd "$PROJECT_ROOT"
    
    # Start infrastructure services first
    log "Starting infrastructure services..."
    docker-compose up -d tinyrag-mongodb tinyrag-redis tinyrag-qdrant
    
    # Wait for infrastructure to be ready
    log "Waiting for infrastructure services to be ready..."
    sleep 30
    
    # Check health of infrastructure services
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Checking infrastructure health (attempt $attempt/$max_attempts)..."
        
        if docker-compose ps | grep -q "unhealthy"; then
            log_warning "Some services are still starting..."
            sleep 10
            ((attempt++))
        else
            break
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Infrastructure services failed to start properly"
        docker-compose logs
        exit 1
    fi
    
    # Start worker service
    log "Starting worker service..."
    docker-compose up -d tinyrag-worker
    
    # Wait for worker to initialize
    sleep 15
    
    # Start API service
    log "Starting API service..."
    docker-compose up -d tinyrag-api
    
    # Wait for API to be ready
    sleep 20
    
    # Start UI service
    log "Starting UI service..."
    docker-compose up -d tinyrag-ui
    
    # Wait for UI to be ready
    sleep 15
    
    log_success "All services started successfully"
}

# Function to check service health
check_health() {
    log "Checking service health..."
    
    cd "$PROJECT_ROOT"
    
    local services=("tinyrag-mongodb" "tinyrag-redis" "tinyrag-qdrant" "tinyrag-worker" "tinyrag-api" "tinyrag-ui")
    local healthy_services=0
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            log_success "$service is running"
            ((healthy_services++))
        else
            log_error "$service is not running"
        fi
    done
    
    # Test API endpoint
    log "Testing API health endpoint..."
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
    fi
    
    # Test UI endpoint
    log "Testing UI endpoint..."
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        log_success "UI health check passed"
    else
        log_error "UI health check failed"
    fi
    
    log "Service health check completed: $healthy_services/${#services[@]} services healthy"
}

# Function to show service information
show_info() {
    log_success "TinyRAG v1.3 is now running!"
    echo
    echo "🌐 Access URLs:"
    echo "  • Frontend UI:      http://localhost:3000"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • API Health:       http://localhost:8000/health"
    echo
    echo "🔐 Default Admin Credentials:"
    echo "  • Email:    admin@tinyrag.local"
    echo "  • Username: admin"
    echo "  • Password: TinyRAG2024!"
    echo "  ⚠️  Please change the default password immediately!"
    echo
    echo "📊 Service Status:"
    docker-compose ps
    echo
    echo "📝 Useful Commands:"
    echo "  • View logs:        docker-compose logs -f"
    echo "  • Stop services:    docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Update services:  docker-compose pull && docker-compose up -d"
    echo
    echo "🆘 Troubleshooting:"
    echo "  • Check logs:       docker-compose logs [service-name]"
    echo "  • Check health:     curl http://localhost:8000/health"
    echo "  • Reset data:       docker-compose down -v"
    echo
}

# Function to handle cleanup on exit
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Startup failed. Cleaning up..."
        cd "$PROJECT_ROOT"
        docker-compose down
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    log "Starting TinyRAG v1.3 setup..."
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run all checks and setup
    check_docker
    check_environment
    create_directories
    pull_images
    build_images
    start_services
    check_health
    show_info
    
    log_success "TinyRAG v1.3 startup completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "TinyRAG v1.3 Startup Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --force        Force restart all services"
        echo "  --rebuild      Rebuild all images before starting"
        echo "  --logs         Show logs after starting"
        echo
        exit 0
        ;;
    --force)
        log "Force restarting all services..."
        cd "$PROJECT_ROOT"
        docker-compose down
        main
        ;;
    --rebuild)
        log "Rebuilding all images..."
        cd "$PROJECT_ROOT"
        docker-compose down
        docker-compose build --no-cache
        main
        ;;
    --logs)
        main
        log "Showing service logs..."
        cd "$PROJECT_ROOT"
        docker-compose logs -f
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 