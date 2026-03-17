"""Scaling curve benchmarks -- how perf degrades with size.

Parametrized benchmarks across dataset sizes for all 3 backends:
- Memory: 1K to 1M (all operations)
- SA sync: 1K to 100K (all operations)
- SA async: 1K to 100K (all operations)

All SA benchmarks use ``do_pipeline`` which EXECUTES queries via
``session.execute()``, not ``do_filter``/``do_sort`` which only
BUILD the SQL ``Select`` object without any database round-trip.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec
from tests.factories.data import make_users
from tests.fixtures.backends import setup_sa_async, setup_sa_sync
from tests.perf.conftest import (
    _make_loop_and_env,
    _run_in_loop,
    _setup_memory_sync,
)


_SA_SIZES = [1_000, 10_000, 100_000]
_SA_IDS = ["1K", "10K", "100K"]
_slow = pytest.mark.slow
_MEM_SIZES = [
    pytest.param(1_000, id="1K"),
    pytest.param(10_000, id="10K"),
    pytest.param(100_000, id="100K"),
    pytest.param(500_000, marks=_slow, id="500K"),
    pytest.param(1_000_000, marks=_slow, id="1M"),
]
_PAG_SIZES = [
    pytest.param(1_000, id="1K"),
    pytest.param(10_000, id="10K"),
    pytest.param(100_000, id="100K"),
    pytest.param(500_000, marks=_slow, id="500K"),
    pytest.param(1_000_000, marks=_slow, id="1M"),
]
_DEFAULT_PARAMS = OffsetParams(page=1, limit=20)


# ── helpers ──────────────────────────────────────────────


def _sa_sync_env(data: list[dict[str, Any]]) -> Any:
    """Create SA sync env (setup is async, wrap with loop)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(setup_sa_sync(data))
    finally:
        loop.close()


# ═══════════════════════════════════════════════════════════
# 1. PAGINATE scaling
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-paginate-memory")
@pytest.mark.parametrize("size", _PAG_SIZES)
def test_memory_paginate_scaling(benchmark: Any, size: int) -> None:
    """Memory paginate latency across dataset sizes."""
    env = _setup_memory_sync(make_users(size))
    result = benchmark(env.do_paginate, env.query, _DEFAULT_PARAMS)
    assert result.total == size


@pytest.mark.benchmark(group="scale-paginate-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_sync_paginate_scaling(benchmark: Any, size: int) -> None:
    """SA sync paginate latency (full query execution)."""
    env = _sa_sync_env(make_users(size))
    result = benchmark(env.do_paginate, env.query, _DEFAULT_PARAMS)
    assert result.total == size


@pytest.mark.benchmark(group="scale-paginate-sa-async")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_async_paginate_scaling(benchmark: Any, size: int) -> None:
    """SA async paginate latency (full query execution)."""
    loop, env = _make_loop_and_env(setup_sa_async, make_users(size))
    params = _DEFAULT_PARAMS

    def _do() -> Any:
        return _run_in_loop(loop, env.do_paginate(env.query, params))

    result = benchmark(_do)
    assert result.total == size


# ═══════════════════════════════════════════════════════════
# 2. FILTER scaling
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-filter-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_memory_filter_scaling(benchmark: Any, size: int) -> None:
    """Memory filter latency across dataset sizes."""
    env = _setup_memory_sync(make_users(size))
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(env.do_filter, env.query, specs)
    assert len(result) <= size


@pytest.mark.benchmark(group="scale-filter-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_sync_filter_scaling(benchmark: Any, size: int) -> None:
    """SA sync filter latency (full query execution via pipeline)."""
    env = _sa_sync_env(make_users(size))
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    result = benchmark(
        env.do_pipeline,
        env.query,
        _DEFAULT_PARAMS,
        filters=specs,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="scale-filter-sa-async")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_async_filter_scaling(benchmark: Any, size: int) -> None:
    """SA async filter latency (full query execution via pipeline)."""
    loop, env = _make_loop_and_env(setup_sa_async, make_users(size))
    specs = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    params = _DEFAULT_PARAMS

    def _do() -> Any:
        return _run_in_loop(
            loop,
            env.do_pipeline(env.query, params, filters=specs),
        )

    result = benchmark(_do)
    assert result.total > 0


# ═══════════════════════════════════════════════════════════
# 3. SORT scaling
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-sort-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_memory_sort_scaling(benchmark: Any, size: int) -> None:
    """Memory sort latency across dataset sizes."""
    env = _setup_memory_sync(make_users(size))
    specs = [SortSpec(field="age", direction=SortDirection.ASC)]
    result = benchmark(env.do_sort, env.query, specs)
    assert len(result) == size


@pytest.mark.benchmark(group="scale-sort-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_sync_sort_scaling(benchmark: Any, size: int) -> None:
    """SA sync sort latency (full query execution via pipeline)."""
    env = _sa_sync_env(make_users(size))
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    result = benchmark(
        env.do_pipeline,
        env.query,
        _DEFAULT_PARAMS,
        sorting=specs,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="scale-sort-sa-async")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_async_sort_scaling(benchmark: Any, size: int) -> None:
    """SA async sort latency (full query execution via pipeline)."""
    loop, env = _make_loop_and_env(setup_sa_async, make_users(size))
    specs = [SortSpec(field="name", direction=SortDirection.ASC)]
    params = _DEFAULT_PARAMS

    def _do() -> Any:
        return _run_in_loop(
            loop,
            env.do_pipeline(env.query, params, sorting=specs),
        )

    result = benchmark(_do)
    assert result.total > 0


# ═══════════════════════════════════════════════════════════
# 4. SEARCH scaling
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-search-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_memory_search_scaling(benchmark: Any, size: int) -> None:
    """Memory search latency across dataset sizes."""
    env = _setup_memory_sync(make_users(size))
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(
        env.do_pipeline,
        env.query,
        _DEFAULT_PARAMS,
        search=spec,
    )
    assert result.total >= 0


@pytest.mark.benchmark(group="scale-search-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_sync_search_scaling(benchmark: Any, size: int) -> None:
    """SA sync search latency (full query execution via pipeline)."""
    env = _sa_sync_env(make_users(size))
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(
        env.do_pipeline,
        env.query,
        _DEFAULT_PARAMS,
        search=spec,
    )
    assert result.total >= 0


@pytest.mark.benchmark(group="scale-search-sa-async")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_async_search_scaling(benchmark: Any, size: int) -> None:
    """SA async search latency (full query execution via pipeline)."""
    loop, env = _make_loop_and_env(setup_sa_async, make_users(size))
    spec = SearchSpec(query="User_5", fields=("name",))
    params = _DEFAULT_PARAMS

    def _do() -> Any:
        return _run_in_loop(
            loop,
            env.do_pipeline(env.query, params, search=spec),
        )

    result = benchmark(_do)
    assert result.total >= 0


# ═══════════════════════════════════════════════════════════
# 5. PIPELINE scaling (filter + sort combined)
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-pipeline-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_memory_pipeline_scaling(benchmark: Any, size: int) -> None:
    """Memory pipeline (filter+sort) latency across sizes."""
    env = _setup_memory_sync(make_users(size))
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
    result = benchmark(
        env.do_pipeline,
        env.query,
        _DEFAULT_PARAMS,
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="scale-pipeline-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_sync_pipeline_scaling(benchmark: Any, size: int) -> None:
    """SA sync pipeline (filter+sort) latency (full execution)."""
    env = _sa_sync_env(make_users(size))
    filters = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    sorting = [SortSpec(field="email", direction=SortDirection.ASC)]
    result = benchmark(
        env.do_pipeline,
        env.query,
        _DEFAULT_PARAMS,
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="scale-pipeline-sa-async")
@pytest.mark.parametrize("size", _SA_SIZES, ids=_SA_IDS)
def test_sa_async_pipeline_scaling(benchmark: Any, size: int) -> None:
    """SA async pipeline (filter+sort) latency (full execution)."""
    loop, env = _make_loop_and_env(setup_sa_async, make_users(size))
    filters = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    sorting = [SortSpec(field="email", direction=SortDirection.ASC)]
    params = _DEFAULT_PARAMS

    def _do() -> Any:
        return _run_in_loop(
            loop,
            env.do_pipeline(
                env.query,
                params,
                filters=filters,
                sorting=sorting,
            ),
        )

    result = benchmark(_do)
    assert result.total > 0
