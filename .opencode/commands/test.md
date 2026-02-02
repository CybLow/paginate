# Test Workflow

Run test suite for pypaginate with various options.

## Basic Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/pypaginate --cov-report=html

# Stop on first failure
uv run pytest -x

# Run last failed tests first
uv run pytest --lf

# Run in parallel (faster)
uv run pytest -n auto

# Run specific test file
uv run pytest tests/test_paginator.py

# Run specific test function
uv run pytest tests/test_paginator.py::test_basic_pagination

# Run tests matching pattern
uv run pytest -k "pagination and not slow"
```

## Test Categories (Markers)

All markers are configured in `pyproject.toml`.

### By Test Type

```bash
# Unit tests (fast, no external deps)
uv run pytest -m unit

# Integration tests (database, real deps)
uv run pytest -m integration

# End-to-end tests
uv run pytest -m e2e

# Property-based tests (Hypothesis)
uv run pytest -m property

# Benchmark tests
uv run pytest -m benchmark

# Snapshot tests
uv run pytest -m snapshot
```

### By Feature

```bash
# SQLAlchemy tests
uv run pytest -m sqlalchemy

# FastAPI tests
uv run pytest -m fastapi

# Search feature tests
uv run pytest -m search

# Filter feature tests
uv run pytest -m filters

# Sorting tests
uv run pytest -m sorting

# Keyset pagination tests
uv run pytest -m keyset
```

### By Execution Hints

```bash
# Exclude slow tests
uv run pytest -m "not slow"

# Skip flaky tests
uv run pytest -m "not flaky"

# Run only CI-safe tests
uv run pytest -m "not skip_ci"

# Combine markers
uv run pytest -m "unit and not slow"
```

## Coverage

```bash
# Run with coverage report
uv run pytest --cov=src/pypaginate --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=src/pypaginate --cov-report=html

# Fail if coverage below threshold (85%)
uv run pytest --cov=src/pypaginate --cov-fail-under=85
```

### Coverage Requirements

- Minimum: 85% (CI gate, configured in pyproject.toml)
- Target: 90%+
- Critical paths: 100%

## Advanced Options

```bash
# Rerun failed tests with retries
uv run pytest --reruns 3 --reruns-delay 1

# Set timeout per test
uv run pytest --timeout=10

# Random test order (finds order-dependent bugs)
uv run pytest -p randomly

# Show 10 slowest tests
uv run pytest --durations=10
```

## Test Naming Convention

Format: `test_<unit>_<scenario>_<expected_result>`

Examples:
- `test_paginator_with_empty_list_returns_empty_page`
- `test_paginator_with_negative_page_raises_value_error`
- `test_filter_with_invalid_operator_raises_validation_error`
