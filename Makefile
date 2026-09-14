.PHONY: help venv install check lint format typecheck test test-cov audit smoke-test run-api simulate train evaluate

help:
	@echo "Available targets:"
	@echo "  install    - Install package in editable mode with dev dependencies"
	@echo "  lint       - Run ruff linter"
	@echo "  format     - Run ruff code formatter"
	@echo "  typecheck  - Run mypy type checker"
	@echo "  test       - Run pytest test suite"
	@echo "  test-cov   - Run pytest with coverage report"
	@echo "  audit      - Run pip-audit dependency vulnerability scanner"
	@echo "  smoke-test - Run post-deployment smoke test suite"
	@echo "  check      - Run all quality checks (lint, format check, typecheck, test, audit)"
	@echo "  run-api    - Run FastAPI development server locally"
	@echo "  simulate   - Run telemetry simulator"
	@echo "  train      - Run ML training pipeline"
	@echo "  evaluate   - Run ML evaluation script"

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy services

test:
	pytest

test-cov:
	pytest --cov=services --cov-report=term-missing

audit:
	pip-audit --desc

smoke-test:
	python scripts/smoke_test.py --base-url http://localhost:8000

check:
	ruff check . && ruff format --check . && mypy services scripts && pytest && pip-audit --desc

run-api:
	uvicorn services.api.app.main:app --reload

simulate:
	python -m services.simulator.telemetry

train:
	python -m services.ml.train

evaluate:
	python -m services.ml.evaluate
