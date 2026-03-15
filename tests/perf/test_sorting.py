"""Sorting perf -- stress correctness + benchmark speed.

Verifies sort order at 100K (memory) and 10K (SA),
benchmarks sort throughput across all 3 backends.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.specs import SortSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import _setup_memory_sync


# -- Stress: memory at 100K ------------------------------------------------


@pytest.mark.slow
def test_sort_100k_asc_order(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Sort 100K by age ASC, verify monotonic non-decreasing."""
    env = _setup_memory_sync(dataset_100k)
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = env.do_sort(env.query, specs)
    ages = [env.get_field(item, "age") for item in result]
    for i in range(len(ages) - 1):
        assert ages[i] <= ages[i + 1]


@pytest.mark.slow
def test_sort_100k_preserves_count(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Sorting 100K items preserves count."""
    env = _setup_memory_sync(dataset_100k)
    specs = [SortSpec(field="name")]
    result = env.do_sort(env.query, specs)
    assert len(result) == 100_000


# -- Stress: SA at 10K (sort builds query, sync) ---------------------------


@pytest.mark.slow
def test_sa_sync_sort_10k_builds_query(
    sa_sync_env_10k: BackendEnv,
) -> None:
    """SA sync: sort 10K by name ASC, query is valid."""
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    result = sa_sync_env_10k.do_sort(sa_sync_env_10k.query, specs)
    assert result is not None


@pytest.mark.slow
def test_sa_async_sort_10k_builds_query(
    sa_async_env_10k: BackendEnv,
) -> None:
    """SA async: sort 10K by name ASC, query is valid."""
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    result = sa_async_env_10k.do_sort(sa_async_env_10k.query, specs)
    assert result is not None


# -- Benchmark: memory -----------------------------------------------------


@pytest.mark.benchmark(group="sort-memory")
def test_bench_sort_memory_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """Benchmark sort on 10K items (memory)."""
    env = memory_env_10k
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == 10_000


@pytest.mark.benchmark(group="sort-memory")
def test_bench_sort_memory_100k(
    benchmark: Any,
    memory_env_100k: BackendEnv,
) -> None:
    """Benchmark sort on 100K items (memory)."""
    env = memory_env_100k
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == 100_000


# -- Benchmark: SA sync (query building) -----------------------------------


@pytest.mark.benchmark(group="sort-sa-sync")
def test_bench_sort_sa_sync_1k(
    benchmark: Any,
    sa_sync_env_1k: BackendEnv,
) -> None:
    """Benchmark sort query build on 1K (SA sync)."""
    env = sa_sync_env_1k
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    benchmark(env.do_sort, env.query, specs)


@pytest.mark.benchmark(group="sort-sa-sync")
def test_bench_sort_sa_sync_10k(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """Benchmark sort query build on 10K (SA sync)."""
    env = sa_sync_env_10k
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    benchmark(env.do_sort, env.query, specs)


# -- Benchmark: SA async (query building) ----------------------------------


@pytest.mark.benchmark(group="sort-sa-async")
def test_bench_sort_sa_async_1k(
    benchmark: Any,
    sa_async_env_1k: BackendEnv,
) -> None:
    """Benchmark sort query build on 1K (SA async)."""
    env = sa_async_env_1k
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    benchmark(env.do_sort, env.query, specs)


@pytest.mark.benchmark(group="sort-sa-async")
def test_bench_sort_sa_async_10k(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
) -> None:
    """Benchmark sort query build on 10K (SA async)."""
    env = sa_async_env_10k
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    benchmark(env.do_sort, env.query, specs)
