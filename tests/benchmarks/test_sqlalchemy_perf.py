"""Benchmark tests for SQLAlchemy pagination operations.

Uses a session-scoped engine with 1000 pre-seeded users
to avoid per-test setup overhead.
"""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pypaginate import FilterSpec, OffsetParams, SortDirection, SortSpec
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline
from tests.fixtures.models import Base, User


pytestmark = pytest.mark.benchmark


@pytest.fixture(scope="function")
async def bench_session() -> AsyncSession:
    """Module-scoped session with 1000 seeded users."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        for i in range(1000):
            session.add(User(id=i + 1, name=f"User_{i:04d}", email=f"u{i}@bench.com"))
        await session.commit()
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.benchmark(group="sqlalchemy")
def test_count_1000_rows(benchmark: Any, bench_session: AsyncSession) -> None:
    """Benchmark counting 1000 rows."""
    import asyncio

    backend = SQLAlchemyBackend(bench_session)

    async def _count() -> int:
        return await backend.count(select(User))

    result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(_count()))
    assert result == 1000


@pytest.mark.benchmark(group="sqlalchemy")
def test_fetch_page_1000_rows(benchmark: Any, bench_session: AsyncSession) -> None:
    """Benchmark fetching a page from 1000 rows."""
    import asyncio

    backend = SQLAlchemyBackend(bench_session)

    async def _fetch() -> list[User]:
        return await backend.fetch(select(User).order_by(User.id), offset=500, limit=20)

    result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(_fetch()))
    assert len(result) == 20


@pytest.mark.benchmark(group="sqlalchemy")
def test_filter_paginate_1000_rows(benchmark: Any, bench_session: AsyncSession) -> None:
    """Benchmark filter + paginate on 1000 rows."""
    import asyncio

    fb = SQLAlchemyFilterBackend()
    backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(bench_session)
    paginator: AsyncPaginator[User] = AsyncPaginator(backend)
    pipeline: AsyncPipeline[User] = AsyncPipeline(paginator, filter_backend=fb)

    async def _run() -> Any:
        return await pipeline.execute(
            select(User),
            OffsetParams(page=1, limit=20),
            filters=[FilterSpec(field="name", operator="contains", value="User_00")],
        )

    result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(_run()))
    assert len(result.items) > 0


@pytest.mark.benchmark(group="sqlalchemy")
def test_sort_paginate_1000_rows(benchmark: Any, bench_session: AsyncSession) -> None:
    """Benchmark sort + paginate on 1000 rows."""
    import asyncio

    sb = SQLAlchemySortBackend()
    backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(bench_session)
    paginator: AsyncPaginator[User] = AsyncPaginator(backend)
    pipeline: AsyncPipeline[User] = AsyncPipeline(paginator, sort_backend=sb)

    async def _run() -> Any:
        return await pipeline.execute(
            select(User),
            OffsetParams(page=25, limit=20),
            sorting=[SortSpec(field="name", direction=SortDirection.DESC)],
        )

    result = benchmark(lambda: asyncio.get_event_loop().run_until_complete(_run()))
    assert len(result.items) == 20
