.PHONY: help build up down logs test clean deploy-local deploy-prod

# Default target
help:
	@echo "Available commands:"
	@echo "  build        - Build Docker images"
	@echo "  up           - Start services locally"
	@echo "  down         - Stop services"
	@echo "  logs         - Show logs"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean up containers and images"
	@echo "  deploy-local - Deploy locally with Docker Compose"
	@echo "  deploy-prod  - Deploy to production with Terraform"

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Run tests
test:
	@echo "Running tests..."
	# Add your test commands here
	@echo "Tests completed"

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Deploy locally
deploy-local: build up
	@echo "Services deployed locally"
	@echo "API Gateway: http://localhost:8000"
	@echo "User Manager: http://localhost:8001"

# Deploy to production
deploy-prod:
	cd devops/terraform && terraform init
	cd devops/terraform && terraform plan
	cd devops/terraform && terraform apply

# Install dependencies locally
install:
	pip install -r backend/gateway/requirements.txt
	pip install -r backend/user-manager/requirements.txt

# Format code
format:
	black backend/
	isort backend/

# Lint code
lint:
	flake8 backend/
	black --check backend/
	isort --check-only backend/
