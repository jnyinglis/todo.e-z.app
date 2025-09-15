# Vite+React+FastAPI+PostgreSQL Template
# Development Makefile

.PHONY: help setup install dev dev-build prod test clean lint type-check build health logs stop restart

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)Vite+React+FastAPI+PostgreSQL Template$(RESET)"
	@echo "======================================"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup: ## Complete project setup (install dependencies, setup environments)
	@echo "$(BLUE)🚀 Setting up development environment...$(RESET)"
	@./scripts/setup.sh

install: ## Install all dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(RESET)"
	@pnpm install
	@cd frontend && pnpm install
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

install-backend: ## Setup Python backend environment
	@echo "$(BLUE)🐍 Setting up Python backend...$(RESET)"
	@cd backend && python -m venv venv
	@cd backend && ./venv/bin/pip install -r requirements.txt
	@echo "$(GREEN)✅ Backend environment ready$(RESET)"

dev: ## Start development environment with hot reload
	@echo "$(BLUE)🔥 Starting development environment...$(RESET)"
	@docker-compose -f docker-compose.dev.yml up

dev-build: ## Start development environment and rebuild containers
	@echo "$(BLUE)🔨 Building and starting development environment...$(RESET)"
	@docker-compose -f docker-compose.dev.yml up --build

prod: ## Start production environment
	@echo "$(BLUE)🚀 Starting production environment...$(RESET)"
	@docker-compose -f docker-compose.prod.yml up -d

test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests...$(RESET)"
	@pnpm run test

test-frontend: ## Run frontend tests
	@echo "$(BLUE)🧪 Running frontend tests...$(RESET)"
	@cd frontend && pnpm test

test-backend: ## Run backend tests
	@echo "$(BLUE)🧪 Running backend tests...$(RESET)"
	@cd backend && python -m pytest

lint: ## Run linting for all code
	@echo "$(BLUE)🔍 Running linters...$(RESET)"
	@pnpm run lint

lint-fix: ## Fix linting issues automatically
	@echo "$(BLUE)🔧 Fixing lint issues...$(RESET)"
	@cd frontend && pnpm run lint --fix
	@echo "$(GREEN)✅ Linting completed$(RESET)"

type-check: ## Run type checking
	@echo "$(BLUE)📋 Running type checks...$(RESET)"
	@pnpm run type-check
	@cd backend && python run_checks.py

build: ## Build production images locally
	@echo "$(BLUE)🏗️  Building production images...$(RESET)"
	@docker build -t template-frontend ./frontend
	@docker build -t template-backend ./backend
	@echo "$(GREEN)✅ Images built$(RESET)"

health: ## Check health of running services
	@echo "$(BLUE)🏥 Checking service health...$(RESET)"
	@curl -f http://localhost:8000/api/health && echo "$(GREEN)✅ Backend healthy$(RESET)" || echo "$(RED)❌ Backend unhealthy$(RESET)"
	@curl -f http://localhost:5173 > /dev/null 2>&1 && echo "$(GREEN)✅ Frontend healthy$(RESET)" || echo "$(RED)❌ Frontend unhealthy$(RESET)"

logs: ## Show logs from all services
	@docker-compose -f docker-compose.dev.yml logs -f

logs-backend: ## Show backend logs only
	@docker-compose -f docker-compose.dev.yml logs -f backend

logs-frontend: ## Show frontend logs only
	@docker-compose -f docker-compose.dev.yml logs -f frontend

logs-db: ## Show database logs only
	@docker-compose -f docker-compose.dev.yml logs -f db

stop: ## Stop all running services
	@echo "$(YELLOW)🛑 Stopping services...$(RESET)"
	@docker-compose -f docker-compose.dev.yml down
	@docker-compose -f docker-compose.prod.yml down
	@echo "$(GREEN)✅ Services stopped$(RESET)"

restart: ## Restart development services
	@echo "$(YELLOW)🔄 Restarting services...$(RESET)"
	@docker-compose -f docker-compose.dev.yml restart
	@echo "$(GREEN)✅ Services restarted$(RESET)"

clean: ## Clean up containers, volumes, and dependencies
	@echo "$(YELLOW)🧹 Cleaning up...$(RESET)"
	@docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	@docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	@docker system prune -f
	@rm -rf node_modules frontend/node_modules backend/venv
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

reset: ## Complete reset (clean + setup)
	@echo "$(BLUE)🔄 Performing complete reset...$(RESET)"
	@$(MAKE) clean
	@$(MAKE) setup

ps: ## Show status of all services
	@echo "$(BLUE)📊 Service Status:$(RESET)"
	@docker-compose -f docker-compose.dev.yml ps

shell-backend: ## Open shell in backend container
	@docker-compose -f docker-compose.dev.yml exec backend bash

shell-frontend: ## Open shell in frontend container
	@docker-compose -f docker-compose.dev.yml exec frontend sh

shell-db: ## Open PostgreSQL shell
	@docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d template_db

generate-types: ## Generate TypeScript types from OpenAPI
	@echo "$(BLUE)📝 Generating TypeScript types...$(RESET)"
	@cd backend && source venv/bin/activate && python generate_types.py
	@echo "$(GREEN)✅ Types generated$(RESET)"

migrate: ## Run database migrations
	@echo "$(BLUE)📊 Running database migrations...$(RESET)"
	@docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
	@echo "$(GREEN)✅ Migrations completed$(RESET)"

migration-create: ## Create a new migration (requires message, e.g. make migration-create MESSAGE="Add user preferences")
	@echo "$(BLUE)📝 Creating new migration...$(RESET)"
	@docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "$(MESSAGE)"
	@echo "$(GREEN)✅ Migration created$(RESET)"

migration-history: ## Show migration history
	@echo "$(BLUE)📜 Migration history:$(RESET)"
	@docker-compose -f docker-compose.dev.yml exec backend alembic history

migration-current: ## Show current migration
	@echo "$(BLUE)📍 Current migration:$(RESET)"
	@docker-compose -f docker-compose.dev.yml exec backend alembic current

migration-rollback: ## Rollback to previous migration
	@echo "$(YELLOW)⏪ Rolling back migration...$(RESET)"
	@docker-compose -f docker-compose.dev.yml exec backend alembic downgrade -1
	@echo "$(GREEN)✅ Rollback completed$(RESET)"

seed: ## Seed database with sample data
	@echo "$(BLUE)🌱 Seeding database...$(RESET)"
	@# Add seed script here when created
	@echo "$(YELLOW)⚠️  Seed script not implemented yet$(RESET)"

backup-db: ## Backup database
	@echo "$(BLUE)💾 Backing up database...$(RESET)"
	@docker-compose -f docker-compose.dev.yml exec db pg_dump -U postgres template_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backed up$(RESET)"