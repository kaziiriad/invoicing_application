#!/bin/bash

# InvoiceFlow Docker Development Helper Script

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to build and start services
start_services() {
    print_status "Building and starting InvoiceFlow services..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "Services started successfully!"
    print_status "Services available at:"
    echo "  🌐 Frontend (React): http://localhost:80"
    echo "  🔧 Backend API: http://localhost:80/api/"
    echo "  📚 API Docs (Swagger): http://localhost:80/swagger/"
    echo "  📖 API Docs (ReDoc): http://localhost:80/redoc/"
    echo "  🗄️  Database: localhost:5432"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop services: ./docker-dev.sh stop"
}

# Function to stop services
stop_services() {
    print_status "Stopping InvoiceFlow services..."
    docker-compose down
    print_success "Services stopped successfully!"
}

# Function to restart services
restart_services() {
    print_status "Restarting InvoiceFlow services..."
    docker-compose restart
    print_success "Services restarted successfully!"
}

# Function to view logs
view_logs() {
    if [ -n "$2" ]; then
        print_status "Viewing logs for service: $2"
        docker-compose logs -f "$2"
    else
        print_status "Viewing logs for all services..."
        docker-compose logs -f
    fi
}

# Function to run backend commands
backend_cmd() {
    if [ -z "$2" ]; then
        print_error "Please provide a command to run in the backend container"
        echo "Example: ./docker-dev.sh backend 'python manage.py migrate'"
        exit 1
    fi
    
    print_status "Running backend command: $2"
    docker-compose exec backend bash -c "cd /app/backend && $2"
}

# Function to run frontend commands
frontend_cmd() {
    if [ -z "$2" ]; then
        print_error "Please provide a command to run in the frontend container"
        echo "Example: ./docker-dev.sh frontend 'npm run build'"
        exit 1
    fi
    
    print_status "Running frontend command: $2"
    docker-compose exec frontend sh -c "cd /app && $2"
}

# Function to show service status
status() {
    print_status "InvoiceFlow service status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "InvoiceFlow Docker Development Helper"
    echo ""
    echo "Usage: ./docker-dev.sh [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start, up        Build and start all services"
    echo "  stop, down       Stop all services"
    echo "  restart          Restart all services"
    echo "  status, ps       Show service status"
    echo "  logs [service]   View logs (optionally for specific service)"
    echo "  backend 'cmd'    Run command in backend container"
    echo "  frontend 'cmd'   Run command in frontend container"
    echo "  cleanup          Stop services and clean up Docker resources"
    echo "  help, -h, --help Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker-dev.sh start"
    echo "  ./docker-dev.sh logs nginx"
    echo "  ./docker-dev.sh backend 'python manage.py migrate'"
    echo "  ./docker-dev.sh frontend 'npm run build'"
    echo ""
    echo "Quick Setup:"
    echo "  1. Make script executable: chmod +x docker-dev.sh"
    echo "  2. Start services: ./docker-dev.sh start"
    echo "  3. Open browser: http://localhost:80"
}

# Main script logic
main() {
    check_docker
    
    case "${1:-help}" in
        start|up)
            start_services
            ;;
        stop|down)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            view_logs "$@"
            ;;
        backend)
            backend_cmd "$@"
            ;;
        frontend)
            frontend_cmd "$@"
            ;;
        status|ps)
            status
            ;;
        cleanup)
            cleanup
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"