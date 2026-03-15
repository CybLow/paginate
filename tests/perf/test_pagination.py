"""Pagination perf -- stress correctness + benchmark speed.

Stress tests verify correctness at scale (100K memory, 10K SA).
Benchmarks measure throughput across all 3 backends.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from pypaginate.domain.models import OffsetParams
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import (
    _run_in_loop,
    _setup_memory_sync,
    _setup_sa_async_with_loop,
    _setup_sa_sync_for_bench,
)


# -- Stress: memory at 100K ------------------------------------------------


@pytest.mark.slow
def test_paginate_100k_total(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Paginate 100K items, verify total is correct."""
    env = _setup_memory_sync(dataset_100k)
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=100))
    assert page.total == 100_000


@pytest.mark.slow
def test_paginate_100k_all_pages(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Iterate ALL pages of 100K items, verify completeness."""
    env = _setup_memory_sync(dataset_100k)
    collected = 0
    page_num = 1
    while True:
        page = env.do_paginate(env.query, OffsetParams(page=page_num, limit=1000))
        collected += len(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert collected == 100_000


@pytest.mark.slow
def test_paginate_100k_no_duplicates(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """All pages combined have no duplicate IDs."""
    env = _setup_memory_sync(dataset_100k)
    ids: set[int] = set()
    page_num = 1
    while True:
        page = env.do_paginate(env.query, OffsetParams(page=page_num, limit=1000))
        for item in page.items:
            ids.add(env.get_field(item, "id"))
        if not page.has_next:
            break
        page_num += 1
    assert len(ids) == 100_000


# -- Stress: SA sync at 10K ------------------------------------------------


@pytest.mark.slow
def test_sa_sync_paginate_10k_total(
    dataset_10k: list[dict[str, Any]],
) -> None:
    """SA sync: paginate 10K items, verify total."""
    env = _setup_sa_sync_for_bench(dataset_10k)
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=100))
    assert page.total == 10_000


# -- Stress: SA async at 10K -----------------------------------------------


@pytest.mark.slow
def test_sa_async_paginate_10k_total(
    dataset_10k: list[dict[str, Any]],
) -> None:
    """SA async: paginate 10K items, verify total."""
    loop, env = _setup_sa_async_with_loop(dataset_10k)
    try:
        coro = env.do_paginate(env.query, OffsetParams(page=1, limit=100))
        page = _run_in_loop(loop, coro)
        assert page.total == 10_000
    finally:
        loop.close()


# -- Benchmark: memory -----------------------------------------------------


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_memory_1k(
    benchmark: Any,
    memory_env_1k: BackendEnv,
) -> None:
    """Benchmark paginate on 1K items (memory)."""
    env = memory_env_1k
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 1_000


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_memory_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """Benchmark paginate on 10K items (memory)."""
    env = memory_env_10k
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 10_000


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_memory_100k(
    benchmark: Any,
    memory_env_100k: BackendEnv,
) -> None:
    """Benchmark paginate on 100K items (memory)."""
    env = memory_env_100k
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 100_000


# -- Benchmark: SA sync ----------------------------------------------------


@pytest.mark.benchmark(group="paginate-sa-sync")
def test_bench_paginate_sa_sync_1k(
    benchmark: Any,
    sa_sync_env_1k: BackendEnv,
) -> None:
    """Benchmark paginate on 1K items (SA sync)."""
    env = sa_sync_env_1k
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 1_000


@pytest.mark.benchmark(group="paginate-sa-sync")
def test_bench_paginate_sa_sync_10k(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """Benchmark paginate on 10K items (SA sync)."""
    env = sa_sync_env_10k
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 10_000


# -- Benchmark: SA async ---------------------------------------------------


@pytest.mark.benchmark(group="paginate-sa-async")
def test_bench_paginate_sa_async_1k(
    benchmark: Any,
    sa_async_env_1k: BackendEnv,
    sa_async_loop_1k: asyncio.AbstractEventLoop,
) -> None:
    """Benchmark paginate on 1K items (SA async)."""
    env = sa_async_env_1k
    loop = sa_async_loop_1k
    params = OffsetParams(page=1, limit=20)

    def _do() -> Any:
        return _run_in_loop(loop, env.do_paginate(env.query, params))

    result = benchmark(_do)
    assert result.total == 1_000


@pytest.mark.benchmark(group="paginate-sa-async")
def test_bench_paginate_sa_async_10k(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
    sa_async_loop_10k: asyncio.AbstractEventLoop,
) -> None:
    """Benchmark paginate on 10K items (SA async)."""
    env = sa_async_env_10k
    loop = sa_async_loop_10k
    params = OffsetParams(page=1, limit=20)

    def _do() -> Any:
        return _run_in_loop(loop, env.do_paginate(env.query, params))

    result = benchmark(_do)
    assert result.total == 10_000
