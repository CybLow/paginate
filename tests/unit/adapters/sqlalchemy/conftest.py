"""Shared fixtures for SQLAlchemy adapter unit tests.

Provides async and sync SQLite engines, empty sessions, and seeded
sessions with 10 users and 8 products for real database tests.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session

from tests.fixtures.models import Base, Product, User


# -- Async fixtures ----------------------------------------------------------


@pytest.fixture()
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """In-memory async SQLite engine with tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Empty async session (no seed data)."""
    factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as sess:
        yield sess


@pytest.fixture()
async def seeded_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Session with 10 users and 8 products from test data."""
    factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as sess:
        sess.add_all(_make_users())
        sess.add_all(_make_products())
        await sess.commit()
        yield sess


# -- Sync fixtures -----------------------------------------------------------


@pytest.fixture()
def sync_engine() -> Generator[object, None, None]:
    """In-memory sync SQLite engine with tables created."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def sync_session(sync_engine: object) -> Generator[Session, None, None]:
    """Empty sync session (no seed data)."""
    with Session(sync_engine) as sess:  # type: ignore[arg-type]
        yield sess


@pytest.fixture()
def sync_seeded_session(
    sync_engine: object,
) -> Generator[Session, None, None]:
    """Sync session with 10 users and 8 products."""
    with Session(sync_engine) as sess:  # type: ignore[arg-type]
        sess.add_all(_make_users())
        sess.add_all(_make_products())
        sess.commit()
        yield sess


# -- Helpers -----------------------------------------------------------------


def _make_users() -> list[User]:
    """Create 10 users matching TEST_USERS_DATA."""
    from tests.fixtures.data import TEST_USERS_DATA

    return [User(id=i + 1, **data) for i, data in enumerate(TEST_USERS_DATA)]


def _make_products() -> list[Product]:
    """Create 8 products matching TEST_PRODUCTS_DATA."""
    from tests.fixtures.data import TEST_PRODUCTS_DATA

    return [
        Product(id=i + 1, **data, description=None) for i, data in enumerate(TEST_PRODUCTS_DATA)
    ]
