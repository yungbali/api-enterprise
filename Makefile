# Enterprise Suite API - Docker Management
.PHONY: help build up down restart logs shell test clean migrate seed backup restore

# Default target
help:
	@echo "Enterprise Suite API - Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  help          Show this help message"
	@echo "  build         Build Docker images"
	@echo "  up            Start all services"
	@echo "  down          Stop all services"
	@echo "  restart       Restart all services"
	@echo "  logs          Show logs for all services"
	@echo "  shell         Access API container shell"
	@echo "  test          Run tests"
	@echo "  clean         Remove containers and volumes"
	@echo "  migrate       Run database migrations"
	@echo "  seed          Seed database with sample data"
	@echo "  backup        Backup database"
	@echo "  restore       Restore database from backup"
	@echo "  monitoring    Start monitoring stack only"
	@echo "  prod          Deploy production environment"
	@echo ""

# Development Environment
build:
	@echo "Building Docker images..."
	docker-compose build --no-cache

up:
	@echo "Starting development environment..."
	docker-compose --env-file .env.docker up -d
	@echo "Services are starting up..."
	@echo "API will be available at: http://localhost:8000"
	@echo "API docs at: http://localhost:8000/docs"
	@echo "Flower (Celery monitoring) at: http://localhost:5555"
	@echo "Grafana at: http://localhost:3000 (admin:admin123)"
	@echo "Prometheus at: http://localhost:9090"
	@echo "MinIO at: http://localhost:9001 (minioadmin:minioadmin123)"

down:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	@echo "Showing logs for all services..."
	docker-compose logs -f

logs-api:
	@echo "Showing API logs..."
	docker-compose logs -f api

logs-worker:
	@echo "Showing Celery worker logs..."
	docker-compose logs -f celery-worker

logs-db:
	@echo "Showing database logs..."
	docker-compose logs -f postgres

shell:
	@echo "Accessing API container shell..."
	docker-compose exec api bash

shell-db:
	@echo "Accessing database shell..."
	docker-compose exec postgres psql -U enterprise_user -d enterprise_db

# Testing
test:
	@echo "Running tests..."
	docker-compose exec api pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	docker-compose exec api pytest tests/ --cov=app --cov-report=html --cov-report=term

test-unit:
	@echo "Running unit tests..."
	docker-compose exec api pytest tests/ -v -m unit

test-integration:
	@echo "Running integration tests..."
	docker-compose exec api pytest tests/ -v -m integration

test-e2e:
	@echo "Running end-to-end tests..."
	docker-compose exec api pytest tests/ -v -m e2e

test-performance:
	@echo "Running performance tests..."
	docker-compose exec api pytest tests/ -v -m performance

test-security:
	@echo "Running security tests..."
	docker-compose exec api pytest tests/ -v -m security

test-infrastructure:
	@echo "Testing infrastructure setup..."
	docker-compose exec api pytest tests/test_infrastructure.py -v

# Test Environment Management
test-env-up:
	@echo "Starting test environment..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "Test services are starting up..."
	@echo "Test API will be available at: http://localhost:8001"
	@echo "Test database at: localhost:5433"
	@echo "Test Redis at: localhost:6380"

test-env-down:
	@echo "Stopping test environment..."
	docker-compose -f docker-compose.test.yml down

test-env-logs:
	@echo "Showing test environment logs..."
	docker-compose -f docker-compose.test.yml logs -f

test-env-shell:
	@echo "Accessing test runner shell..."
	docker-compose -f docker-compose.test.yml exec test-runner bash

test-standalone:
	@echo "Running tests in standalone test environment..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	docker-compose -f docker-compose.test.yml exec test-runner pytest tests/ -v
	docker-compose -f docker-compose.test.yml down

test-local:
	@echo "Running tests locally (requires local services)..."
	@export ENVIRONMENT=testing && \
	export DATABASE_URL=postgresql://enterprise_test_user:enterprise_test_pass@localhost:5433/enterprise_test_db && \
	export REDIS_URL=redis://localhost:6380/0 && \
	pytest tests/ -v

# Database Management
migrate:
	@echo "Running database migrations..."
	docker-compose exec api alembic upgrade head

migrate-create:
	@echo "Creating new migration..."
	@read -p "Enter migration message: " msg; \
	docker-compose exec api alembic revision --autogenerate -m "$$msg"

seed:
	@echo "Seeding database with sample data..."
	docker-compose exec api python -c "from app.core.seed import seed_database; seed_database()"

# Backup and Restore
backup:
	@echo "Creating database backup..."
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U enterprise_user enterprise_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/"

restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T postgres psql -U enterprise_user -d enterprise_db < "$$backup_file"

# Monitoring
monitoring:
	@echo "Starting monitoring stack..."
	docker-compose up -d prometheus grafana
	@echo "Monitoring services started:"
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"

# Production Environment
prod:
	@echo "Deploying production environment..."
	@if [ ! -f .env.docker.prod ]; then \
		echo "Error: .env.docker.prod file not found"; \
		echo "Please create .env.docker.prod with production settings"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml --env-file .env.docker.prod up -d --build

prod-down:
	@echo "Stopping production environment..."
	docker-compose -f docker-compose.prod.yml down

# Cleanup
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup complete"

clean-all:
	@echo "Cleaning up all Docker resources (including images)..."
	docker-compose down -v --remove-orphans
	docker system prune -af
	@echo "Full cleanup complete"

# Health Checks
health:
	@echo "Checking service health..."
	@echo "API Health:"
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo ""
	@echo "Database Health:"
	@docker-compose exec postgres pg_isready -U enterprise_user
	@echo ""
	@echo "Redis Health:"
	@docker-compose exec redis redis-cli ping

# Development Utilities
format:
	@echo "Formatting code..."
	docker-compose exec api black app/ tests/
	docker-compose exec api isort app/ tests/

lint:
	@echo "Linting code..."
	docker-compose exec api flake8 app/ tests/

type-check:
	@echo "Running type checks..."
	docker-compose exec api mypy app/

security-check:
	@echo "Running security checks..."
	docker-compose exec api bandit -r app/

# Documentation
docs:
	@echo "Generating API documentation..."
	@echo "API docs available at: http://localhost:8000/docs"
	@echo "ReDoc available at: http://localhost:8000/redoc"

# Quick Start
quickstart: build up migrate seed
	@echo "Quick start complete!"
	@echo "Your Enterprise Suite API is ready at:"
	@echo "  API: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"
	@echo "  Monitoring: http://localhost:3000"

# Update and Rebuild
update:
	@echo "Updating and rebuilding services..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Services updated and restarted"
