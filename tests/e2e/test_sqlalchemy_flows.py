"""End-to-end flows with real SQLAlchemy + SQLite database.

Each test sets up its own engine, creates tables, seeds data,
and runs pagination through the full stack.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pypaginate import (
    FilterSpec,
    OffsetParams,
    OverflowStrategy,
    SortDirection,
    SortSpec,
    paginate,
)
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline
from tests.fixtures.models import Base, Product, User


async def _create_session(user_count: int) -> AsyncSession:
    """Spin up a fresh in-memory SQLite and seed users."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = factory()
    for i in range(user_count):
        session.add(User(id=i + 1, name=f"User_{i}", email=f"u{i}@test.com"))
    await session.commit()
    return session


async def test_full_workflow_from_scratch() -> None:
    """Create engine, tables, seed, paginate, verify."""
    session = await _create_session(15)
    backend = SQLAlchemyBackend(session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=1, limit=5),
        backend=backend,
    )
    assert page.total == 15
    assert page.page == 1
    assert len(page.items) == 5
    await session.close()


async def test_paginate_through_all_pages() -> None:
    """Walk every page and collect all items."""
    session = await _create_session(23)
    backend = SQLAlchemyBackend(session)
    collected: list[User] = []
    page_num = 1
    while True:
        page = await paginate(
            select(User).order_by(User.id),
            OffsetParams(page=page_num, limit=5),
            backend=backend,
        )
        collected.extend(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert len(collected) == 23
    await session.close()


async def test_filter_sort_paginate_products() -> None:
    """Pipeline: filter by category + sort by price + paginate."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        cats = ("electronics", "books", "clothing")
        for i in range(12):
            session.add(
                Product(
                    id=i + 1,
                    name=f"P_{i}",
                    price=Decimal(str(10 + i * 3)),
                    category=cats[i % 3],
                ),
            )
        await session.commit()
        backend: SQLAlchemyBackend[Product] = SQLAlchemyBackend(session)
        paginator: AsyncPaginator[Product] = AsyncPaginator(backend)
        pipeline: AsyncPipeline[Product] = AsyncPipeline(
            paginator,
            filter_backend=SQLAlchemyFilterBackend(),
            sort_backend=SQLAlchemySortBackend(),
        )
        page = await pipeline.execute(
            select(Product),
            OffsetParams(page=1, limit=10),
            filters=[FilterSpec(field="category", operator="eq", value="electronics")],
            sorting=[SortSpec(field="price", direction=SortDirection.DESC)],
        )
        prices = [p.price for p in page.items]
        assert prices == sorted(prices, reverse=True)
        assert all(p.category == "electronics" for p in page.items)


async def test_overflow_clamp_with_real_data() -> None:
    """Clamp overflow redirects to last page on a real database."""
    session = await _create_session(10)
    backend = SQLAlchemyBackend(session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=100, limit=3),
        backend=backend,
        overflow=OverflowStrategy.CLAMP,
    )
    assert page.page == 4
    assert len(page.items) == 1
    await session.close()


async def test_empty_table_pagination() -> None:
    """Paginating an empty table returns zero items gracefully."""
    session = await _create_session(0)
    backend = SQLAlchemyBackend(session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=1, limit=10),
        backend=backend,
    )
    assert page.total == 0
    assert page.items == []
    assert not page.has_next
    assert not page.has_previous
    await session.close()
