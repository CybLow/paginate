"""Perf test fixtures -- large datasets and sync memory envs.

Session-scoped datasets avoid regeneration across benchmarks.
The sync helper avoids async overhead for memory-only tests.
"""

from __future__ import annotations

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
from tests.fixtures.backends import BackendEnv


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


# -- Function-scoped backend envs -------------------------------------------


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
