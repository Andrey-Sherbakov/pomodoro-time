.DEFAULT_GOAL := help

HOST ?= 127.0.0.1
PORT ?= 8000
M ?= migration

# FastAPI
run: ## Run the application using uvicorn with provided arguments or defaults
	uv run uvicorn src.main:app --host $(HOST) --port $(PORT) --reload

run-prod: ## Run the application using gunicorn with provided arguments or defaults
	uv run gunicorn main:app -c infra/gunicorn.conf.py

migrate-create: ## Make alembic migrations
	@echo "Making migrations with message $(M)"
	alembic revision --autogenerate -m $(M)

migrate: ## Apply latest alembic migration
	@echo "Migrating"
	alembic upgrade head

install:  ## Install a dependency using poetry
	@echo "Installing dependency $(LIBRARY)"
	uv add $(LIBRARY)

uninstall: ## Uninstall a dependency using poetry
	@echo "Uninstalling dependency $(LIBRARY)"
	uv remove $(LIBRARY)

# Docker
base-up: ## Start base docker containers with postgres, redis and broker
	@echo "Base containers starting"
	docker compose -f docker-compose.base.yml --env-file .local.env up -d

base-down: ## Close base docker containers with postgres, redis and broker
	@echo "Base containers closing"
	docker compose -f docker-compose.base.yml --env-file .local.env down

dev-up: ## Start docker dev containers
	@echo "Starting dev containers"
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml --env-file .dev.env up -d --build

dev-logs: ## Monitor logs in the app container
	@echo "Starting app container monitoring"
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml --env-file .dev.env logs -f app

dev-down: ## Close docker dev containers
	@echo "Closing dev containers"
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml --env-file .dev.env down

test-up: ## Start docker containers with test postgres and redis
	@echo "Test database containers starting"
	docker compose -f docker-compose.test.yml --env-file .test.env up -d

test-down: ## Close docker containers with test postgres and redis
	@echo "Test database containers closing"
	docker compose -f docker-compose.test.yml --env-file .test.env down

# Help
help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands: "
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'