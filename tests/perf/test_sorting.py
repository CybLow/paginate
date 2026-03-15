"""Sorting perf — stress correctness + benchmark speed.

Verifies sort order at 100K scale and benchmarks
sort throughput at various dataset sizes.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.specs import SortSpec
from tests.perf.conftest import _setup_memory_sync


# -- Stress: correctness at scale -------------------------------------------


@pytest.mark.slow
def test_sort_100k_asc_order(dataset_100k: list[dict[str, Any]]) -> None:
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


# -- Benchmark: speed -------------------------------------------------------


@pytest.mark.benchmark(group="sort-memory")
def test_bench_sort_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Benchmark sort on 10K items."""
    env = _setup_memory_sync(dataset_10k)
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == 10_000


@pytest.mark.benchmark(group="sort-memory")
def test_bench_sort_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Benchmark sort on 100K items."""
    env = _setup_memory_sync(dataset_100k)
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == 100_000
