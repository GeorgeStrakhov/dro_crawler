#!/bin/bash

# Docker Development Helper Script for Firecrawl Crawler

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [[ ! -f .env ]]; then
        print_error ".env file not found!"
        echo "Please create a .env file with:"
        echo "FIRECRAWL_API_KEY=fc-your-api-key-here"
        echo "ADMIN_PASSWORD=your-admin-password"
        exit 1
    fi
    print_success ".env file found"
}

# Help function
show_help() {
    echo "🔥 Firecrawl Crawler - Docker Development Helper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development environment with auto-reload"
    echo "  prod        Start production-like environment for testing"
    echo "  build       Build Docker images"
    echo "  rebuild     Rebuild Docker images from scratch"
    echo "  logs        Show logs from running containers"
    echo "  stop        Stop all containers"
    echo "  clean       Stop containers and remove images"
    echo "  shell       Open shell in development container"
    echo "  test        Run a quick test of both environments"
    echo "  help        Show this help message"
    echo ""
    echo "Development URLs:"
    echo "  Dev environment:  http://localhost:8000"
    echo "  Prod environment: http://localhost:8001"
}

# Start development environment
start_dev() {
    print_status "Starting development environment..."
    check_env
    docker-compose up --build app-dev
}

# Start production environment
start_prod() {
    print_status "Starting production-like environment..."
    check_env
    docker-compose up --build app-prod
}

# Build images
build_images() {
    print_status "Building Docker images..."
    docker-compose build
    print_success "Images built successfully"
}

# Rebuild images from scratch
rebuild_images() {
    print_status "Rebuilding Docker images from scratch..."
    docker-compose build --no-cache
    print_success "Images rebuilt successfully"
}

# Show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f
}

# Stop containers
stop_containers() {
    print_status "Stopping containers..."
    docker-compose down
    print_success "Containers stopped"
}

# Clean up
clean_up() {
    print_status "Cleaning up containers and images..."
    docker-compose down --rmi all --volumes --remove-orphans
    print_success "Cleanup complete"
}

# Open shell in dev container
open_shell() {
    print_status "Opening shell in development container..."
    if ! docker-compose ps app-dev | grep -q "Up"; then
        print_warning "Development container not running, starting it..."
        docker-compose up -d app-dev
        sleep 5
    fi
    docker-compose exec app-dev /bin/bash
}

# Test both environments
test_environments() {
    print_status "Testing both environments..."
    check_env
    
    # Start both services in background
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Test dev environment
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Development environment is healthy (http://localhost:8000)"
    else
        print_error "Development environment health check failed"
    fi
    
    # Test prod environment
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        print_success "Production environment is healthy (http://localhost:8001)"
    else
        print_error "Production environment health check failed"
    fi
    
    print_status "Both environments are running. Press Ctrl+C to stop."
    docker-compose logs -f
}

# Main script logic
case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    build)
        build_images
        ;;
    rebuild)
        rebuild_images
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_containers
        ;;
    clean)
        clean_up
        ;;
    shell)
        open_shell
        ;;
    test)
        test_environments
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 