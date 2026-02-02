---
name: perf-ops
description: >
  Performance testing in CI/CD. Covers benchmark pipelines, regression detection,
  continuous benchmarking with pytest-benchmark, and automated performance gates.
related:
  - perf-core
  - perf-slo
  - test-ops
  - test-load
---

## PERFOPS: PERFORMANCE IN CI/CD

Integrate performance testing into your development workflow to catch regressions early.

---

### Performance Testing Pipeline

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Nightly baseline

env:
  BASELINE_FILE: performance-baseline.json

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: Run benchmarks
        run: |
          uv run pytest tests/benchmark \
            --benchmark-json=benchmark-results.json \
            --benchmark-compare \
            --benchmark-compare-fail=mean:10%
            
      - name: Check for regressions
        run: |
          python scripts/check_performance.py \
            --current benchmark-results.json \
            --baseline $BASELINE_FILE \
            --threshold 10
            
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark-results.json
          
      - name: Update baseline (main only)
        if: github.ref == 'refs/heads/main'
        run: |
          mv benchmark-results.json $BASELINE_FILE
          git add $BASELINE_FILE
          git commit -m "chore: update performance baseline" || true
          git push
```

### Benchmark Regression Detection

```python
# scripts/check_performance.py
"""Check for performance regressions."""
import json
import sys
from pathlib import Path


def check_regressions(
    current_file: str,
    baseline_file: str,
    threshold_percent: float = 10.0,
) -> list[dict]:
    """Compare current results against baseline."""
    current = json.loads(Path(current_file).read_text())
    baseline = json.loads(Path(baseline_file).read_text())
    
    regressions = []
    
    for bench in current["benchmarks"]:
        name = bench["name"]
        current_mean = bench["stats"]["mean"]
        
        # Find matching baseline
        baseline_bench = next(
            (b for b in baseline["benchmarks"] if b["name"] == name),
            None
        )
        if baseline_bench is None:
            continue
            
        baseline_mean = baseline_bench["stats"]["mean"]
        change_percent = ((current_mean - baseline_mean) / baseline_mean) * 100
        
        if change_percent > threshold_percent:
            regressions.append({
                "name": name,
                "baseline_ms": baseline_mean * 1000,
                "current_ms": current_mean * 1000,
                "change_percent": change_percent,
            })
    
    return regressions


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--threshold", type=float, default=10.0)
    args = parser.parse_args()
    
    regressions = check_regressions(
        args.current,
        args.baseline,
        args.threshold,
    )
    
    if regressions:
        print("Performance regressions detected:")
        for r in regressions:
            print(f"  {r['name']}: {r['baseline_ms']:.2f}ms -> {r['current_ms']:.2f}ms "
                  f"(+{r['change_percent']:.1f}%)")
        sys.exit(1)
    
    print("No performance regressions detected")
```

### Continuous Benchmarking

```python
# tests/benchmark/test_core_performance.py
import pytest


class TestCorePerformance:
    """Benchmark critical code paths."""

    @pytest.mark.benchmark(group="pagination")
    def test_paginate_small_list(self, benchmark):
        """Paginate small list performance."""
        items = list(range(100))
        result = benchmark(paginate, items, page=1, per_page=10)
        assert len(result.items) == 10

    @pytest.mark.benchmark(group="pagination")
    def test_paginate_large_list(self, benchmark):
        """Paginate large list performance."""
        items = list(range(100_000))
        result = benchmark(paginate, items, page=500, per_page=100)
        assert len(result.items) == 100

    @pytest.mark.benchmark(group="serialization")
    def test_serialize_model(self, benchmark):
        """Model serialization performance."""
        user = User(id=1, name="Test", email="test@example.com")
        result = benchmark(user.model_dump_json)
        assert "test@example.com" in result

    @pytest.mark.benchmark(group="database")
    def test_query_with_joins(self, benchmark, db_session):
        """Complex query performance."""
        def run_query():
            return (
                db_session.query(Order)
                .options(joinedload(Order.user), selectinload(Order.items))
                .filter(Order.status == "active")
                .limit(100)
                .all()
            )
        
        result = benchmark(run_query)
        assert len(result) <= 100
```

---

## PERFORMANCE GATES

### Automated Quality Gates

```python
# conftest.py
import pytest


@pytest.fixture
def performance_gate():
    """Assert performance constraints."""
    class PerformanceGate:
        def __init__(self):
            self.assertions = []
        
        def assert_under(self, metric_name: str, threshold_ms: float):
            self.assertions.append((metric_name, threshold_ms))
        
        def check(self, results: dict):
            failures = []
            for name, threshold in self.assertions:
                actual = results.get(name, 0) * 1000  # Convert to ms
                if actual > threshold:
                    failures.append(f"{name}: {actual:.2f}ms > {threshold}ms")
            
            if failures:
                pytest.fail("\n".join(failures))
    
    return PerformanceGate()


def test_api_performance(performance_gate, benchmark):
    """Test API endpoint performance."""
    performance_gate.assert_under("mean", 50)  # P50 < 50ms
    performance_gate.assert_under("max", 200)  # Max < 200ms
    
    result = benchmark(call_api_endpoint)
    performance_gate.check(benchmark.stats)
```

### PR Comment with Results

```yaml
# .github/workflows/performance.yml (continued)
- name: Comment on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const results = JSON.parse(fs.readFileSync('benchmark-results.json'));
      
      let comment = '## Performance Results\n\n';
      comment += '| Benchmark | Mean | Min | Max |\n';
      comment += '|-----------|------|-----|-----|\n';
      
      for (const bench of results.benchmarks) {
        const mean = (bench.stats.mean * 1000).toFixed(2);
        const min = (bench.stats.min * 1000).toFixed(2);
        const max = (bench.stats.max * 1000).toFixed(2);
        comment += `| ${bench.name} | ${mean}ms | ${min}ms | ${max}ms |\n`;
      }
      
      await github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

---

## QUICK REFERENCE

### pytest-benchmark Commands

```bash
# Run benchmarks
uv run pytest tests/benchmark --benchmark-only

# Compare to baseline
uv run pytest --benchmark-compare=baseline.json

# Fail on regression
uv run pytest --benchmark-compare-fail=mean:10%

# Save results
uv run pytest --benchmark-json=results.json

# Group by fixture
uv run pytest --benchmark-group-by=group
```

### Performance Thresholds

| Metric | Warning | Error |
|--------|---------|-------|
| P50 latency | > 50ms | > 100ms |
| P95 latency | > 150ms | > 300ms |
| P99 latency | > 300ms | > 500ms |
| Regression | > 5% | > 10% |
