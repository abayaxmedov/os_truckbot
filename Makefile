# Use the docker compose plugin if present, else fall back to standalone docker-compose
COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

.PHONY: help db-up db-down up down logs migrate revision seed dev backend-install test fmt miniapp-install miniapp-dev miniapp-build

help:
	@echo "Targets:"
	@echo "  db-up            Start only PostgreSQL (docker)"
	@echo "  up               Start full stack (db + backend) via docker compose"
	@echo "  down             Stop the stack"
	@echo "  logs             Tail backend logs"
	@echo "  migrate          Apply DB migrations (alembic upgrade head)"
	@echo "  revision m=msg   Autogenerate a new migration"
	@echo "  seed             Load seed data (brands, categories, demo)"
	@echo "  dev              Run backend locally with reload (needs local .env + db-up)"
	@echo "  backend-install  Create venv and install backend deps"
	@echo "  test             Run backend pytest suite"
	@echo "  miniapp-install  npm install for the Mini App"
	@echo "  miniapp-dev      Run the Mini App dev server (vite)"
	@echo "  miniapp-build    Build the Mini App for production"

# ---- Docker ----
db-up:
	$(COMPOSE) up -d db

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f backend

# ---- Backend (local) ----
backend-install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

migrate:
	cd backend && alembic upgrade head

revision:
	cd backend && alembic revision --autogenerate -m "$(m)"

seed:
	cd backend && python -m app.seed.run

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8010

test:
	cd backend && pytest -q

fmt:
	cd backend && ruff check --fix . && ruff format .

# ---- Mini App ----
miniapp-install:
	cd miniapp && npm install

miniapp-dev:
	cd miniapp && npm run dev

miniapp-build:
	cd miniapp && npm run build
