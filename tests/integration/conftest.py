"""Integration test configuration with cross-backend fixtures.

Provides parametrized fixtures that yield both memory and SQLAlchemy
backends seeded with identical data, enabling ONE test, TWO backends.
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

from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.adapters.sqlalchemy.search import SQLAlchemySearchBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from tests.fixtures.models import Base, User


pytestmark = pytest.mark.integration

# -- Shared seed data (identical for both backends) --------------------------

SEED_USERS: list[dict[str, Any]] = [
    {"id": 1, "name": "Alice", "email": "alice@test.com"},
    {"id": 2, "name": "Bob", "email": "bob@test.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@test.com"},
    {"id": 4, "name": "Diana", "email": "diana@test.com"},
    {"id": 5, "name": "Eve", "email": "eve@test.com"},
    {"id": 6, "name": "Frank", "email": "frank@test.com"},
    {"id": 7, "name": "Grace", "email": "grace@test.com"},
    {"id": 8, "name": "Hank", "email": "hank@test.com"},
]

TOTAL_USERS = len(SEED_USERS)


# -- SQLAlchemy session helper -----------------------------------------------


async def _seeded_session() -> tuple[async_sessionmaker[AsyncSession], Any]:
    """Create an in-memory SQLite, seed users, return factory + engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add_all([User(**u) for u in SEED_USERS])
        await session.commit()
    return factory, engine


# -- Cross-backend pagination env -------------------------------------------


@pytest.fixture(params=["memory", "sqlalchemy"])
async def pagination_env(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[tuple[str, Any, Any, int], None]:
    """Yield (mode, pagination_backend, query, total)."""
    if request.param == "memory":
        yield ("sync", MemoryBackend(), list(SEED_USERS), TOTAL_USERS)
    else:
        factory, engine = await _seeded_session()
        async with factory() as session:
            yield ("async", SQLAlchemyBackend(session), select(User).order_by(User.id), TOTAL_USERS)
        await engine.dispose()


# -- Cross-backend full env (pagination + filter + sort + search) -----------


@pytest.fixture(params=["memory", "sqlalchemy"])
async def full_env(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[dict[str, Any], None]:
    """Yield a dict with mode, all backends, query, and total."""
    if request.param == "memory":
        yield {
            "mode": "sync",
            "pagination": MemoryBackend(),
            "filter": MemoryFilterBackend(),
            "sort": MemorySortBackend(),
            "search": MemorySearchBackend(),
            "query": list(SEED_USERS),
            "total": TOTAL_USERS,
        }
    else:
        factory, engine = await _seeded_session()
        async with factory() as session:
            yield {
                "mode": "async",
                "pagination": SQLAlchemyBackend(session),
                "filter": SQLAlchemyFilterBackend(),
                "sort": SQLAlchemySortBackend(),
                "search": SQLAlchemySearchBackend(),
                "query": select(User),
                "total": TOTAL_USERS,
            }
        await engine.dispose()
