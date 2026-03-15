"""Filtering perf — stress correctness + benchmark speed.

Verifies filter accuracy at 100K scale and benchmarks
single-spec and multi-spec filtering throughput.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.specs import FilterSpec
from tests.perf.conftest import _setup_memory_sync


# -- Stress: correctness at scale -------------------------------------------


@pytest.mark.slow
def test_filter_100k_eq_correctness(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Filter 100K by age==20, verify all results match."""
    env = _setup_memory_sync(dataset_100k)
    specs = [FilterSpec(field="age", operator="eq", value=20)]
    result = env.do_filter(env.query, specs)
    assert all(env.get_field(item, "age") == 20 for item in result)
    assert len(result) > 0


@pytest.mark.slow
def test_filter_100k_gte_correctness(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Filter 100K by age>=40, verify all results match."""
    env = _setup_memory_sync(dataset_100k)
    specs = [FilterSpec(field="age", operator="gte", value=40)]
    result = env.do_filter(env.query, specs)
    assert all(env.get_field(item, "age") >= 40 for item in result)


@pytest.mark.slow
def test_filter_100k_never_adds(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Filtering never produces more items than input."""
    env = _setup_memory_sync(dataset_100k)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = env.do_filter(env.query, specs)
    assert len(result) <= 100_000


# -- Benchmark: speed -------------------------------------------------------


@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_10k_single(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Benchmark single filter on 10K items."""
    env = _setup_memory_sync(dataset_10k)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_10k_multi(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Benchmark 3 filters on 10K items."""
    env = _setup_memory_sync(dataset_10k)
    specs = [
        FilterSpec(field="age", operator="gte", value=25),
        FilterSpec(field="age", operator="lte", value=50),
        FilterSpec(field="active", operator="eq", value=True),
    ]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Benchmark single filter on 100K items."""
    env = _setup_memory_sync(dataset_100k)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= 100_000
