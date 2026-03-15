"""Scaling curve benchmarks -- how perf degrades with size.

Parametrized benchmarks across dataset sizes for all 3 backends:
- Memory: 1K to 1M
- SA sync: 1K to 10K
- SA async: 1K to 10K
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.models import OffsetParams
from pypaginate.domain.specs import FilterSpec, SortSpec
from tests.factories.data import make_users
from tests.fixtures.backends import setup_sa_async, setup_sa_sync
from tests.perf.conftest import (
    _make_loop_and_env,
    _run_in_loop,
    _setup_memory_sync,
)


# ── Memory: paginate scaling ──────────────────────────────


@pytest.mark.benchmark(group="scale-paginate-memory")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000, 100_000, 500_000, 1_000_000],
    ids=["1K", "10K", "100K", "500K", "1M"],
)
def test_memory_paginate_scaling(benchmark: Any, size: int) -> None:
    """Memory paginate latency across dataset sizes."""
    data = make_users(size)
    env = _setup_memory_sync(data)
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == size


# ── Memory: filter scaling ────────────────────────────────


@pytest.mark.benchmark(group="scale-filter-memory")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000, 100_000],
    ids=["1K", "10K", "100K"],
)
def test_memory_filter_scaling(benchmark: Any, size: int) -> None:
    """Memory filter latency across dataset sizes."""
    data = make_users(size)
    env = _setup_memory_sync(data)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= size


# ── Memory: sort scaling ──────────────────────────────────


@pytest.mark.benchmark(group="scale-sort-memory")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000, 100_000],
    ids=["1K", "10K", "100K"],
)
def test_memory_sort_scaling(benchmark: Any, size: int) -> None:
    """Memory sort latency across dataset sizes."""
    data = make_users(size)
    env = _setup_memory_sync(data)
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == size


# ── SA sync: paginate scaling ─────────────────────────────


@pytest.mark.benchmark(group="scale-paginate-sa-sync")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000],
    ids=["1K", "10K"],
)
def test_sa_sync_paginate_scaling(benchmark: Any, size: int) -> None:
    """SA sync paginate latency across dataset sizes."""
    data = make_users(size)
    loop = asyncio.new_event_loop()
    try:
        env = loop.run_until_complete(setup_sa_sync(data))
    finally:
        loop.close()
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == size


# ── SA sync: filter scaling ───────────────────────────────


@pytest.mark.benchmark(group="scale-filter-sa-sync")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000],
    ids=["1K", "10K"],
)
def test_sa_sync_filter_scaling(benchmark: Any, size: int) -> None:
    """SA sync filter query-build latency across sizes."""
    data = make_users(size)
    loop = asyncio.new_event_loop()
    try:
        env = loop.run_until_complete(setup_sa_sync(data))
    finally:
        loop.close()
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    benchmark(env.do_filter, env.query, specs)


# ── SA sync: sort scaling ─────────────────────────────────


@pytest.mark.benchmark(group="scale-sort-sa-sync")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000],
    ids=["1K", "10K"],
)
def test_sa_sync_sort_scaling(benchmark: Any, size: int) -> None:
    """SA sync sort query-build latency across sizes."""
    data = make_users(size)
    loop = asyncio.new_event_loop()
    try:
        env = loop.run_until_complete(setup_sa_sync(data))
    finally:
        loop.close()
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    benchmark(env.do_sort, env.query, specs)


# ── SA async: paginate scaling ────────────────────────────


@pytest.mark.benchmark(group="scale-paginate-sa-async")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000],
    ids=["1K", "10K"],
)
def test_sa_async_paginate_scaling(benchmark: Any, size: int) -> None:
    """SA async paginate latency across dataset sizes."""
    data = make_users(size)
    loop, env = _make_loop_and_env(setup_sa_async, data)
    params = OffsetParams(page=1, limit=20)

    def _do() -> Any:
        return _run_in_loop(loop, env.do_paginate(env.query, params))

    result = benchmark(_do)
    assert result.total == size


# ── SA async: filter scaling ──────────────────────────────


@pytest.mark.benchmark(group="scale-filter-sa-async")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000],
    ids=["1K", "10K"],
)
def test_sa_async_filter_scaling(benchmark: Any, size: int) -> None:
    """SA async filter query-build latency across sizes."""
    data = make_users(size)
    loop, env = _make_loop_and_env(setup_sa_async, data)
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    benchmark(env.do_filter, env.query, specs)
    loop.close()


# ── SA async: sort scaling ────────────────────────────────


@pytest.mark.benchmark(group="scale-sort-sa-async")
@pytest.mark.parametrize(
    "size",
    [1_000, 10_000],
    ids=["1K", "10K"],
)
def test_sa_async_sort_scaling(benchmark: Any, size: int) -> None:
    """SA async sort query-build latency across sizes."""
    data = make_users(size)
    loop, env = _make_loop_and_env(setup_sa_async, data)
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    benchmark(env.do_sort, env.query, specs)
    loop.close()
