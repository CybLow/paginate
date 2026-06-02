# Testing Guide

How to write, run, and benchmark tests for pypaginate.

---

## Running Tests

### All Tests (excluding benchmarks)

```bash
uv run pytest tests/ --ignore=tests/perf -q
```

### By Category

```bash
# Unit tests (fastest, bulk of the suite)
uv run pytest tests/unit/ -q

# Integration (cross-module + database)
uv run pytest tests/integration/ -q

# End-to-end (full workflows with FastAPI)
uv run pytest tests/e2e/ -q

# Property-based (Hypothesis invariants)
uv run pytest tests/property/ -q

# Architecture enforcement (file limits, imports, protocol compliance)
uv run pytest tests/architecture/ -q
```

### Specific Module

```bash
# All filtering tests
uv run pytest tests/unit/filtering/ -v

# Single test class
uv run pytest tests/unit/filtering/test_engine.py::TestFilterEngineSingle -v

# Single test method
uv run pytest tests/unit/filtering/test_engine.py::TestFilterEngineSingle::test_eq_filter -v
```

### With Coverage

```bash
uv run pytest tests/unit/ --cov=pypaginate --cov-config=pyproject.toml --cov-report=term-missing
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

Per-module tests that exercise individual classes and functions in isolation.
Each source file maps to a test file:

```
src/pypaginate/filtering/engine.py  -->  tests/unit/filtering/test_engine.py
src/pypaginate/search/matching.py   -->  tests/unit/search/test_matching.py
src/pypaginate/domain/pages.py      -->  tests/unit/domain/test_pages.py
```

### Integration Tests (`tests/integration/`)

Cross-module tests that verify multiple components work together.
May use real SQLAlchemy sessions with in-memory SQLite.

### End-to-End Tests (`tests/e2e/`)

Full workflow tests using FastAPI's `TestClient`. These exercise the
complete request path from HTTP query params through pagination and back
to JSON response.

### Property-Based Tests (`tests/property/`)

Hypothesis-driven tests that verify invariants hold across randomized inputs.
These catch edge cases that unit tests miss.

### Architecture Tests (`tests/architecture/`)

Automated enforcement of structural rules:

- **File limits** -- no source file exceeds 250 code lines (excluding comments, docstrings, blanks)
- **Import rules** -- no circular imports, layer violations detected
- **Protocol compliance** -- all backends satisfy their declared protocols

---

## Writing Tests

### Structure

Use classes for grouping, AAA (Arrange-Act-Assert) pattern:

```python
"""Tests for SQLAlchemyFilterBackend."""

from __future__ import annotations

from pypaginate.domain.specs import FilterSpec
from pypaginate.adapters.sqlalchemy import SQLAlchemyFilterBackend


class TestFilterBackendEquality:
    def test_eq_filter_applies_where_clause(self) -> None:
        # Arrange
        backend = SQLAlchemyFilterBackend()
        specs = [FilterSpec(field="name", operator="eq", value="Alice")]

        # Act
        result = backend.apply_filters(query, specs)

        # Assert
        assert "WHERE" in str(result)
```

### Fixtures

Use shared fixtures from `conftest.py` -- don't create objects inline when a
fixture exists:

```python
# GOOD -- uses shared fixture
def test_filter(self, filter_engine: FilterEngine) -> None: ...

# BAD -- duplicated setup
def test_filter(self) -> None:
    engine = FilterEngine()
```

### Parametrize for Coverage

```python
@pytest.mark.parametrize(
    ("operator", "value", "expected_count"),
    [
        ("eq", "Alice", 1),
        ("ne", "Alice", 3),
        ("contains", "li", 1),
        ("gte", 30, 2),
    ],
    ids=["eq", "ne", "contains", "gte"],
)
def test_filter_operator(self, operator, value, expected_count) -> None:
    specs = [FilterSpec(field="name", operator=operator, value=value)]
    result = filter_engine.apply(sample_users, specs)
    assert len(result) == expected_count
```

### Test Naming

Test names should describe the behavior being tested:

```python
# GOOD -- describes behavior
def test_between_requires_two_element_sequence(self) -> None: ...
def test_cursor_after_and_before_are_mutually_exclusive(self) -> None: ...

# BAD -- vague
def test_filter(self) -> None: ...
def test_error(self) -> None: ...
```

---

## Coverage Expectations

- **Unit tests** -- cover happy path and error cases for every public method
- **New features** -- must include tests before merging
- **Bug fixes** -- must include a regression test that fails without the fix

---

## Benchmarking

### Running Benchmarks

```bash
# Quick comparison benchmarks
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-only -q

# Save baseline before optimizing
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-save=before

# Compare after a change
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-compare=0001
```

### Benchmark Suites

| Suite | Purpose |
|---|---|
| `test_comparison.py` | pypaginate vs raw Python at 10K |
| `test_scaling.py` | 1K to 1M across backends |
| `test_competitors.py` | vs other pagination libraries |
| `test_fastapi_scaling.py` | HTTP endpoint scaling |
| `test_overhead.py` | ops to paginate to serialize to HTTP |

### Writing Benchmarks

```python
@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_10k(benchmark, memory_env_10k) -> None:
    """Benchmark single filter on 10K items."""
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(memory_env_10k.do_filter, memory_env_10k.query, specs)
    assert len(result) <= 10_000
```

Rules:

1. Always use `@pytest.mark.benchmark(group="...")` for grouping
2. Assert correctness inside the benchmark
3. Use `benchmark()` callable -- it handles warmup, calibration, and rounds
4. Focus on **Median** when reading results (Mean is skewed by outliers)
