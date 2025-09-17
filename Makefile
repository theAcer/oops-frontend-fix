# Makefile for Zidisha Loyalty Platform

.PHONY: dev prod up down build clean logs logs-api logs-frontend db-shell test-backend test-file

# Start development environment
dev:
	docker-compose --profile dev -f docker-compose.yml up --build --remove-orphans --wait

# Start production environment
prod:
	docker-compose --profile production -f docker-compose.yml up --build --remove-orphans --wait

# Bring up all services (default to dev profile)
up:
	docker-compose --profile dev -f docker-compose.yml up --build --remove-orphans --wait

# Bring down all services
down:
	docker-compose -f docker-compose.yml down --remove-orphans

# Build all services
build:
	docker-compose -f docker-compose.yml build

# Clean up Docker resources
clean:
	docker-compose -f docker-compose.yml down --volumes --rmi all --remove-orphans

# View logs for all services
logs:
	docker-compose -f docker-compose.yml logs -f

# View logs for API service
logs-api:
	docker-compose -f docker-compose.yml logs -f api

# View logs for Frontend service
logs-frontend:
	docker-compose -f docker-compose.yml logs -f frontend

# Access PostgreSQL database shell
db-shell:
	docker-compose -f docker-compose.yml exec db psql -U postgres zidisha_db

# Run backend tests in a dedicated container
test-backend:
	docker-compose --profile test -f docker-compose.yml up --build --remove-orphans --exit-code-from test test

# Run a specific backend test file in a dedicated container
test-file:
	docker-compose --profile test -f docker-compose.yml run --rm test pytest $(FILE)