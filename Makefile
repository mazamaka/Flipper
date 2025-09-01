# Simple Makefile to manage the FastAPI service

PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

.PHONY: help env install up up-prod down clean

help:
	@echo "Available targets:"
	@echo "  make up       - start FastAPI with reload (dev)"
	@echo "  make up-prod  - start FastAPI in production mode"
	@echo "  make install  - create venv and install dependencies"
	@echo "  make down     - stop uvicorn (best-effort)"
	@echo "  make clean    - remove __pycache__"

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

up:
	$(UVICORN) app.main:app --reload

up-prod:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

# Best-effort stop (Linux)
# If you run multiple uvicorn processes, refine the pattern.
# Alternatively, manage with systemd, docker-compose, or a process manager.
down:
	- pkill -f "uvicorn app.main:app" || true

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
