"""Cross-backend E2E flows — ONE test, TWO backends.

Full end-to-end pagination flows parametrized over memory and
SQLAlchemy backends with identical seed data.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pypaginate import OffsetParams, SortDirection
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.adapters.sqlalchemy.search import SQLAlchemySearchBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from pypaginate.domain.specs import FilterSpec, SortSpec
from pypaginate.engine.paginator import AsyncPaginator, Paginator
from pypaginate.engine.pipeline import AsyncPipeline, SyncPipeline
from tests.fixtures.models import Base, User


# -- Seed data (same for both backends) -------------------------------------

_USERS: list[dict[str, Any]] = [
    {"id": 1, "name": "Alice", "email": "alice@test.com"},
    {"id": 2, "name": "Bob", "email": "bob@test.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@test.com"},
    {"id": 4, "name": "Diana", "email": "diana@test.com"},
    {"id": 5, "name": "Eve", "email": "eve@test.com"},
    {"id": 6, "name": "Frank", "email": "frank@test.com"},
    {"id": 7, "name": "Grace", "email": "grace@test.com"},
    {"id": 8, "name": "Hank", "email": "hank@test.com"},
]

_TOTAL = len(_USERS)


# -- Fixture -----------------------------------------------------------------


@pytest.fixture(params=["memory", "sqlalchemy"])
async def e2e_env(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[dict[str, Any], None]:
    """Yield full pipeline env for each backend."""
    if request.param == "memory":
        yield _build_memory_env()
    else:
        async for env in _build_sqlalchemy_env():
            yield env


def _build_memory_env() -> dict[str, Any]:
    """Build memory backend env."""
    return {
        "mode": "sync",
        "pipeline": SyncPipeline(
            Paginator(MemoryBackend()),
            filter_backend=MemoryFilterBackend(),
            sort_backend=MemorySortBackend(),
            search_backend=MemorySearchBackend(),
        ),
        "query": list(_USERS),
        "total": _TOTAL,
    }


async def _build_sqlalchemy_env() -> AsyncGenerator[dict[str, Any], None]:
    """Build SQLAlchemy backend env with seeded database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add_all([User(**u) for u in _USERS])
        await session.commit()
    async with factory() as session:
        backend = SQLAlchemyBackend(session)
        yield {
            "mode": "async",
            "pipeline": AsyncPipeline(
                AsyncPaginator(backend),
                filter_backend=SQLAlchemyFilterBackend(),
                sort_backend=SQLAlchemySortBackend(),
                search_backend=SQLAlchemySearchBackend(),
            ),
            "query": select(User).order_by(User.id),
            "total": _TOTAL,
        }
    await engine.dispose()


# -- Helpers -----------------------------------------------------------------


async def _execute(env: dict, params: OffsetParams, **kwargs: Any) -> Any:
    """Execute pipeline on either sync or async path."""
    if env["mode"] == "sync":
        return env["pipeline"].execute(env["query"], params, **kwargs)
    return await env["pipeline"].execute(env["query"], params, **kwargs)


def _get_name(item: Any) -> str:
    """Extract name from dict or ORM model."""
    if isinstance(item, dict):
        return str(item["name"])
    return str(item.name)


# -- E2E flow tests ----------------------------------------------------------


class TestPaginateFirstPage:
    """First page returns correct items on both backends."""

    async def test_first_page(self, e2e_env: dict) -> None:
        """Page 1 limit 3 yields 3 items with total=8."""
        page = await _execute(e2e_env, OffsetParams(page=1, limit=3))

        assert page.total == _TOTAL
        assert len(page.items) == 3
        assert page.has_next is True


class TestPaginateAllPagesCompleteness:
    """Collecting all pages yields exactly N items."""

    async def test_all_pages(self, e2e_env: dict) -> None:
        """Iterate all pages, collect all items."""
        collected: list[Any] = []
        page_num = 1

        while True:
            page = await _execute(e2e_env, OffsetParams(page=page_num, limit=3))
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        assert len(collected) == _TOTAL


class TestFilterAndPaginate:
    """Filter + paginate on both backends."""

    async def test_filter_and_paginate(self, e2e_env: dict) -> None:
        """Filter id >= 5 then paginate returns 4 items total."""
        filters = [FilterSpec(field="id", operator="gte", value=5)]

        page = await _execute(e2e_env, OffsetParams(page=1, limit=10), filters=filters)

        assert page.total == 4


class TestSortAndPaginate:
    """Sort + paginate preserves order on both backends."""

    async def test_sort_name_asc(self, e2e_env: dict) -> None:
        """Sort by name ASC yields alphabetical order."""
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]

        page = await _execute(e2e_env, OffsetParams(page=1, limit=10), sorting=sorting)
        names = [_get_name(item) for item in page.items]

        assert names == sorted(names)


class TestCombinedFilterSortPaginate:
    """Filter + sort + paginate combined on both backends."""

    async def test_combined(self, e2e_env: dict) -> None:
        """Filter id >= 3 + sort name ASC + paginate page 1."""
        filters = [FilterSpec(field="id", operator="gte", value=3)]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]

        page = await _execute(
            e2e_env,
            OffsetParams(page=1, limit=10),
            filters=filters,
            sorting=sorting,
        )
        names = [_get_name(item) for item in page.items]

        assert page.total == 6
        assert names == sorted(names)
