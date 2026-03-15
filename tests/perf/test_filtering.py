"""Filtering perf -- stress correctness + benchmark speed.

Verifies filter accuracy at 100K (memory) and 10K (SA),
benchmarks single/multi-spec filtering across all backends.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.specs import FilterSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import _setup_memory_sync


# -- Stress: memory at 100K ------------------------------------------------


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


# -- Stress: SA at 10K (filter builds query, sync) -------------------------


@pytest.mark.slow
def test_sa_sync_filter_10k_builds_query(
    sa_sync_env_10k: BackendEnv,
) -> None:
    """SA sync: filter 10K by name starts_with, query is valid."""
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    result = sa_sync_env_10k.do_filter(sa_sync_env_10k.query, specs)
    assert result is not None


@pytest.mark.slow
def test_sa_async_filter_10k_builds_query(
    sa_async_env_10k: BackendEnv,
) -> None:
    """SA async: filter 10K by name starts_with, query is valid."""
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    result = sa_async_env_10k.do_filter(sa_async_env_10k.query, specs)
    assert result is not None


# -- Benchmark: memory -----------------------------------------------------


@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_memory_10k_single(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """Benchmark single filter on 10K items (memory)."""
    env = memory_env_10k
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_memory_10k_multi(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """Benchmark 3 filters on 10K items (memory)."""
    env = memory_env_10k
    specs = [
        FilterSpec(field="age", operator="gte", value=25),
        FilterSpec(field="age", operator="lte", value=50),
        FilterSpec(field="active", operator="eq", value=True),
    ]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="filter-memory")
def test_bench_filter_memory_100k(
    benchmark: Any,
    memory_env_100k: BackendEnv,
) -> None:
    """Benchmark single filter on 100K items (memory)."""
    env = memory_env_100k
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= 100_000


# -- Benchmark: SA sync (query building) -----------------------------------


@pytest.mark.benchmark(group="filter-sa-sync")
def test_bench_filter_sa_sync_1k(
    benchmark: Any,
    sa_sync_env_1k: BackendEnv,
) -> None:
    """Benchmark filter query build on 1K (SA sync)."""
    env = sa_sync_env_1k
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    benchmark(env.do_filter, env.query, specs)


@pytest.mark.benchmark(group="filter-sa-sync")
def test_bench_filter_sa_sync_10k(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """Benchmark filter query build on 10K (SA sync)."""
    env = sa_sync_env_10k
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    benchmark(env.do_filter, env.query, specs)


# -- Benchmark: SA async (query building) ----------------------------------


@pytest.mark.benchmark(group="filter-sa-async")
def test_bench_filter_sa_async_1k(
    benchmark: Any,
    sa_async_env_1k: BackendEnv,
) -> None:
    """Benchmark filter query build on 1K (SA async)."""
    env = sa_async_env_1k
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    benchmark(env.do_filter, env.query, specs)


@pytest.mark.benchmark(group="filter-sa-async")
def test_bench_filter_sa_async_10k(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
) -> None:
    """Benchmark filter query build on 10K (SA async)."""
    env = sa_async_env_10k
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    benchmark(env.do_filter, env.query, specs)
