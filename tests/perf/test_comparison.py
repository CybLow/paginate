"""Side-by-side adapter comparison benchmarks.

Compares memory backend against raw Python baselines
to quantify pypaginate overhead.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.models import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec
from tests.perf.conftest import _setup_memory_sync


# -- Paginate: pypaginate vs raw baseline -----------------------------------


@pytest.mark.benchmark(group="compare-paginate-10k")
def test_memory_paginate_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate memory paginate on 10K."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(
        env.do_paginate,
        env.query,
        OffsetParams(page=5, limit=20),
    )
    assert result.total == 10_000


@pytest.mark.benchmark(group="compare-paginate-10k")
def test_raw_list_slice_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Baseline: raw Python list slicing (no pypaginate)."""

    def raw_paginate() -> list[dict[str, Any]]:
        offset, limit = 80, 20
        return dataset_10k[offset : offset + limit]

    result = benchmark(raw_paginate)
    assert len(result) == 20


# -- Filter: pypaginate vs raw baseline -------------------------------------


@pytest.mark.benchmark(group="compare-filter-10k")
def test_memory_filter_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate memory filter on 10K."""
    env = _setup_memory_sync(dataset_10k)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
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


# -- Sort: pypaginate vs raw baseline ---------------------------------------


@pytest.mark.benchmark(group="compare-sort-10k")
def test_memory_sort_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate memory sort on 10K."""
    env = _setup_memory_sync(dataset_10k)
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
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


# -- Search: pypaginate vs raw baseline -------------------------------------


@pytest.mark.benchmark(group="compare-search-10k")
def test_memory_search_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate memory search on 10K."""
    env = _setup_memory_sync(dataset_10k)
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(env.do_search, env.query, spec)
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
