# Testing Guide

> How to write, run, and benchmark tests for pypaginate.

---

## Running Tests

### All Tests (excluding benchmarks)

```bash
uv run pytest tests/ --ignore=tests/perf -q
```

### By Category

```bash
# Unit (fastest, ~700 tests)
uv run pytest tests/unit/ -q

# Integration (cross-module + DB)
uv run pytest tests/integration/ -q

# E2E (full workflows)
uv run pytest tests/e2e/ -q

# Property-based (Hypothesis)
uv run pytest tests/property/ -q

# Architecture enforcement
uv run pytest tests/architecture/ -q
```

### Specific Module

```bash
# All filtering tests
uv run pytest tests/unit/filtering/ -v

# Single test class
uv run pytest tests/unit/filtering/test_engine.py::TestFilterEngineSingle -v

# Single test method
uv run pytest tests/unit/filtering/test_engine.py::TestFilterEngineSingle::test_eq_filter_returns_matching_item -v
```

### With Coverage

```bash
uv run pytest tests/unit/ --cov=pypaginate --cov-config=pyproject.toml --cov-report=term-missing
```

---

## Writing Tests

### File Naming

Each source file maps to a test file:

```
src/pypaginate/filtering/engine.py  →  tests/unit/filtering/test_engine.py
src/pypaginate/search/matching.py   →  tests/unit/search/test_matching.py
src/pypaginate/domain/pages.py      →  tests/unit/domain/test_pages.py
```

### Test Structure

Use classes for grouping, AAA (Arrange-Act-Assert) pattern:

```python
"""Tests for FilterEngine."""

from __future__ import annotations

from pypaginate.domain.specs import FilterSpec
from pypaginate.filtering.engine import FilterEngine


class TestFilterEngineSingle:
    def test_eq_filter_returns_matching_item(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [FilterSpec(field="name", operator="eq", value="Alice")]

        result = filter_engine.apply(sample_users, filters)

        assert len(result) == 1
        assert result[0]["name"] == "Alice"
```

### Fixtures

Use fixtures from `conftest.py` — don't create objects inline when a fixture exists:

```python
# GOOD — uses shared fixture
def test_filter(self, filter_engine: FilterEngine) -> None: ...

# BAD — creates inline (duplicated setup)
def test_filter(self) -> None:
    engine = FilterEngine(create_default_registry())
```

Available fixtures (from `tests/conftest.py`):
- `filter_engine` — FilterEngine with default registry
- `sort_engine` — SortEngine
- `search_engine` — SearchEngine
- `filter_registry` — OperatorRegistry
- `sample_users` — 4 users (unit) or 8 users (root)

### Parametrize for Coverage

```python
@pytest.mark.parametrize(
    ("direction", "nulls", "expected_first"),
    [
        (SortDirection.ASC, NullsPosition.FIRST, None),
        (SortDirection.ASC, NullsPosition.LAST, 1),
    ],
    ids=["asc-nulls-first", "asc-nulls-last"],
)
def test_null_position(self, direction, nulls, expected_first) -> None: ...
```

---

## Benchmarking

### Quick Start

```bash
# Run comparison benchmarks
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-only -q

# Save baseline before optimizing
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-save=before-change

# Run after change and compare
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-compare=0001
```

### Writing Benchmarks

```python
@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_10k(benchmark: Any, memory_env_10k: BackendEnv) -> None:
    """Benchmark single filter on 10K items."""
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(memory_env_10k.do_filter, memory_env_10k.query, specs)
    assert len(result) <= 10_000
```

Key rules:
1. Always use `@pytest.mark.benchmark(group="...")` for grouping
2. Assert correctness inside the benchmark — don't just measure speed
3. Use `benchmark()` callable — it handles warmup, calibration, rounds
4. Use `memory_env_10k` / `memory_env_100k` fixtures for consistent data

### Benchmark Suites

| Suite | Purpose | Run Command |
|---|---|---|
| Comparison | pypaginate vs raw at 10K | `uv run pytest tests/perf/test_comparison.py --benchmark-enable -q` |
| Scaling | 1K→1M across backends | `uv run pytest tests/perf/test_scaling.py --benchmark-enable -q` |
| Competitors | vs paginate-lib, fp, sqlakeyset | `uv run pytest tests/perf/test_competitors.py --benchmark-enable -q` |
| FastAPI HTTP | HTTP endpoint scaling | `uv run pytest tests/perf/test_fastapi_scaling.py --benchmark-enable -q` |
| Overhead | ops → paginate → serialize → HTTP | `uv run pytest tests/perf/test_overhead.py --benchmark-enable -q` |
| ALL perf | Everything | `uv run pytest tests/perf/ --benchmark-enable -q` |

### Reading Results

Focus on **Median** (not Mean — Mean is skewed by outliers):

```
Name                         Min       Max       Mean      Median    OPS
test_memory_filter_10k     2.5ms     6.7ms     3.8ms     3.5ms     263/s   ← use Median
test_raw_list_filter_10k   159us     530us     257us     231us     3882/s
```

The ratio `3.5ms / 231us = 15.1x` is the overhead vs raw Python.
