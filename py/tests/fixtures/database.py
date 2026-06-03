"""Database fixtures for integration tests.

This module provides async SQLAlchemy fixtures for database testing.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tests.fixtures.data import create_test_users
from tests.fixtures.models import Base


if TYPE_CHECKING:
    pass


@pytest.fixture(scope="function")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an async SQLite engine per test.

    This fixture creates an in-memory SQLite database with all tables
    from the Base metadata. The engine is disposed after the test.

    Yields:
        AsyncEngine: An async SQLAlchemy engine.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create an async session for testing.

    This fixture creates a session from the async_engine fixture.
    The session is rolled back after the test to ensure isolation.

    Args:
        async_engine: The async engine fixture.

    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def populated_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a session with pre-populated test data.

    This fixture creates a session and populates it with sample
    user data from the data module.

    Args:
        async_engine: The async engine fixture.

    Yields:
        AsyncSession: A session with pre-populated test data.
    """
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        users = create_test_users()
        session.add_all(users)
        await session.commit()
        yield session


__all__ = [
    "async_engine",
    "async_session",
    "populated_session",
]
