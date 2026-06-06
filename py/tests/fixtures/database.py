"""Database session fixtures for the integration / e2e / PostgreSQL lanes.

Three flavours, each seeded with the same deterministic ``make_users(50)`` rows:
a sync in-memory SQLite session, an async in-memory SQLite session (aiosqlite),
and an async PostgreSQL session bound to ``$PYPAGINATE_PG_URL`` (skipped when the
variable is unset). Every fixture creates the schema, seeds, yields, then drops
the schema and disposes the engine so no state leaks between tests.

Registered as a plugin from the root ``conftest`` so the fixtures are available
suite-wide without per-module imports.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from tests.factories.data import make_users
from tests.fixtures.models import Base, User


#: Rows seeded into every database fixture (deterministic, see the factory).
_SEED_ROWS = 50

#: Keeps a single in-memory SQLite connection alive across sessions.
_MEMORY_ARGS: dict[str, object] = {
    "poolclass": StaticPool,
    "connect_args": {"check_same_thread": False},
}


def _seed_sync(session: Session) -> None:
    """Insert the deterministic seed rows into a sync session."""
    session.add_all(User(**row) for row in make_users(_SEED_ROWS))
    session.commit()


async def _seed_async(session: AsyncSession) -> None:
    """Insert the deterministic seed rows into an async session."""
    session.add_all(User(**row) for row in make_users(_SEED_ROWS))
    await session.commit()


@pytest.fixture
def sqlite_engine() -> Iterator[Engine]:
    """A sync in-memory SQLite engine with the schema created."""
    engine = create_engine("sqlite://", **_MEMORY_ARGS)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sqlite_session(sqlite_engine: Engine) -> Iterator[Session]:
    """A sync SQLite session seeded with the deterministic users."""
    with Session(sqlite_engine) as session:
        _seed_sync(session)
        yield session


@pytest.fixture
async def async_sqlite_engine() -> AsyncIterator[AsyncEngine]:
    """An async in-memory SQLite engine (aiosqlite) with the schema created."""
    engine = create_async_engine("sqlite+aiosqlite://", **_MEMORY_ARGS)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_sqlite_session(async_sqlite_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """An async SQLite session seeded with the deterministic users."""
    maker = async_sessionmaker(async_sqlite_engine, expire_on_commit=False)
    async with maker() as session:
        await _seed_async(session)
        yield session


@pytest.fixture
async def postgres_session() -> AsyncIterator[AsyncSession]:
    """An async PostgreSQL session from ``$PYPAGINATE_PG_URL`` (skipped if unset)."""
    url = os.environ.get("PYPAGINATE_PG_URL")
    if not url:
        pytest.skip("PYPAGINATE_PG_URL is not set")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async for session in _pg_session(engine):
        yield session
    await engine.dispose()


async def _pg_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Seed + yield one session, then drop the schema (engine disposed by caller)."""
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        await _seed_async(session)
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
