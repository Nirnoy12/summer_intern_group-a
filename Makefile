# ==============================================================
# Makefile — LMS Project Convenience Commands
# ==============================================================
# Run any target with: make <target>
# Examples:
#   make setup          → full first-time setup (backend + frontend)
#   make dev            → start both servers (requires tmux or 2 terminals)
#   make test           → run all backend tests
#   make verify         → verify both environments
# ==============================================================

# ── Paths ─────────────────────────────────────────────────────
BACKEND_DIR = backend
FRONTEND_DIR = frontend
PYTHON = $(BACKEND_DIR)/venv/Scripts/python  # Windows
# PYTHON = $(BACKEND_DIR)/venv/bin/python    # Mac/Linux (uncomment)
PIP    = $(BACKEND_DIR)/venv/Scripts/pip     # Windows
# PIP  = $(BACKEND_DIR)/venv/bin/pip         # Mac/Linux (uncomment)

.PHONY: help setup setup-backend setup-frontend dev dev-backend dev-frontend \
        test verify lint format typecheck clean

# ── Default target: show help ──────────────────────────────────
help:
	@echo ""
	@echo "  LMS Project — Available Make Targets"
	@echo "  ───────────────────────────────────────────"
	@echo "  make setup           Full first-time setup (backend + frontend)"
	@echo "  make setup-backend   Python venv + pip install"
	@echo "  make setup-frontend  npm install"
	@echo ""
	@echo "  make dev-backend     Start uvicorn (port 8000)"
	@echo "  make dev-frontend    Start Vite dev server (port 5173)"
	@echo ""
	@echo "  make test            Run all backend pytest tests"
	@echo "  make verify          Run both frontend and backend verifiers"
	@echo "  make lint            Lint backend (ruff) + frontend (eslint)"
	@echo "  make format          Auto-format backend code (ruff format)"
	@echo "  make typecheck       TypeScript type check (frontend)"
	@echo ""
	@echo "  make clean           Remove build artifacts"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────
setup: setup-backend setup-frontend
	@echo ""
	@echo "✅ Setup complete!"
	@echo "   Next: fill in backend/.env, then run:"
	@echo "         make dev-backend  (Terminal 1)"
	@echo "         make dev-frontend (Terminal 2)"

setup-backend:
	@echo "── Setting up Python backend ──"
	cd $(BACKEND_DIR) && python -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	$(PIP) install -r $(BACKEND_DIR)/requirements-dev.txt
	@if not exist $(BACKEND_DIR)\.env copy $(BACKEND_DIR)\.env.example $(BACKEND_DIR)\.env && echo "Created backend/.env from template — fill in your values!"

setup-frontend:
	@echo "── Setting up Node.js frontend ──"
	cd $(FRONTEND_DIR) && npm install

# ── Dev Servers ───────────────────────────────────────────────
dev-backend:
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn main:app --reload --port 8000

dev-frontend:
	cd $(FRONTEND_DIR) && npm run dev

# ── Testing & Verification ────────────────────────────────────
test:
	cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v --tb=short

verify: verify-backend verify-frontend

verify-backend:
	cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/test_environment.py -v --tb=short -k "not TestDatabaseConnectivity and not TestAuthFlow"

verify-frontend:
	cd $(FRONTEND_DIR) && npm run verify

# ── Code Quality ──────────────────────────────────────────────
lint: lint-backend lint-frontend

lint-backend:
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff check .

lint-frontend:
	cd $(FRONTEND_DIR) && npm run lint

format:
	cd $(BACKEND_DIR) && $(PYTHON) -m ruff format .

typecheck:
	cd $(FRONTEND_DIR) && npm run typecheck

# ── Cleanup ───────────────────────────────────────────────────
clean:
	rd /s /q $(FRONTEND_DIR)\dist 2>NUL || true
	rd /s /q $(BACKEND_DIR)\__pycache__ 2>NUL || true
	rd /s /q $(BACKEND_DIR)\.pytest_cache 2>NUL || true
	rd /s /q $(BACKEND_DIR)\.ruff_cache 2>NUL || true
	del /q $(BACKEND_DIR)\*.pyc 2>NUL || true
	@echo "✅ Cleaned build artifacts"
