# pypaginate Testing Architecture

> Comprehensive test strategy for maintaining, benchmarking, and validating pypaginate across all adapters.

---

## Test Pyramid

```
              ╱╲
             ╱  ╲         E2E (cross-backend workflows)
            ╱    ╲
           ╱──────╲       Integration (adapter composition, cross-backend equivalence)
          ╱        ╲
         ╱──────────╲     Property (Hypothesis invariants)
        ╱            ╲
       ╱──────────────╲   Stress (large datasets, boundary values)
      ╱                ╲
     ╱──────────────────╲  Benchmarks (perf regression, adapter comparison)
    ╱                    ╲
   ╱──────────────────────╲ Architecture (imports, protocols, file limits)
  ╱                        ╲
 ╱────────────────────────────╲  Unit (100% coverage, typed fakes, all backends)
```

---

## Directory Structure

```
tests/
├── conftest.py                         # Root: markers, shared data, engine/backend fixtures
├── factories/
│   ├── data.py                         # make_users(), make_products(), make_records()
│   └── domain.py                       # make_offset_params(), make_filter_spec(), etc.
├── fixtures/
│   ├── models.py                       # SQLAlchemy ORM models (User, Product, Order)
│   ├── database.py                     # Async engine/session fixtures
│   └── data.py                         # Seed data constants (TEST_USERS_DATA, etc.)
│
├── unit/                               # 473 tests, 100% coverage
│   ├── conftest.py                     # Unit-specific: sample_users (4 named users)
│   ├── domain/                         # params, pages, specs, enums, exceptions, protocols
│   ├── engine/                         # paginator, cursor, pipeline, dispatch
│   ├── filtering/                      # operators, engine, registry, accessor
│   ├── sorting/                        # engine, keys
│   ├── search/                         # engine, parser, matching
│   ├── text/                           # normalize
│   └── adapters/
│       ├── memory/                     # backend, filters, sorting, search
│       ├── sqlalchemy/                 # backend, cursor, filters, sorting, search (real DB)
│       └── fastapi/                    # dependencies (real TestClient)
│
├── integration/                        # Cross-module, cross-backend
│   ├── conftest.py                     # Parametrized cross-backend fixtures
│   ├── memory/                         # Memory pipeline, backend protocol checks
│   ├── sqlalchemy/                     # Real DB: pagination, filters, sorting, search, pipeline
│   ├── test_cross_backend.py           # Parametrized: same test on BOTH backends
│   ├── test_adapter_composition.py     # Filter → sort → search → paginate chains
│   └── test_custom_backend.py          # User-defined backends work with pypaginate
│
├── e2e/                                # Full user workflows
│   ├── conftest.py                     # Large dataset fixtures
│   ├── test_offset_flows.py            # All-pages iteration, completeness
│   ├── test_filter_flows.py            # Filter + paginate workflows
│   ├── test_sort_flows.py              # Sort + paginate across pages
│   ├── test_search_flows.py            # Search + paginate with relevance
│   ├── test_combined_flows.py          # Filter + sort + search + paginate
│   ├── test_full_pipeline_flows.py     # Full pipeline with parametrized dataset sizes
│   ├── test_cross_backend_flows.py     # Same flows on BOTH memory + SQLAlchemy
│   └── test_sqlalchemy_flows.py        # SQLAlchemy-specific deep flows
│
├── property/                           # Hypothesis invariants
│   ├── strategies.py                   # Reusable: offset_params(), datasets(), etc.
│   ├── test_pagination_props.py        # total == sum(page.items), navigation consistency
│   ├── test_filter_props.py            # Filter never adds, idempotent, subset guarantee
│   └── test_sort_props.py             # Preserves count, ordering, idempotent
│
├── stress/                             # Large-scale, boundary conditions
│   ├── test_large_datasets.py          # 50K-100K items: paginate, filter, sort, pipeline
│   ├── test_boundary_values.py         # limit=1, limit=MAX, exact fit, empty, clamp MAX_INT
│   └── test_pipeline_stress.py         # 10K filtered+sorted, 100x repeated, limit=1 on 10K
│
├── benchmarks/                         # Performance regression + adapter comparison
│   ├── conftest.py                     # Datasets: 100/1K/10K items, session-scoped SA engine
│   ├── test_pagination_perf.py         # Paginate 100/1K/10K items + clamp
│   ├── test_filter_perf.py             # Single/multiple filters on 1K items
│   ├── test_sort_perf.py               # Single/multi-field sort on 1K items
│   ├── test_search_perf.py             # Single/multi-field search on 1K items
│   ├── test_pipeline_perf.py           # Full pipeline on 1K/10K items
│   ├── test_adapter_perf.py            # Memory adapter operations benchmarked
│   ├── test_sqlalchemy_perf.py         # SQLAlchemy adapter operations benchmarked
│   ├── test_e2e_perf.py                # End-to-end paginate() call benchmarked
│   └── test_adapter_comparison.py      # SAME operation on BOTH adapters, side-by-side
│
└── architecture/                       # Structural verification
    ├── test_imports.py                 # Layer boundary enforcement (domain → engine → adapters)
    ├── test_protocols.py               # All backends satisfy their protocols
    └── test_file_limits.py             # No source file > 200 LOC (code only)
```

---

## Fixture Hierarchy

### Root conftest.py (shared by ALL test categories)

```python
# Markers
pytest_configure → register unit, integration, e2e, property, stress, benchmark
pytest_collection_modifyitems → auto-apply markers by directory

# Engines (singleton-like, reused everywhere)
filter_registry → create_default_registry()
filter_engine   → FilterEngine(filter_registry)
sort_engine     → SortEngine()
search_engine   → SearchEngine()

# Data
sample_users    → make_users(8) from factories/data.py
large_dataset   → make_users(1000) for stress/e2e
```

### Unit conftest.py (overrides for unit-specific data)

```python
sample_users → 4 named users (Alice, Bob, Charlie, Diana) with known ages
search_items → 4 items with full names for search relevance testing
```

### SA conftest.py (real database fixtures)

```python
async_engine   → SQLite in-memory via aiosqlite
session        → Empty session (no data)
seeded_session → 10 users + 8 products from TEST_DATA constants
```

### Cross-backend conftest.py (parametrized)

```python
@pytest.fixture(params=["memory", "sqlalchemy"])
pagination_env → (mode, backend, query, total) for each backend
full_env       → all backends (pagination + filter + sort + search)
```

---

## Adapter Testing Strategy

### Every adapter tested at EVERY level:

| Level | Memory | SQLAlchemy | FastAPI |
|-------|:------:|:----------:|:-------:|
| **Unit** | Direct calls, typed fakes | Mock + real async SQLite DB | Real TestClient |
| **Integration** | Pipeline composition | Pipeline + real DB queries | — |
| **E2E** | Full workflows | Full workflows (parametrized) | — |
| **Cross-backend** | Same test, parametrized | Same test, parametrized | — |
| **Stress** | 100K items | 1K items (DB overhead) | — |
| **Benchmark** | Measured | Measured + compared | — |

### Cross-backend equivalence tests

The key principle: **same logical operation on both backends must produce same logical results**.

```python
@pytest.fixture(params=["memory", "sqlalchemy"])
async def pagination_env(request, ...):
    # Both backends seeded with IDENTICAL data
    if request.param == "memory":
        yield MemoryBackend(), sample_users, 8
    else:
        yield SQLAlchemyBackend(seeded_session), select(User), 8

# ONE test, TWO backends:
async def test_count_matches(pagination_env):
    mode, backend, query, expected = pagination_env
    total = await backend.count(query) if mode == "async" else backend.count(query)
    assert total == expected
```

---

## Benchmark Strategy

### Groups

| Group | What it measures | Datasets |
|-------|-----------------|----------|
| `pagination` | paginate() end-to-end | 100, 1K, 10K items |
| `filtering` | FilterEngine.apply / SA apply_filters | 1K items, 1-5 specs |
| `sorting` | SortEngine.apply / SA apply_sorting | 1K items, 1-3 fields |
| `search` | SearchEngine.apply / SA apply_search | 1K items |
| `pipeline` | Full filter+sort+paginate | 1K, 10K items |
| `adapter-comparison` | Same operation on memory vs SA | 1K items |

### Regression detection

```bash
# Save baseline
uv run pytest tests/benchmarks/ --benchmark-enable --benchmark-autosave

# Compare with previous run
uv run pytest tests/benchmarks/ --benchmark-enable --benchmark-compare

# Fail if regression > 25%
uv run pytest tests/benchmarks/ --benchmark-enable --benchmark-compare --benchmark-max-time=2.0
```

### Adapter comparison benchmarks

```python
@pytest.mark.benchmark(group="adapter-comparison-paginate")
@pytest.mark.parametrize("adapter", ["memory", "sqlalchemy"])
def test_paginate_1k(benchmark, adapter, ...):
    if adapter == "memory":
        result = benchmark(paginate, data, OffsetParams(page=1, limit=20))
    else:
        result = benchmark.pedantic(async_paginate, args=(...), rounds=10)
    assert result.total == 1000
```

This produces side-by-side output:
```
Name                                    Min       Max      Mean    Rounds
test_paginate_1k[memory]              0.0002    0.0004   0.0003      100
test_paginate_1k[sqlalchemy]          0.0015    0.0025   0.0018       10
```

---

## Test Data Strategy

### Canonical datasets (reproducible, deterministic)

| Dataset | Size | Source | Used by |
|---------|------|--------|---------|
| `SAMPLE_USERS` | 8 | `factories/data.py:make_users(8)` | unit, integration |
| `TEST_USERS_DATA` | 10 | `fixtures/data.py` | SA unit tests |
| `large_dataset` | 1K | `factories/data.py:make_users(1000)` | e2e, stress |
| `benchmark datasets` | 100/1K/10K | `benchmarks/conftest.py` | benchmarks |

### Data consistency rule

Memory and SQLAlchemy tests use **logically identical data**:
- Memory: `[{"id": 1, "name": "Alice", "email": "alice@test.com"}, ...]`
- SQLAlchemy: `User(id=1, name="Alice", email="alice@test.com"), ...`

Cross-backend tests seed BOTH from the same `SEED_USERS` constant.

---

## Running Tests

```bash
# Unit only (fast, 100% coverage)
uv run pytest tests/unit/ -q

# Full suite (excludes benchmarks and slow stress)
uv run pytest tests/ --ignore=tests/benchmarks -q

# Include slow stress tests
uv run pytest tests/ --ignore=tests/benchmarks --run-slow -q

# Benchmarks with comparison
uv run pytest tests/benchmarks/ --benchmark-enable --benchmark-autosave

# Compare with baseline
uv run pytest tests/benchmarks/ --benchmark-enable --benchmark-compare

# Specific adapter
uv run pytest tests/ -k "sqlalchemy" -q

# Cross-backend only
uv run pytest tests/integration/test_cross_backend.py tests/e2e/test_cross_backend_flows.py -v

# Quality checks
uv run mypy src/pypaginate/ --exclude src/pypaginate/_cli --strict --ignore-missing-imports
uv run mypy tests/unit/ --ignore-missing-imports
uv run ruff check src/pypaginate/ tests/
```

---

## Maintenance Guide

### Adding a new adapter (e.g., Django ORM)

1. Create source: `src/pypaginate/adapters/django/backend.py`
2. Create unit tests: `tests/unit/adapters/django/test_backend.py` (mock + real DB)
3. Add to cross-backend fixtures: `tests/integration/conftest.py` → add `"django"` to `params`
4. Add benchmark: `tests/benchmarks/test_django_perf.py`
5. Add to adapter comparison: `tests/benchmarks/test_adapter_comparison.py` → add `"django"` to `params`

### Adding a new feature (e.g., new operator)

1. Add operator class to `src/pypaginate/filtering/operators.py`
2. Register in `src/pypaginate/filtering/registry.py`
3. Add to `FilterOperator` Literal in `src/pypaginate/domain/specs.py`
4. Add parametrized test in `tests/unit/filtering/test_operators.py`
5. Add SA translation in `tests/unit/adapters/sqlalchemy/test_filters.py`
6. Verify coverage: `uv run pytest tests/unit/ --cov=pypaginate --cov-config=pyproject.toml`

### Reviewing test health

```bash
# Coverage must be 100%
uv run pytest tests/unit/ --cov=pypaginate --cov-config=pyproject.toml

# No mypy errors in source or tests
uv run mypy src/pypaginate/ --strict --ignore-missing-imports
uv run mypy tests/unit/ --ignore-missing-imports

# Architecture constraints hold
uv run pytest tests/architecture/ -v

# Benchmark regression check
uv run pytest tests/benchmarks/ --benchmark-enable --benchmark-compare
```

---

## PyCharm LSP Known False Positives

These warnings CANNOT be fixed and should be ignored:

| Warning | Reason |
|---------|--------|
| `pages.py`: TypeVar in Generic base | Pydantic `BaseModel + Generic[T]` pattern — works correctly |
| `pipeline.py`: Duplicate code in init | Sync/async dual-class init — inherent to the pattern |
| `_FakeBackend` not matching Protocol | PyCharm generic Protocol structural typing limitation |
| `conftest.py` AsyncIterator | SQLAlchemy async type annotation limitation |
| `test_dispatch.py` overload resolution | Intentionally testing error paths with wrong types |
| Unused `query` params in fakes | Protocol conformance requires these exact param names |
