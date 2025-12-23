# Makefile for pypaginator
# Uses UV for dependency management and tooling

.PHONY: help sync lock upgrade test test-quick test-unit test-integration lint lint-fix format typecheck qa qas clean build publish-test publish docs

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# DEPENDENCY MANAGEMENT
# =============================================================================

sync:  ## Install/sync all dependencies
	uv sync

sync-all:  ## Install with all optional features
	uv sync --all-extras

lock:  ## Update the lock file
	uv lock

upgrade:  ## Upgrade all dependencies
	uv lock --upgrade
	uv sync

# =============================================================================
# CODE QUALITY
# =============================================================================

lint:  ## Run linting checks
	uv run ruff check src tests

lint-fix:  ## Run linting and auto-fix issues
	uv run ruff check --fix src tests

format:  ## Format code with ruff
	uv run ruff format src tests

format-check:  ## Check code formatting
	uv run ruff format --check src tests

typecheck:  ## Run type checking with mypy
	uv run mypy src

qa:  ## Run essential quality checks (format, lint, test)
	uv run pypaginator qa

qas:  ## Run all quality checks including mypy
	uv run pypaginator qas

# =============================================================================
# TESTING
# =============================================================================

test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=pypaginator --cov-report=term-missing --cov-report=html --cov-report=xml

test-quick:  ## Run tests without coverage (fast)
	uv run pytest -x -q

test-unit:  ## Run only unit tests
	uv run pytest -m unit

test-integration:  ## Run only integration tests
	uv run pytest -m integration

# =============================================================================
# BUILD & PUBLISH
# =============================================================================

build:  ## Build package distribution
	uv build

publish-test:  ## Publish to Test PyPI
	uv build
	uv publish --index testpypi

publish:  ## Publish to PyPI
	uv build
	uv publish

clean:  ## Clean build artifacts and caches
	uv run pypaginator clean

# =============================================================================
# DOCUMENTATION
# =============================================================================

docs:  ## Build documentation
	uv run --group docs mkdocs build

docs-serve:  ## Serve documentation locally
	uv run --group docs mkdocs serve

# =============================================================================
# DEVELOPMENT UTILITIES
# =============================================================================

pre-commit-install:  ## Install pre-commit hooks
	uv run pre-commit install

pre-commit:  ## Run pre-commit on all files
	uv run pre-commit run --all-files
