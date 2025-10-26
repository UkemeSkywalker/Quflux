.PHONY: help build up down logs clean setup-venv install-backend install-frontend dev-backend dev-frontend celery-worker celery-beat test-setup test-db-config setup-env dev-setup docker-dev

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

clean: ## Clean up Docker containers and volumes
	docker-compose down -v
	docker system prune -f

setup-venv: ## Create Python virtual environment
	python3 -m venv backend/venv
	@echo "Virtual environment created at backend/venv"
	@echo "Activate with: source backend/venv/bin/activate"

install-backend: setup-venv ## Install backend dependencies in virtual environment
	backend/venv/bin/pip install --upgrade pip
	backend/venv/bin/pip install -r backend/requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

dev-backend: ## Run backend in development mode
	cd backend && ./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

celery-worker: ## Run Celery worker
	cd backend && ./venv/bin/celery -A celery_app worker --loglevel=info

celery-beat: ## Run Celery beat scheduler
	cd backend && ./venv/bin/celery -A celery_app beat --loglevel=info

test-setup: ## Test backend setup
	cd backend && ./venv/bin/python test_setup.py

test-db-config: ## Test database configuration
	./backend/venv/bin/python backend/test_db_config.py

setup-env: ## Copy environment files
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "Environment files created. Please update them with your configuration."

dev-setup: setup-env install-backend install-frontend ## Complete development setup
	@echo "Development setup complete!"

docker-dev: build up ## Start development environment with Docker
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"