#!/bin/bash

# Complete Development Environment Setup Script
# This script sets up the entire development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 is installed"
        return 0
    else
        log_error "$1 is not installed"
        return 1
    fi
}

# Main setup function
main() {
    echo -e "${BLUE}🚀 Setting up Vite+React+FastAPI+PostgreSQL Template${NC}"
    echo "=============================================="
    echo

    # Check prerequisites
    log_info "Checking prerequisites..."

    missing_deps=()

    if ! check_command "node"; then
        missing_deps+=("node")
    fi

    if ! check_command "pnpm"; then
        missing_deps+=("pnpm")
    fi

    if ! check_command "python3"; then
        missing_deps+=("python3")
    fi

    if ! check_command "docker"; then
        missing_deps+=("docker")
    fi

    if ! check_command "docker-compose"; then
        missing_deps+=("docker-compose")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo
        log_info "Please install the following dependencies:"
        for dep in "${missing_deps[@]}"; do
            case $dep in
                "node")
                    echo "  • Node.js: https://nodejs.org/"
                    ;;
                "pnpm")
                    echo "  • pnpm: npm install -g pnpm"
                    ;;
                "python3")
                    echo "  • Python 3: https://python.org/"
                    ;;
                "docker")
                    echo "  • Docker: https://docker.com/"
                    ;;
                "docker-compose")
                    echo "  • Docker Compose: https://docs.docker.com/compose/"
                    ;;
            esac
        done
        exit 1
    fi

    echo

    # Install root dependencies
    log_info "Installing root dependencies..."
    pnpm install
    log_success "Root dependencies installed"

    # Setup frontend
    log_info "Setting up frontend..."
    cd frontend
    if [ ! -f "package.json" ]; then
        log_error "Frontend package.json not found"
        exit 1
    fi
    pnpm install
    log_success "Frontend dependencies installed"
    cd ..

    # Setup backend
    log_info "Setting up backend Python environment..."
    cd backend

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi

    # Activate virtual environment and install dependencies
    log_info "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Python dependencies installed"

    # Run type checking to verify setup
    log_info "Running type checks..."
    if python -m mypy app --ignore-missing-imports; then
        log_success "Type checking passed"
    else
        log_warning "Type checking found issues (this is normal for initial setup)"
    fi

    cd ..

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please update .env with your actual values!"
        log_info "Key variables to update:"
        echo "  • POSTGRES_PASSWORD"
        echo "  • SECRET_KEY"
        echo "  • GOOGLE_CLIENT_ID (for OAuth)"
        echo "  • DOMAIN (for production)"
    else
        log_info ".env file already exists"
    fi

    # Test Docker setup
    log_info "Testing Docker setup..."
    if docker info &> /dev/null; then
        log_success "Docker is running"

        # Pull required images
        log_info "Pulling required Docker images..."
        docker pull postgres:16
        log_success "Docker images ready"
    else
        log_error "Docker is not running. Please start Docker."
        exit 1
    fi

    # Generate build info for development
    log_info "Generating build information..."
    cd frontend
    node generate-build-info.js
    cd ../backend
    python generate_build_info.py
    cd ..
    log_success "Build information generated"

    echo
    log_success "🎉 Setup complete!"
    echo
    echo -e "${GREEN}Next steps:${NC}"
    echo "  1. Update .env file with your actual values"
    echo "  2. Run 'make dev' or 'pnpm dev' to start development server"
    echo "  3. Visit http://localhost:5173 for frontend"
    echo "  4. Visit http://localhost:8000/docs for API documentation"
    echo
    echo -e "${BLUE}Available commands:${NC}"
    echo "  make help          - Show all available commands"
    echo "  make dev           - Start development environment"
    echo "  make test          - Run all tests"
    echo "  make health        - Check service health"
    echo "  make logs          - View service logs"
    echo "  make stop          - Stop all services"
    echo
    echo -e "${YELLOW}Don't forget to:${NC}"
    echo "  • Set up your Google OAuth credentials"
    echo "  • Configure your email service for magic links"
    echo "  • Review security settings before production deployment"
}

# Run main function
main "$@"