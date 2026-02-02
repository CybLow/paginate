# Benchmark Workflow

Run performance benchmarks using pytest-benchmark.

## Commands

```bash
# Run all benchmarks
uv run pytest -m benchmark --benchmark-only

# Run benchmarks with comparison
uv run pytest -m benchmark --benchmark-compare

# Run benchmarks and save results
uv run pytest -m benchmark --benchmark-save=baseline

# Compare against saved baseline
uv run pytest -m benchmark --benchmark-compare=baseline

# Run with detailed stats
uv run pytest -m benchmark --benchmark-verbose

# Generate JSON report
uv run pytest -m benchmark --benchmark-json=benchmark.json

# Run specific benchmark
uv run pytest tests/benchmarks/test_pagination_perf.py -m benchmark
```

## Writing Benchmarks

```python
import pytest

@pytest.mark.benchmark
def test_pagination_performance(benchmark):
    """Benchmark pagination speed."""
    def paginate():
        paginator = Paginator(page=1, per_page=100)
        return paginator.paginate(large_dataset)
    
    result = benchmark(paginate)
    assert result.total > 0

@pytest.mark.benchmark
def test_filter_performance(benchmark):
    """Benchmark filter application."""
    benchmark.pedantic(
        apply_filters,
        args=(data, filters),
        iterations=100,
        rounds=10,
    )
```

## Benchmark Options

| Option | Purpose |
|--------|---------|
| `--benchmark-min-rounds=N` | Minimum rounds per test |
| `--benchmark-max-time=N` | Max time per benchmark |
| `--benchmark-warmup=on/off` | Enable warmup iterations |
| `--benchmark-disable-gc` | Disable GC during benchmark |
| `--benchmark-histogram` | Generate histogram |

## Analyzing Results

```bash
# Compare two runs
uv run pytest-benchmark compare baseline current

# Generate histogram
uv run pytest -m benchmark --benchmark-histogram=perf
```
