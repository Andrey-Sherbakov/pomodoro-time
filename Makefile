.DEFAULT_GOAL := help

HOST ?= 127.0.0.1
PORT ?= 8000
M ?= migration

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

dev-db-up: ## Start docker containers with dev postgres and redis
	@echo "Dev database containers starting"
	docker compose -f docker-compose.dev.yml --env-file .dev.env up -d

dev-db-down: ## Close docker containers with dev postgres and redis
	@echo "Dev database containers closing"
	docker compose -f docker-compose.dev.yml --env-file .dev.env down

test-db-up: ## Start docker containers with test postgres and redis
	@echo "Test database containers starting"
	docker compose -f docker-compose.test.yml --env-file .test.env up -d

test-db-down: ## Close docker containers with test postgres and redis
	@echo "Test database containers closing"
	docker compose -f docker-compose.test.yml --env-file .test.env down

help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands: "
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'