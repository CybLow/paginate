# pypaginate Testing Architecture

> **714 tests** across 5 categories + ~150 benchmark functions

---

## Test Pyramid

```
              ╱╲
             ╱  ╲           E2E (6 tests — full workflows with FastAPI)
            ╱    ╲
           ╱──────╲         Integration (8 tests — cross-module + DB)
          ╱        ╲
         ╱──────────╲       Property (3 tests — Hypothesis invariants)
        ╱            ╲
       ╱──────────────╲     Architecture (3 tests — file limits, imports, protocols)
      ╱                ╲
     ╱──────────────────╲   Benchmarks (~150 functions — perf regression, competitors)
    ╱                    ╲
   ╱──────────────────────╲ Unit (694 tests — 100% module coverage)
```

---

## Directory Structure

```
tests/
├── conftest.py                    # Root: markers, engine/backend fixtures, data generators
├── factories/
│   ├── data.py                    # make_users(n), make_products(), make_records()
│   └── domain.py                  # make_offset_params(), make_filter_spec(), etc.
├── fixtures/
│   ├── backends.py                # BackendEnv dataclass, setup_sa_sync/async helpers
│   ├── models.py                  # SQLAlchemy ORM models (User, Product)
│   ├── database.py                # Async engine/session fixtures
│   └── helpers.py                 # Test utilities
│
├── unit/                          # 694 tests — isolated per-module coverage
│   ├── conftest.py                # sample_users (Alice, Bob, Charlie, Diana), search_items
│   ├── domain/                    # params, pages, specs, enums, exceptions, protocols
│   ├── engine/                    # paginator, cursor, pipeline, dispatch
│   ├── filtering/                 # operators, engine, registry, accessor
│   ├── sorting/                   # engine, keys
│   ├── search/                    # engine, parser, matching
│   ├── text/                      # normalize (LRU cache, ASCII fast path)
│   └── adapters/
│       ├── memory/                # backend, filters, sorting, search
│       ├── sqlalchemy/            # backend, filters, sorting, search, cursor, columns
│       └── fastapi/               # dependencies (OffsetDep, CursorDep)
│
├── integration/                   # 8 tests — cross-module composition
│   ├── conftest.py                # SQLite async engine fixture
│   ├── test_smoke.py              # Basic sanity: paginate([1,2,3], params)
│   ├── test_pagination.py         # Full offset + cursor flows
│   ├── test_filtering.py          # FilterEngine + MemoryBackend composition
│   ├── test_sorting.py            # SortEngine + MemoryBackend
│   ├── test_search.py             # SearchEngine + MemoryBackend
│   ├── test_pipeline.py           # Full pipeline (filter → sort → search → paginate)
│   ├── test_custom_backend.py     # User-defined backend protocol compliance
│   └── test_fastapi.py            # Full FastAPI app with TestClient
│
├── e2e/                           # 6 tests — real-world workflows
│   ├── conftest.py                # 100-item dataset
│   ├── test_offset_flows.py       # Offset pagination edge cases
│   ├── test_filter_flows.py       # Filter → paginate chains
│   ├── test_sort_flows.py         # Sort → paginate chains
│   ├── test_combined_flows.py     # Filter + sort + search + paginate
│   ├── test_completeness.py       # No data loss across pages
│   └── test_fastapi_flows.py      # Full HTTP endpoint scenarios
│
├── property/                      # 3 tests — Hypothesis-based invariants
│   ├── conftest.py                # Hypothesis settings (deadline=500ms)
│   ├── strategies.py              # Custom strategies for specs, params, data
│   ├── test_pagination.py         # Invariant: total == sum(page.items for all pages)
│   ├── test_filtering.py          # Invariant: filtered <= original
│   └── test_sorting.py            # Invariant: sorted output is actually sorted
│
├── architecture/                  # 3 tests — code quality enforcement
│   ├── test_file_limits.py        # All source files ≤ 200 lines (code only)
│   ├── test_imports.py            # No circular imports
│   └── test_protocols.py          # All backends implement protocol interfaces
│
└── perf/                          # ~150 benchmark functions (excluded from normal runs)
    ├── conftest.py                # Dataset fixtures (1K→1M), backend setup helpers
    ├── test_comparison.py         # Side-by-side: memory vs SA vs raw at 10K
    ├── test_competitors.py        # vs paginate-lib, fastapi-pagination, sqlakeyset
    ├── test_scaling.py            # pypaginate scaling: 1K→100K for all ops × all backends
    ├── test_competitor_scaling.py  # Competitor scaling: raw, paginate-lib, fp at 1K→1M
    ├── test_competitor_scaling_sa.py # SA competitors: raw SA, sqlakeyset, fp-sa at 1K→100K
    ├── test_fastapi_scaling.py    # HTTP scaling: pypaginate vs raw vs fp at 1K→100K
    ├── test_fastapi_perf.py       # FastAPI endpoint benchmarks (error handling, valid/invalid)
    ├── test_filtering.py          # Filter stress + benchmark (single/multi/100K)
    ├── test_sorting.py            # Sort stress + benchmark
    ├── test_search.py             # Search stress + benchmark
    ├── test_pagination.py         # Paginate benchmark (memory/SA sync/SA async)
    ├── test_pipeline.py           # Pipeline benchmark (memory/SA)
    ├── test_overhead.py           # Ops only → +paginate → +serialize → full HTTP
    ├── test_serialization.py      # OffsetPage.create() overhead at 20/100/1000 items
    ├── test_error_handling.py     # Error path benchmarks
    └── test_boundary.py           # Edge cases (empty, single item, max page)
```

---

## Running Tests

### Quick Commands

```bash
# All tests (excluding benchmarks)
uv run pytest tests/ --ignore=tests/perf -q

# Unit tests only (fastest)
uv run pytest tests/unit/ -q

# With coverage
uv run pytest tests/unit/ --cov=pypaginate --cov-config=pyproject.toml

# Specific module
uv run pytest tests/unit/filtering/ -v

# Single test
uv run pytest tests/unit/filtering/test_engine.py::TestFilterEngineSingle -v
```

### Markers

```bash
# Run slow tests (500K/1M datasets)
uv run pytest --run-slow

# Run by marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m e2e
uv run pytest -m property
```

### Parallel Execution

```bash
# Use all cores
uv run pytest tests/unit/ -n auto

# Use specific count
uv run pytest tests/unit/ -n 4
```

---

## Writing Tests

### Naming Convention

```
tests/unit/{module}/test_{source_file}.py

# Example:
src/pypaginate/filtering/engine.py  →  tests/unit/filtering/test_engine.py
src/pypaginate/search/matching.py   →  tests/unit/search/test_matching.py
```

### Test Structure (AAA Pattern)

```python
class TestFilterEngineSingle:
    def test_eq_filter_returns_matching_item(
        self,
        filter_engine: FilterEngine,         # Arrange (fixture)
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [FilterSpec(field="name", operator="eq", value="Alice")]

        result = filter_engine.apply(sample_users, filters)  # Act

        assert len(result) == 1                                # Assert
        assert result[0]["name"] == "Alice"
```

### Fixtures

Shared fixtures are in `conftest.py` files at each level:

```python
# tests/conftest.py — available everywhere
@pytest.fixture()
def filter_engine() -> FilterEngine:
    return FilterEngine(create_default_registry())

@pytest.fixture()
def sample_users() -> list[dict[str, object]]:
    return make_users(8)

# tests/unit/conftest.py — overrides for unit tests
@pytest.fixture()
def sample_users() -> list[dict[str, object]]:
    return [
        {"name": "Alice", "age": 30, "email": "alice@test.com", "active": True},
        {"name": "Bob", "age": 25, "email": "bob@test.com", "active": True},
        {"name": "Charlie", "age": 35, "email": "charlie@test.com", "active": False},
        {"name": "Diana", "age": 28, "email": "diana@test.com", "active": True},
    ]
```

---

## Benchmarking

### Running Benchmarks

```bash
# Quick comparison (10K, all operations)
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-only -q

# Full scaling suite (1K→1M)
uv run pytest tests/perf/test_scaling.py --benchmark-enable --benchmark-only -q

# Competitor comparison
uv run pytest tests/perf/test_competitors.py --benchmark-enable --benchmark-only -q

# Save results for later comparison
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-save=my-run

# Compare against saved baseline
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-compare=0001
```

### Benchmark Categories

| Suite | What It Measures | Sizes |
|---|---|---|
| `test_comparison.py` | pypaginate vs raw Python at 10K | 10K |
| `test_competitors.py` | vs paginate-lib, fastapi-pagination, sqlakeyset | 10K, 100K |
| `test_scaling.py` | pypaginate scaling across backends | 1K → 1M |
| `test_competitor_scaling.py` | Competitor scaling (memory) | 1K → 1M |
| `test_competitor_scaling_sa.py` | Competitor scaling (SA sync/async) | 1K → 100K |
| `test_fastapi_scaling.py` | HTTP endpoint scaling | 1K → 100K |
| `test_overhead.py` | ops → +paginate → +serialize → HTTP | 10K |
| `test_serialization.py` | OffsetPage.create() overhead | 20, 100, 1000 items |

### Best Practices for Benchmarking

1. **Close other applications** — CPU frequency scaling affects results
2. **Run multiple times** — pytest-benchmark auto-calibrates rounds
3. **Use `--benchmark-save`** — always save baselines before optimizing
4. **Compare on same machine** — cross-machine comparisons are unreliable
5. **Use `--benchmark-disable`** by default — benchmarks slow down normal test runs
6. **Group by operation** — use `@pytest.mark.benchmark(group="filter-memory")` for clean output
7. **Test at multiple scales** — 1K/10K/100K reveal different bottlenecks (O(n) vs O(n log n))

### Reading Benchmark Output

```
Name                    Min        Max        Mean       StdDev     Median     OPS
test_memory_filter_10k  2.5 ms     6.7 ms     3.8 ms     0.9 ms     3.5 ms    263/s
test_raw_list_filter    159 us     530 us     257 us      64 us      231 us    3882/s
```

- **Median** is the most reliable metric (not affected by outliers)
- **OPS** (operations per second) is useful for throughput comparison
- **Min** shows best-case (warm cache, no GC)
- **StdDev** > 30% of Mean indicates noisy results — re-run

---

## Architecture Tests

The `tests/architecture/` directory enforces code quality at CI level:

### File Limits (`test_file_limits.py`)

Every source file in `src/pypaginate/` (excluding `_cli/`) must be ≤ 200 lines of code (comments, docstrings, blanks excluded). This prevents files from growing unbounded.

### Import Cycles (`test_imports.py`)

Detects circular imports by attempting to import every module. Fails fast if any cycle exists.

### Protocol Compliance (`test_protocols.py`)

Verifies that all backend adapters (Memory, SQLAlchemy) implement the required protocol interfaces (`PaginationBackend`, `FilterBackend`, `SortBackend`, `SearchBackend`).

---

## Coverage

```bash
# Run with coverage
uv run pytest tests/unit/ --cov=pypaginate --cov-config=pyproject.toml

# HTML report
uv run pytest tests/unit/ --cov=pypaginate --cov-report=html

# Fail if coverage drops below threshold
uv run pytest tests/unit/ --cov=pypaginate --cov-fail-under=85
```

Coverage configuration in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src/pypaginate"]
branch = true

[tool.coverage.report]
fail_under = 85
```
