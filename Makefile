.PHONY: help install install-backend install-frontend \
        dev-backend dev-frontend \
        lint lint-backend lint-frontend \
        format format-backend format-frontend \
        typecheck test test-backend test-frontend \
        build clean

help:
	@echo "Common targets:"
	@echo "  install            Install backend (dev) and frontend dependencies"
	@echo "  dev-backend        Run the FastAPI dev server on :8000"
	@echo "  dev-frontend       Run the CRA dev server on :3000"
	@echo "  lint               Run all linters (backend + frontend)"
	@echo "  format             Auto-format all code (backend + frontend)"
	@echo "  typecheck          Run mypy on the backend"
	@echo "  test               Run backend and frontend test suites"
	@echo "  build              Build the frontend for production"
	@echo "  clean              Remove caches and build artifacts"

# -------- install --------

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements-dev.txt

install-frontend:
	cd frontend && npm install

# -------- dev servers --------

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm start

# -------- lint / format --------

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check .

lint-frontend:
	cd frontend && npm run lint

format: format-backend format-frontend

format-backend:
	cd backend && ruff format . && ruff check --fix .

format-frontend:
	cd frontend && npm run format

typecheck:
	cd backend && mypy app

# -------- tests --------

test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test -- --watchAll=false

# -------- build --------

build:
	cd frontend && npm run build

# -------- clean --------

clean:
	rm -rf backend/.ruff_cache backend/.mypy_cache backend/.pytest_cache
	find backend -type d -name __pycache__ -exec rm -rf {} +
	rm -rf frontend/build frontend/coverage
