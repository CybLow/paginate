"""Integration tests for SQLAlchemy filter backend with real SQLite.

Validates SQLAlchemyFilterBackend against actual database rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from pypaginate import FilterSpec, OffsetParams, paginate
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from tests.fixtures.models import Product, User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_filter_eq_single_match(seeded_session: AsyncSession) -> None:
    """Equality filter returns exactly one user."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(User),
        [FilterSpec(field="name", operator="eq", value="User_5")],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=10)
    assert len(items) == 1
    assert items[0].name == "User_5"


async def test_filter_by_category(seeded_session: AsyncSession) -> None:
    """Category filter returns products in that category."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(Product),
        [FilterSpec(field="category", operator="eq", value="electronics")],
    )
    backend = SQLAlchemyBackend(seeded_session)
    count = await backend.count(stmt)
    assert count == 4


async def test_filter_gte_price(seeded_session: AsyncSession) -> None:
    """Price >= 30 filters low-priced products out."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(Product),
        [FilterSpec(field="price", operator="gte", value=30)],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt.order_by(Product.price), offset=0, limit=20)
    assert all(p.price >= 30 for p in items)


async def test_filter_multiple_and(seeded_session: AsyncSession) -> None:
    """Multiple AND filters narrow results correctly."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(Product),
        [
            FilterSpec(field="category", operator="eq", value="electronics"),
            FilterSpec(field="in_stock", operator="eq", value=True),
        ],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=20)
    assert all(p.category == "electronics" and p.in_stock for p in items)


async def test_filter_no_match_returns_empty(seeded_session: AsyncSession) -> None:
    """Filter with impossible condition yields no rows."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(User),
        [FilterSpec(field="name", operator="eq", value="NONEXISTENT")],
    )
    backend = SQLAlchemyBackend(seeded_session)
    count = await backend.count(stmt)
    assert count == 0


async def test_filter_contains(seeded_session: AsyncSession) -> None:
    """CONTAINS filter matches substring in name."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(User),
        [FilterSpec(field="name", operator="contains", value="User_1")],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=30)
    assert all("User_1" in u.name for u in items)
    assert len(items) >= 2  # User_1, User_10..User_19


async def test_filter_plus_paginate(seeded_session: AsyncSession) -> None:
    """Filter then paginate returns correct subset."""
    fb = SQLAlchemyFilterBackend()
    stmt = fb.apply_filters(
        select(Product).order_by(Product.id),
        [FilterSpec(field="category", operator="eq", value="books")],
    )
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(stmt, OffsetParams(page=1, limit=2), backend=backend)
    assert page.total == 3
    assert len(page.items) == 2
    assert all(p.category == "books" for p in page.items)
