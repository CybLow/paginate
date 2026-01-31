"""Root pytest configuration with shared fixtures and hooks.

This module provides:
- Pytest configuration hooks
- Shared fixtures available to all tests
- Custom command line options
- Test collection modifiers
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.nodes import Item
    from sqlalchemy.ext.asyncio import AsyncEngine


# ============================================
# Backward compatibility: Models from old conftest
# These are re-exported for existing tests
# ============================================


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class User(Base):
    """Sample user model for integration tests."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


# Sample test data (backward compatibility)
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


# ============================================
# Pytest Hooks
# ============================================


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options.

    Options:
        --run-slow: Run tests marked as slow
        --run-benchmark: Run benchmark tests
        --run-mutation: Run mutation tests
    """
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests (marked with @pytest.mark.slow)",
    )
    parser.addoption(
        "--run-benchmark",
        action="store_true",
        default=False,
        help="Run benchmark tests (marked with @pytest.mark.benchmark)",
    )


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom settings."""
    # Register custom markers (already in pyproject.toml, but good for IDE support)
    config.addinivalue_line("markers", "focus: Mark test to run in isolation during development")


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Modify test collection based on markers and options.

    - Skips slow tests unless --run-slow is provided
    - Skips benchmark tests unless --run-benchmark is provided
    - Auto-applies markers based on test location
    """
    # Handle slow tests
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="use --run-slow to run slow tests")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    # Handle benchmark tests
    run_benchmark = config.getoption("--run-benchmark", default=False)
    # Also check if pytest-benchmark is enabling benchmarks
    benchmark_enabled = config.getoption("--benchmark-enable", default=False) if hasattr(config.option, "benchmark_enable") else False

    if not run_benchmark and not benchmark_enabled:
        skip_benchmark = pytest.mark.skip(reason="use --run-benchmark or --benchmark-enable to run benchmarks")
        for item in items:
            if "benchmark" in item.keywords:
                item.add_marker(skip_benchmark)

    # Auto-apply markers based on test location
    for item in items:
        # Add unit marker to tests in tests/unit/
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in tests/integration/
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add e2e marker to tests in tests/e2e/
        elif "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        # Add property marker to tests in tests/property/
        elif "/property/" in str(item.fspath):
            item.add_marker(pytest.mark.property)
        # Add benchmark marker to tests in tests/benchmarks/
        elif "/benchmarks/" in str(item.fspath):
            item.add_marker(pytest.mark.benchmark)


# ============================================
# Database Fixtures
# ============================================


@pytest.fixture(scope="function")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an async SQLite engine for testing.

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

    Populates the database with 10 sample users (Alice through Jack).

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
        for user_data in TEST_USERS:
            session.add(User(**user_data))
        await session.commit()
        yield session


@pytest.fixture
def user_query():
    """Return a base query for User ordered by id.

    Returns:
        A SQLAlchemy select statement for User.
    """
    return select(User).order_by(User.id)


# ============================================
# Snapshot Testing Fixtures
# ============================================


@pytest.fixture
def snapshot_json(snapshot):
    """JSON snapshot fixture for syrupy.

    Use this for testing JSON-serializable data structures.

    Args:
        snapshot: The syrupy snapshot fixture.

    Returns:
        A snapshot configured for JSON comparison.
    """
    try:
        from syrupy.extensions.json import JSONSnapshotExtension
        return snapshot.use_extension(JSONSnapshotExtension)
    except ImportError:
        pytest.skip("syrupy not installed")


# ============================================
# Utility Fixtures
# ============================================


@pytest.fixture
def sample_items() -> list[dict[str, int | str]]:
    """Provide a sample list of items for testing.

    Returns:
        A list of 20 sample items with id, name, and category.
    """
    return [
        {"id": i, "name": f"Item {i}", "category": "A" if i % 2 == 0 else "B"}
        for i in range(1, 21)
    ]


@pytest.fixture
def large_dataset() -> list[int]:
    """Provide a large dataset for performance testing.

    Returns:
        A list of 100,000 integers.
    """
    return list(range(100_000))


# ============================================
# Exports for backward compatibility
# ============================================

__all__ = [
    # Models
    "Base",
    "User",
    "TEST_USERS",
    # Fixtures
    "async_engine",
    "async_session",
    "populated_session",
    "user_query",
    "sample_items",
    "large_dataset",
    "snapshot_json",
]
