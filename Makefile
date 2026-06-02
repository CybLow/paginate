# Makefile for pypaginate
# Uses UV for dependency management and tooling

.PHONY: help sync sync-all lock upgrade test test-cov test-quick test-unit test-integration build-release build-debug test-release bench-release lint lint-fix format format-check typecheck qa qas clean build publish-test publish docs docs-serve docs-clean pre-commit-install pre-commit

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# DEPENDENCY MANAGEMENT
# =============================================================================

sync:  ## Install/sync all dependencies
	uv sync

sync-all:  ## Install with all optional features and groups
	uv sync --all-extras --group docs

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
	@echo "Running format check..."
	uv run ruff format --check src tests
	@echo "Running lint..."
	uv run ruff check src tests
	@echo "Running tests..."
	uv run pytest -q

qas:  ## Run all quality checks including mypy
	@echo "Running format check..."
	uv run ruff format --check src tests
	@echo "Running lint..."
	uv run ruff check src tests
	@echo "Running type check..."
	uv run mypy src
	@echo "Running tests..."
	uv run pytest -q

# =============================================================================
# TESTING
# =============================================================================

test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=pypaginate --cov-report=term-missing --cov-report=html --cov-report=xml

test-quick:  ## Run tests without coverage (fast)
	uv run pytest -x -q

test-unit:  ## Run only unit tests
	uv run pytest -m unit

test-integration:  ## Run only integration tests
	uv run pytest -m integration

# =============================================================================
# NATIVE EXTENSION (Rust _core via maturin)
# =============================================================================
# pypaginate._core is a Rust extension. A debug build (plain `maturin develop`)
# is ~10x slower at runtime, so ALWAYS use release for perf/benchmark work and
# any speed-sensitive run. CI already builds release wheels; this is local-dev.

build-release:  ## Build native _core (release; ~10x faster — use for perf/benchmarks)
	uv run maturin develop --release

build-debug:  ## Build native _core (debug; fast compile, slow runtime)
	uv run maturin develop

test-release: build-release  ## Release-build the native ext, then run the full suite
	uv run pytest

bench-release: build-release  ## Release-build the native ext, then run perf benchmarks
	uv run pytest tests/perf --run-benchmark

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
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# =============================================================================
# DOCUMENTATION
# =============================================================================

docs:  ## Build documentation
	uv run sphinx-build -b html docs site

docs-serve:  ## Serve documentation locally
	uv run sphinx-autobuild docs site

docs-clean:  ## Clean documentation build
	rm -rf site/

# =============================================================================
# DEVELOPMENT UTILITIES
# =============================================================================

pre-commit-install:  ## Install pre-commit hooks
	uv run pre-commit install

pre-commit:  ## Run pre-commit on all files
	uv run pre-commit run --all-files

# =============================================================================
# QUICK COMMANDS
# =============================================================================

.PHONY: dev
dev: sync-all pre-commit-install  ## Set up development environment
	@echo "Development environment ready!"

.PHONY: check
check: format-check lint typecheck  ## Run all checks without tests
	@echo "All checks passed!"

.PHONY: fix
fix: lint-fix format  ## Auto-fix code style issues
	@echo "Code fixed!"
