"""Side-by-side adapter comparison benchmarks.

Compares memory, SA sync, SA async, and raw baselines in the same groups.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import _run_in_loop


# -- Paginate --------------------------------------------------


@pytest.mark.benchmark(group="compare-paginate-10k")
def test_memory_paginate_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """pypaginate memory paginate on 10K."""
    result = benchmark(
        memory_env_10k.do_paginate,
        memory_env_10k.query,
        OffsetParams(page=50, limit=20),
    )
    assert result.total == 10_000


@pytest.mark.benchmark(group="compare-paginate-10k")
def test_sa_sync_paginate_10k(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """pypaginate SA sync paginate on 10K."""
    result = benchmark(
        sa_sync_env_10k.do_paginate,
        sa_sync_env_10k.query,
        OffsetParams(page=50, limit=20),
    )
    assert result.total == 10_000


@pytest.mark.benchmark(group="compare-paginate-10k")
def test_sa_async_paginate_10k(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
    sa_async_loop_10k: asyncio.AbstractEventLoop,
) -> None:
    """pypaginate SA async paginate on 10K."""
    params = OffsetParams(page=50, limit=20)
    coro_fn = sa_async_env_10k.do_paginate

    def _do() -> Any:
        return _run_in_loop(sa_async_loop_10k, coro_fn(sa_async_env_10k.query, params))

    result = benchmark(_do)
    assert result.total == 10_000


@pytest.mark.benchmark(group="compare-paginate-10k")
def test_raw_list_slice_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Baseline: raw Python list slicing (no pypaginate)."""
    result = benchmark(lambda: {"items": dataset_10k[980:1000], "total": len(dataset_10k)})
    assert result["total"] == 10_000


# -- Filter ----------------------------------------------------


@pytest.mark.benchmark(group="compare-filter-10k")
def test_memory_filter_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """pypaginate memory filter on 10K."""
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(memory_env_10k.do_filter, memory_env_10k.query, specs)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="compare-filter-10k")
def test_raw_list_filter_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Baseline: raw list comprehension filter."""

    def raw_filter() -> list[dict[str, Any]]:
        return [d for d in dataset_10k if d["age"] >= 30]

    result = benchmark(raw_filter)
    assert len(result) <= 10_000


# -- Sort ------------------------------------------------------


@pytest.mark.benchmark(group="compare-sort-10k")
def test_memory_sort_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """pypaginate memory sort on 10K."""
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(memory_env_10k.do_sort, memory_env_10k.query, specs)
    assert len(result) == 10_000


@pytest.mark.benchmark(group="compare-sort-10k")
def test_raw_list_sort_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Baseline: raw sorted() call."""

    def raw_sort() -> list[dict[str, Any]]:
        return sorted(dataset_10k, key=lambda d: d["age"])

    result = benchmark(raw_sort)
    assert len(result) == 10_000


# -- Search ----------------------------------------------------


@pytest.mark.benchmark(group="compare-search-10k")
def test_memory_search_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """pypaginate memory search on 10K."""
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(memory_env_10k.do_search, memory_env_10k.query, spec)
    assert len(result) >= 0


@pytest.mark.benchmark(group="compare-search-10k")
def test_raw_list_search_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Baseline: raw string matching."""

    def raw_search() -> list[dict[str, Any]]:
        q = "user_5"
        return [d for d in dataset_10k if q in d["name"].lower()]

    result = benchmark(raw_search)
    assert len(result) >= 0


# -- Pipeline --------------------------------------------------


@pytest.mark.benchmark(group="compare-pipeline-10k")
def test_memory_pipeline_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """pypaginate memory pipeline on 10K."""
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(
        memory_env_10k.do_pipeline,
        memory_env_10k.query,
        OffsetParams(page=1, limit=20),
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="compare-pipeline-10k")
def test_raw_pipeline_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Baseline: raw Python filter + sort + slice."""

    def raw_pipeline() -> dict[str, Any]:
        filtered = [u for u in dataset_10k if u["age"] >= 30]
        sorted_items = sorted(filtered, key=lambda u: u["name"])
        return {"items": sorted_items[0:20], "total": len(sorted_items)}

    result = benchmark(raw_pipeline)
    assert result["total"] > 0
