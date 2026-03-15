"""Boundary-value perf tests.

Exercises edge-case limits and page values
across all 3 backends at moderate scale.
"""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from typing import Any

import pytest

from pypaginate._dispatch import paginate
from pypaginate.domain.enums import OverflowStrategy
from pypaginate.domain.models import OffsetParams
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import (
    _run_in_loop,
    _setup_memory_sync,
    _setup_sa_async_with_loop,
    _setup_sa_sync_for_bench,
)


# ── Memory boundary tests ─────────────────────────────────


@pytest.fixture()
def mem_env_1k(dataset_1k: list[dict[str, Any]]) -> BackendEnv:
    """Memory env with 1K items."""
    return _setup_memory_sync(dataset_1k)


@pytest.mark.parametrize("limit", [1, 20, 100, 1000])
def test_memory_boundary_limit(
    mem_env_1k: BackendEnv,
    limit: int,
) -> None:
    """Memory: various limits produce correct page sizes."""
    page = mem_env_1k.do_paginate(mem_env_1k.query, OffsetParams(page=1, limit=limit))
    assert len(page.items) == min(limit, 1_000)
    assert page.total == 1_000


def test_memory_limit_1_single_item(mem_env_1k: BackendEnv) -> None:
    """Memory: limit=1 yields exactly 1 item per page."""
    page = mem_env_1k.do_paginate(mem_env_1k.query, OffsetParams(page=1, limit=1))
    assert len(page.items) == 1
    assert page.has_next is True


def test_memory_exact_fit(mem_env_1k: BackendEnv) -> None:
    """Memory: N items with limit=N yields exactly 1 page."""
    page = mem_env_1k.do_paginate(mem_env_1k.query, OffsetParams(page=1, limit=1000))
    assert len(page.items) == 1_000
    assert page.has_next is False
    assert page.pages == 1


def test_memory_empty_dataset() -> None:
    """Memory: 0 items yields empty page with total=0."""
    env = _setup_memory_sync([])
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=20))
    assert page.total == 0
    assert len(page.items) == 0
    assert page.has_next is False


def test_memory_overflow_empty(mem_env_1k: BackendEnv) -> None:
    """Memory: page beyond range with EMPTY yields no items."""
    page = paginate(
        mem_env_1k.query,
        OffsetParams(page=999, limit=20),
        overflow=OverflowStrategy.EMPTY,
    )
    assert len(page.items) == 0
    assert page.total == 1_000


def test_memory_overflow_clamp(mem_env_1k: BackendEnv) -> None:
    """Memory: page beyond range with CLAMP yields last page."""
    page = paginate(
        mem_env_1k.query,
        OffsetParams(page=999, limit=20),
        overflow=OverflowStrategy.CLAMP,
    )
    assert len(page.items) > 0
    assert page.total == 1_000


# ── SA sync boundary tests ────────────────────────────────


@pytest.fixture()
def sa_sync_env_boundary(
    dataset_1k: list[dict[str, Any]],
) -> BackendEnv:
    """SA sync env with 1K items for boundary tests."""
    return _setup_sa_sync_for_bench(dataset_1k)


@pytest.mark.parametrize("limit", [1, 20, 100, 1000])
def test_sa_sync_boundary_limit(
    sa_sync_env_boundary: BackendEnv,
    limit: int,
) -> None:
    """SA sync: various limits produce correct page sizes."""
    env = sa_sync_env_boundary
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=limit))
    assert len(page.items) == min(limit, 1_000)
    assert page.total == 1_000


def test_sa_sync_limit_1(sa_sync_env_boundary: BackendEnv) -> None:
    """SA sync: limit=1 yields exactly 1 item."""
    env = sa_sync_env_boundary
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=1))
    assert len(page.items) == 1
    assert page.has_next is True


def test_sa_sync_exact_fit(sa_sync_env_boundary: BackendEnv) -> None:
    """SA sync: N items with limit=N yields 1 page."""
    env = sa_sync_env_boundary
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=1000))
    assert len(page.items) == 1_000
    assert page.has_next is False


# ── SA async boundary tests ───────────────────────────────


@pytest.fixture()
def sa_async_boundary(
    dataset_1k: list[dict[str, Any]],
) -> Generator[tuple[asyncio.AbstractEventLoop, BackendEnv], None, None]:
    """SA async loop+env with 1K items for boundary tests."""
    loop, env = _setup_sa_async_with_loop(dataset_1k)
    yield loop, env
    if env.cleanup:
        loop.run_until_complete(env.cleanup())
    loop.close()


@pytest.mark.parametrize("limit", [1, 20, 100, 1000])
def test_sa_async_boundary_limit(
    sa_async_boundary: tuple[asyncio.AbstractEventLoop, BackendEnv],
    limit: int,
) -> None:
    """SA async: various limits produce correct page sizes."""
    loop, env = sa_async_boundary
    coro = env.do_paginate(env.query, OffsetParams(page=1, limit=limit))
    page = _run_in_loop(loop, coro)
    assert len(page.items) == min(limit, 1_000)
    assert page.total == 1_000


def test_sa_async_limit_1(
    sa_async_boundary: tuple[asyncio.AbstractEventLoop, BackendEnv],
) -> None:
    """SA async: limit=1 yields exactly 1 item."""
    loop, env = sa_async_boundary
    coro = env.do_paginate(env.query, OffsetParams(page=1, limit=1))
    page = _run_in_loop(loop, coro)
    assert len(page.items) == 1
    assert page.has_next is True


def test_sa_async_exact_fit(
    sa_async_boundary: tuple[asyncio.AbstractEventLoop, BackendEnv],
) -> None:
    """SA async: N items with limit=N yields 1 page."""
    loop, env = sa_async_boundary
    coro = env.do_paginate(env.query, OffsetParams(page=1, limit=1000))
    page = _run_in_loop(loop, coro)
    assert len(page.items) == 1_000
    assert page.has_next is False
