"""PostgreSQL integration tests — optional, skip if no PG available.

Tests pypaginate against a real PostgreSQL database to verify:
- Async pagination with real network I/O
- SA filter/sort/search with PostgreSQL-specific SQL
- Correct behavior with connection pooling

Requires: PostgreSQL running + PYPAGINATE_PG_URL env var set.
Example: PYPAGINATE_PG_URL=postgresql+asyncpg://user:pass@localhost/testdb

Run: uv run pytest tests/integration/test_postgresql.py -v
"""

from __future__ import annotations

import os
from typing import Any

import asyncpg
import pytest


_PG_URL = os.environ.get(
    "PYPAGINATE_PG_URL",
    "postgresql+asyncpg://pypaginate:pypaginate@localhost:5433/pypaginate_test",
)


def _pg_available() -> bool:
    """Check if asyncpg is installed AND PostgreSQL is reachable."""
    import asyncio

    async def _check() -> bool:
        try:
            conn = await asyncpg.connect(_PG_URL.replace("postgresql+asyncpg://", "postgresql://"))
            await conn.close()
        except Exception:
            return False
        else:
            return True

    return asyncio.get_event_loop().run_until_complete(_check())


_PG_AVAILABLE = _pg_available()

_SKIP = pytest.mark.skipif(
    not _PG_AVAILABLE,
    reason="PostgreSQL not available (install asyncpg + run docker-compose.test.yml)",
)

pytestmark = [_SKIP, pytest.mark.postgresql]


@pytest.fixture()
async def pg_engine():
    """Create async PG engine and seed test data."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(_PG_URL, pool_size=5)

    from tests.fixtures.models import Base, User

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(1000)],
        )
        await session.commit()

    yield engine, factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def pg_session(pg_engine: Any) -> Any:
    """Get a fresh PG session."""
    _, factory = pg_engine
    async with factory() as session:
        yield session


class TestPgAsyncPaginate:
    async def test_offset_pagination(self, pg_session: Any) -> None:
        from sqlalchemy import select

        from pypaginate import OffsetParams, paginate
        from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
        from tests.fixtures.models import User

        backend = SQLAlchemyBackend(pg_session)
        query = select(User)
        params = OffsetParams(page=1, limit=20)

        result = await paginate(query, params, backend=backend)

        assert hasattr(result, "total")
        assert result.total == 1000
        assert len(result.items) == 20

    async def test_paginate_page_2(self, pg_session: Any) -> None:
        from sqlalchemy import select

        from pypaginate import OffsetParams, paginate
        from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
        from tests.fixtures.models import User

        backend = SQLAlchemyBackend(pg_session)
        result = await paginate(
            select(User),
            OffsetParams(page=2, limit=20),
            backend=backend,
        )

        assert result.has_previous is True
        assert len(result.items) == 20


class TestPgAsyncFilter:
    async def test_filter_with_starts_with(self, pg_session: Any) -> None:
        from sqlalchemy import select

        from pypaginate import FilterSpec, OffsetParams
        from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
        from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
        from pypaginate.engine.paginator import AsyncPaginator
        from pypaginate.engine.pipeline import AsyncPipeline
        from tests.fixtures.models import User

        backend = SQLAlchemyBackend(pg_session)
        fb = SQLAlchemyFilterBackend()
        paginator = AsyncPaginator(backend)
        pipeline = AsyncPipeline(paginator, filter_backend=fb)

        result = await pipeline.execute(
            select(User),
            OffsetParams(page=1, limit=20),
            filters=[FilterSpec(field="name", operator="starts_with", value="User_5")],
        )

        assert result.total > 0
        for item in result.items:
            assert item.name.startswith("User_5")


class TestPgAsyncSort:
    async def test_sort_by_name_desc(self, pg_session: Any) -> None:
        from sqlalchemy import select

        from pypaginate import OffsetParams, SortDirection, SortSpec
        from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
        from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
        from pypaginate.engine.paginator import AsyncPaginator
        from pypaginate.engine.pipeline import AsyncPipeline
        from tests.fixtures.models import User

        backend = SQLAlchemyBackend(pg_session)
        sb = SQLAlchemySortBackend()
        paginator = AsyncPaginator(backend)
        pipeline = AsyncPipeline(paginator, sort_backend=sb)

        result = await pipeline.execute(
            select(User),
            OffsetParams(page=1, limit=20),
            sorting=[SortSpec(field="name", direction=SortDirection.DESC)],
        )

        names = [item.name for item in result.items]
        assert names == sorted(names, reverse=True)
