"""Pipeline perf -- stress correctness + benchmark speed.

Full pipeline: filter + sort + paginate at scale.
Tests all 3 backends (memory at 100K, SA at 10K).
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import (
    _run_in_loop,
    _setup_memory_sync,
    _setup_sa_async_with_loop,
    _setup_sa_sync_for_bench,
)


# -- Stress: memory at 100K ------------------------------------------------


@pytest.mark.slow
def test_pipeline_100k_correctness(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Full pipeline on 100K: filter + sort + paginate."""
    env = _setup_memory_sync(dataset_100k)
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=50)
    page = env.do_pipeline(env.query, params, filters=filters, sorting=sorting)
    assert page.total > 0
    assert len(page.items) <= 50
    ages = [env.get_field(item, "age") for item in page.items]
    assert all(a >= 30 for a in ages)


@pytest.mark.slow
def test_pipeline_100k_all_filtered_pages(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Iterate all pipeline pages, verify completeness."""
    env = _setup_memory_sync(dataset_100k)
    filters = [FilterSpec(field="age", operator="gte", value=40)]
    collected = 0
    page_num = 1
    while True:
        page = env.do_pipeline(
            env.query,
            OffsetParams(page=page_num, limit=500),
            filters=filters,
        )
        collected += len(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert collected == page.total


# -- Stress: SA sync at 10K ------------------------------------------------


@pytest.mark.slow
def test_sa_sync_pipeline_10k(
    dataset_10k: list[dict[str, Any]],
) -> None:
    """SA sync: pipeline 10K with sort, verify page."""
    env = _setup_sa_sync_for_bench(dataset_10k)
    sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=50)
    page = env.do_pipeline(env.query, params, sorting=sorting)
    assert page.total == 10_000
    assert len(page.items) <= 50


# -- Stress: SA async at 10K -----------------------------------------------


@pytest.mark.slow
def test_sa_async_pipeline_10k(
    dataset_10k: list[dict[str, Any]],
) -> None:
    """SA async: pipeline 10K with sort, verify page."""
    loop, env = _setup_sa_async_with_loop(dataset_10k)
    try:
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
        params = OffsetParams(page=1, limit=50)
        coro = env.do_pipeline(env.query, params, sorting=sorting)
        page = _run_in_loop(loop, coro)
        assert page.total == 10_000
        assert len(page.items) <= 50
    finally:
        loop.close()


# -- Benchmark: memory -----------------------------------------------------


@pytest.mark.benchmark(group="pipeline-memory")
def test_bench_pipeline_memory_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """Benchmark full pipeline on 10K items (memory)."""
    env = memory_env_10k
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)
    result = benchmark(
        env.do_pipeline,
        env.query,
        params,
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="pipeline-memory")
def test_bench_pipeline_memory_100k(
    benchmark: Any,
    memory_env_100k: BackendEnv,
) -> None:
    """Benchmark full pipeline on 100K items (memory)."""
    env = memory_env_100k
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)
    result = benchmark(
        env.do_pipeline,
        env.query,
        params,
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0


# -- Benchmark: SA sync ----------------------------------------------------


@pytest.mark.benchmark(group="pipeline-sa-sync")
def test_bench_pipeline_sa_sync_1k(
    benchmark: Any,
    sa_sync_env_1k: BackendEnv,
) -> None:
    """Benchmark pipeline on 1K items (SA sync)."""
    env = sa_sync_env_1k
    sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)
    result = benchmark(env.do_pipeline, env.query, params, sorting=sorting)
    assert result.total == 1_000


@pytest.mark.benchmark(group="pipeline-sa-sync")
def test_bench_pipeline_sa_sync_10k(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """Benchmark pipeline on 10K items (SA sync)."""
    env = sa_sync_env_10k
    sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)
    result = benchmark(env.do_pipeline, env.query, params, sorting=sorting)
    assert result.total == 10_000


# -- Benchmark: SA async ---------------------------------------------------


@pytest.mark.benchmark(group="pipeline-sa-async")
def test_bench_pipeline_sa_async_1k(
    benchmark: Any,
    sa_async_env_1k: BackendEnv,
    sa_async_loop_1k: asyncio.AbstractEventLoop,
) -> None:
    """Benchmark pipeline on 1K items (SA async)."""
    env = sa_async_env_1k
    loop = sa_async_loop_1k
    sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)

    def _do() -> Any:
        coro = env.do_pipeline(env.query, params, sorting=sorting)
        return _run_in_loop(loop, coro)

    result = benchmark(_do)
    assert result.total == 1_000


@pytest.mark.benchmark(group="pipeline-sa-async")
def test_bench_pipeline_sa_async_10k(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
    sa_async_loop_10k: asyncio.AbstractEventLoop,
) -> None:
    """Benchmark pipeline on 10K items (SA async)."""
    env = sa_async_env_10k
    loop = sa_async_loop_10k
    sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)

    def _do() -> Any:
        coro = env.do_pipeline(env.query, params, sorting=sorting)
        return _run_in_loop(loop, coro)

    result = benchmark(_do)
    assert result.total == 10_000
