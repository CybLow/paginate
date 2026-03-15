"""Scaling curve benchmarks — how perf degrades with size.

Parametrized benchmarks across 1K to 1M for paginate,
filter, and sort to reveal scaling characteristics.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.models import OffsetParams
from pypaginate.domain.specs import FilterSpec, SortSpec
from tests.factories.data import make_users
from tests.perf.conftest import _setup_memory_sync


# -- Paginate scaling -------------------------------------------------------


@pytest.mark.benchmark(group="scaling-paginate")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000, 100_000, 500_000, 1_000_000],
    ids=["1K", "10K", "100K", "500K", "1M"],
)
def test_paginate_scaling(benchmark: Any, size: int) -> None:
    """Measure paginate latency across dataset sizes."""
    data = make_users(size)
    env = _setup_memory_sync(data)
    result = benchmark(
        env.do_paginate,
        env.query,
        OffsetParams(page=1, limit=20),
    )
    assert result.total == size


# -- Filter scaling ---------------------------------------------------------


@pytest.mark.benchmark(group="scaling-filter")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000, 100_000],
    ids=["1K", "10K", "100K"],
)
def test_filter_scaling(benchmark: Any, size: int) -> None:
    """Measure filter latency across dataset sizes."""
    data = make_users(size)
    env = _setup_memory_sync(data)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= size


# -- Sort scaling -----------------------------------------------------------


@pytest.mark.benchmark(group="scaling-sort")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000, 100_000],
    ids=["1K", "10K", "100K"],
)
def test_sort_scaling(benchmark: Any, size: int) -> None:
    """Measure sort latency across dataset sizes."""
    data = make_users(size)
    env = _setup_memory_sync(data)
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == size
