# Performance Benchmarks

pypaginate tracks performance automatically on every commit and pull request.

## Live Dashboard

View the interactive benchmark charts:

**[Benchmark Dashboard](https://cyblow.github.io/paginate/dev/bench/)**

The dashboard shows historical performance trends across all benchmark categories,
updated automatically when changes merge to `main`.

## What We Measure

| Category | File | Description |
|----------|------|-------------|
| Pagination | `test_pagination.py` | Core offset/cursor pagination throughput |
| Filtering | `test_filtering.py` | Filter engine across all operators |
| Sorting | `test_sorting.py` | Sort engine with various dataset sizes |
| Search | `test_search.py` | Text search and fuzzy matching |
| Pipeline | `test_pipeline.py` | End-to-end pipeline composition overhead |
| Scaling | `test_scaling.py` | 1K to 1M items scaling behavior |
| FastAPI | `test_fastapi_perf.py` | HTTP endpoint response overhead |
| Serialization | `test_serialization.py` | Page model serialization speed |
| Overhead | `test_overhead.py` | Full ops to paginate to serialize path |
| Boundaries | `test_boundary.py` | Edge case performance |
| Comparison | `test_comparison.py` | pypaginate vs raw Python |
| Competitors | `test_competitors.py` | vs other pagination libraries |

## Running Locally

```bash
# Run all benchmarks
uv run pytest tests/perf --benchmark-enable -v

# Run specific category
uv run pytest tests/perf/test_pagination.py --benchmark-enable -v

# Save results for comparison
uv run pytest tests/perf --benchmark-enable --benchmark-autosave

# Compare against a saved baseline
uv run pytest tests/perf --benchmark-enable --benchmark-compare=0001

# Generate JSON output
uv run pytest tests/perf --benchmark-enable --benchmark-json=results.json
```

## CI Pipeline

The full CI pipeline runs **40+ concurrent jobs** across 4 Python versions and 3 operating systems:

```{mermaid}
graph TD
    S[Setup] --> Q[Quality<br>ruff + mypy]
    S --> SEC[Security<br>bandit + pip-audit]
    S --> CQL[CodeQL]

    Q --> ARCH[Architecture<br>72 subtests]
    Q --> U1[Unit 3.11<br>Linux / macOS / Win]
    Q --> U2[Unit 3.12<br>Linux / macOS / Win]
    Q --> U3[Unit 3.13<br>Linux / macOS / Win]
    Q --> U4[Unit 3.14<br>Linux / macOS / Win]

    U1 & U2 & U3 & U4 --> I[Integration<br>4 Py × 3 OS = 12 jobs]
    U1 & U2 & U3 & U4 --> E2E[E2E Tests<br>6 FastAPI flows]
    U1 & U2 & U3 & U4 --> PG[PostgreSQL<br>real Postgres 16]
    U1 & U2 & U3 & U4 --> PROP[Property<br>Hypothesis]
    U1 & U2 & U3 & U4 --> BENCH[Benchmarks<br>293 data points]
    U1 & U2 & U3 & U4 --> BUILD[Build<br>hatchling + twine]

    style S fill:#1f6feb,color:#fff
    style Q fill:#238636,color:#fff
    style ARCH fill:#238636,color:#fff
    style BENCH fill:#d29922,color:#fff
    style PG fill:#8957e5,color:#fff
```

| Test Suite | Jobs | Coverage |
|------------|------|----------|
| Unit | 12 (4 Python × 3 OS) | All modules, parallel execution |
| Integration | 12 (4 Python × 3 OS) | Cross-module with real SQLite |
| E2E | 1 | Full FastAPI user journeys |
| PostgreSQL | 1 | Real Postgres 16 via service container |
| Property | 1 | Hypothesis invariant checking |
| Architecture | 1 | File limits, imports, protocols |
| Benchmarks | 1 | 293 perf benchmarks, PR regression alerts |
| **Total** | **29+** | **872+ tests, 85% coverage gate** |

Benchmarks run automatically:

- **On `main`**: full benchmark suite, results stored for historical tracking
- **On pull requests**: full suite with comparison against `main` baseline

When a PR introduces a performance regression exceeding **20%**, the CI flags it
with a comment on the pull request showing the before/after comparison.

## Benchmark Datasets

Tests use pre-generated datasets at various scales:

| Dataset | Size | Purpose |
|---------|------|---------|
| `dataset_1k` | 1,000 items | Fast iteration, basic correctness |
| `dataset_10k` | 10,000 items | Standard workload |
| `dataset_100k` | 100,000 items | Medium scale |
| `dataset_500k` | 500,000 items | Large scale |
| `dataset_1m` | 1,000,000 items | Stress testing |

Each dataset contains user-like dictionaries with name, email, age, status, and
timestamp fields.

## Interpreting Results

- **Median** is the primary metric (more stable than mean)
- **IQR** (interquartile range) shows result stability
- **Rounds** indicates how many iterations were run
- Compare results on the **same machine/environment** for accuracy
- CI comparisons account for runner variability with a 20% threshold
