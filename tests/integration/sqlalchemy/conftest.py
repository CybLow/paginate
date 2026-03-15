"""SQLAlchemy integration test fixtures.

Provides seeded database sessions for testing against real SQLite.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from tests.fixtures.models import Base, Product, User


_CATEGORIES = ("electronics", "books", "clothing")


@pytest.fixture()
async def async_engine() -> AsyncEngine:
    """Create an async SQLite engine per test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine  # type: ignore[misc]
    await engine.dispose()


@pytest.fixture()
async def seeded_session(async_engine: AsyncEngine) -> AsyncSession:
    """Session with 20 users and 10 products seeded."""
    factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        for i in range(20):
            session.add(
                User(
                    id=i + 1,
                    name=f"User_{i}",
                    email=f"user{i}@test.com",
                ),
            )
        for i in range(10):
            session.add(
                Product(
                    id=i + 1,
                    name=f"Product_{i}",
                    price=Decimal(str(10 + i * 5)),
                    category=_CATEGORIES[i % 3],
                    in_stock=i % 3 != 0,
                ),
            )
        await session.commit()
        yield session  # type: ignore[misc]
