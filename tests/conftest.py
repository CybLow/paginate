"""Pytest configuration and shared fixtures for pypaginator tests.

This module provides async SQLAlchemy fixtures for integration testing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, AsyncGenerator

import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class User(Base):
    """Sample user model for integration tests."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


# Sample test data
TEST_USERS = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "David", "email": "david@example.com"},
    {"name": "Eve", "email": "eve@example.com"},
    {"name": "Frank", "email": "frank@example.com"},
    {"name": "Grace", "email": "grace@example.com"},
    {"name": "Henry", "email": "henry@example.com"},
    {"name": "Ivy", "email": "ivy@example.com"},
    {"name": "Jack", "email": "jack@example.com"},
]


@pytest.fixture
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an async SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create an async session for testing."""
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def populated_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a session with pre-populated test data."""
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        # Insert test users
        for user_data in TEST_USERS:
            session.add(User(**user_data))
        await session.commit()
        yield session


@pytest.fixture
def user_query():
    """Return a base query for User ordered by id."""
    return select(User).order_by(User.id)


__all__ = [
    "Base",
    "User",
    "TEST_USERS",
    "async_engine",
    "async_session",
    "populated_session",
    "user_query",
]
