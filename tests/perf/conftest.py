"""Perf test fixtures -- large datasets and backend envs.

Session-scoped datasets avoid regeneration across benchmarks.
Provides memory, SA sync, and SA async envs at various sizes.
"""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from typing import Any

import pytest

from pypaginate._dispatch import paginate
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline
from tests.factories.data import make_users
from tests.fixtures.backends import (
    BackendEnv,
    setup_sa_async,
    setup_sa_sync,
)


# -- Async helpers for benchmarks -------------------------------------------


def _make_loop_and_env(
    setup_fn: Any,
    data: list[dict[str, Any]],
) -> tuple[asyncio.AbstractEventLoop, BackendEnv]:
    """Create an event loop and set up a backend env inside it."""
    loop = asyncio.new_event_loop()
    env = loop.run_until_complete(setup_fn(data))
    return loop, env


def _run_in_loop(
    loop: asyncio.AbstractEventLoop,
    coro: Any,
) -> Any:
    """Run a coroutine in an existing event loop."""
    return loop.run_until_complete(coro)


# -- Memory sync setup (no async overhead) ----------------------------------


def _setup_memory_sync(data: list[dict[str, Any]]) -> BackendEnv:
    """Build a memory BackendEnv synchronously (no async)."""
    backend = MemoryBackend()
    fb = MemoryFilterBackend()
    sb = MemorySortBackend()
    srch = MemorySearchBackend()
    paginator: Paginator[Any] = Paginator(backend)
    pipeline: SyncPipeline[Any] = SyncPipeline(
        paginator,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
    )
    return BackendEnv(
        name="memory",
        mode="sync",
        pagination_backend=backend,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
        query=data,
        total=len(data),
        field_names=("id", "name", "age", "email", "active"),
        get_field=lambda item, f: item[f],
        do_paginate=lambda q, p, **kw: paginate(q, p, **kw),
        do_filter=lambda q, specs: fb.apply_filters(q, specs),
        do_sort=lambda q, specs: sb.apply_sorting(q, specs),
        do_search=lambda q, spec: srch.apply_search(q, spec),
        do_pipeline=lambda q, p, **kw: pipeline.execute(q, p, **kw),
    )


# -- SA sync setup (sync wrapper) -------------------------------------------


def _setup_sa_sync_for_bench(
    data: list[dict[str, Any]],
) -> BackendEnv:
    """Create SA sync env synchronously for benchmarks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(setup_sa_sync(data))
    finally:
        loop.close()


# -- SA async setup (preserves event loop) ----------------------------------


def _setup_sa_async_with_loop(
    data: list[dict[str, Any]],
) -> tuple[asyncio.AbstractEventLoop, BackendEnv]:
    """Create SA async env with its event loop for benchmarks."""
    return _make_loop_and_env(setup_sa_async, data)


# -- Session-scoped datasets (generated once) --------------------------------


@pytest.fixture(scope="session")
def dataset_1k() -> list[dict[str, Any]]:
    """1K user dicts for lightweight benchmarks."""
    return make_users(1_000)


@pytest.fixture(scope="session")
def dataset_10k() -> list[dict[str, Any]]:
    """10K user dicts for medium benchmarks."""
    return make_users(10_000)


@pytest.fixture(scope="session")
def dataset_100k() -> list[dict[str, Any]]:
    """100K user dicts for stress tests."""
    return make_users(100_000)


@pytest.fixture(scope="session")
def dataset_500k() -> list[dict[str, Any]]:
    """500K user dicts for heavy benchmarks."""
    return make_users(500_000)


@pytest.fixture(scope="session")
def dataset_1m() -> list[dict[str, Any]]:
    """1M user dicts for extreme scaling tests."""
    return make_users(1_000_000)


# -- Function-scoped memory envs -------------------------------------------


@pytest.fixture()
def memory_env_1k(dataset_1k: list[dict[str, Any]]) -> BackendEnv:
    """Memory backend with 1K items."""
    return _setup_memory_sync(dataset_1k)


@pytest.fixture()
def memory_env_10k(dataset_10k: list[dict[str, Any]]) -> BackendEnv:
    """Memory backend with 10K items."""
    return _setup_memory_sync(dataset_10k)


@pytest.fixture()
def memory_env_100k(dataset_100k: list[dict[str, Any]]) -> BackendEnv:
    """Memory backend with 100K items."""
    return _setup_memory_sync(dataset_100k)


@pytest.fixture()
def memory_env_500k(dataset_500k: list[dict[str, Any]]) -> BackendEnv:
    """Memory backend with 500K items."""
    return _setup_memory_sync(dataset_500k)


@pytest.fixture()
def memory_env_1m(dataset_1m: list[dict[str, Any]]) -> BackendEnv:
    """Memory backend with 1M items."""
    return _setup_memory_sync(dataset_1m)


# -- Session-scoped SA sync envs -------------------------------------------


@pytest.fixture(scope="session")
def sa_sync_env_1k(
    dataset_1k: list[dict[str, Any]],
) -> Generator[BackendEnv, None, None]:
    """SA sync backend with 1K items."""
    env = _setup_sa_sync_for_bench(dataset_1k)
    yield env
    if env.cleanup:
        asyncio.run(env.cleanup())


@pytest.fixture(scope="session")
def sa_sync_env_10k(
    dataset_10k: list[dict[str, Any]],
) -> Generator[BackendEnv, None, None]:
    """SA sync backend with 10K items."""
    env = _setup_sa_sync_for_bench(dataset_10k)
    yield env
    if env.cleanup:
        asyncio.run(env.cleanup())


# -- Session-scoped SA async envs (with event loops) -----------------------


@pytest.fixture(scope="session")
def _sa_async_loop_env_1k(
    dataset_1k: list[dict[str, Any]],
) -> Generator[tuple[asyncio.AbstractEventLoop, BackendEnv], None, None]:
    """SA async loop+env with 1K items (internal)."""
    loop, env = _setup_sa_async_with_loop(dataset_1k)
    yield loop, env
    if env.cleanup:
        loop.run_until_complete(env.cleanup())
    loop.close()


@pytest.fixture(scope="session")
def _sa_async_loop_env_10k(
    dataset_10k: list[dict[str, Any]],
) -> Generator[tuple[asyncio.AbstractEventLoop, BackendEnv], None, None]:
    """SA async loop+env with 10K items (internal)."""
    loop, env = _setup_sa_async_with_loop(dataset_10k)
    yield loop, env
    if env.cleanup:
        loop.run_until_complete(env.cleanup())
    loop.close()


@pytest.fixture(scope="session")
def sa_async_env_1k(
    _sa_async_loop_env_1k: tuple[asyncio.AbstractEventLoop, BackendEnv],
) -> BackendEnv:
    """SA async backend with 1K items."""
    return _sa_async_loop_env_1k[1]


@pytest.fixture(scope="session")
def sa_async_loop_1k(
    _sa_async_loop_env_1k: tuple[asyncio.AbstractEventLoop, BackendEnv],
) -> asyncio.AbstractEventLoop:
    """Event loop for SA async 1K env."""
    return _sa_async_loop_env_1k[0]


@pytest.fixture(scope="session")
def sa_async_env_10k(
    _sa_async_loop_env_10k: tuple[asyncio.AbstractEventLoop, BackendEnv],
) -> BackendEnv:
    """SA async backend with 10K items."""
    return _sa_async_loop_env_10k[1]


@pytest.fixture(scope="session")
def sa_async_loop_10k(
    _sa_async_loop_env_10k: tuple[asyncio.AbstractEventLoop, BackendEnv],
) -> asyncio.AbstractEventLoop:
    """Event loop for SA async 10K env."""
    return _sa_async_loop_env_10k[0]
