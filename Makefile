.PHONY: help install install-dev test lint format typecheck clean build publish-test publish docs

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in production mode
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev,all]"

test:  ## Run tests with coverage
	pytest --cov=pypaginator --cov-report=term-missing --cov-report=html

test-quick:  ## Run tests without coverage
	pytest -v

test-unit:  ## Run only unit tests
	pytest -m unit

test-integration:  ## Run only integration tests
	pytest -m integration

lint:  ## Run linting checks
	ruff check src/pypaginator

lint-fix:  ## Run linting and fix auto-fixable issues
	ruff check --fix src/pypaginator

format:  ## Format code with black
	black src/pypaginator tests examples

format-check:  ## Check code formatting
	black --check src/pypaginator tests examples

typecheck:  ## Run type checking
	mypy src/pypaginator

complexity:  ## Check code complexity
	radon cc -s -n B src/pypaginator

quality:  ## Run all quality checks
	@echo "Running type check..."
	@mypy src/pypaginator
	@echo "\nRunning linter..."
	@ruff check src/pypaginator
	@echo "\nChecking format..."
	@black --check src/pypaginator tests
	@echo "\nChecking complexity..."
	@radon cc -s -n B src/pypaginator
	@echo "\n✓ All quality checks passed!"

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package distribution
	python -m build

publish-test:  ## Publish to Test PyPI
	python -m build
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	python -m build
	twine upload dist/*

docs:  ## Generate documentation
	cd docs && make html

example-basic:  ## Run basic example
	python examples/basic_example.py

example-sqlalchemy:  ## Run SQLAlchemy example
	python examples/sqlalchemy_example.py

example-fastapi:  ## Run FastAPI example
	python examples/fastapi_example.py

