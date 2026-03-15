"""Integration tests for SQLAlchemy sort backend with real SQLite.

Validates SQLAlchemySortBackend ordering against actual database rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from pypaginate import OffsetParams, SortDirection, SortSpec, paginate
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from tests.fixtures.models import Product, User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_sort_asc_by_name(seeded_session: AsyncSession) -> None:
    """ASC sort returns users in alphabetical order."""
    sb = SQLAlchemySortBackend()
    stmt = sb.apply_sorting(
        select(User),
        [SortSpec(field="name", direction=SortDirection.ASC)],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=20)
    names = [u.name for u in items]
    assert names == sorted(names)


async def test_sort_desc_by_name(seeded_session: AsyncSession) -> None:
    """DESC sort reverses alphabetical order."""
    sb = SQLAlchemySortBackend()
    stmt = sb.apply_sorting(
        select(User),
        [SortSpec(field="name", direction=SortDirection.DESC)],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=20)
    names = [u.name for u in items]
    assert names == sorted(names, reverse=True)


async def test_sort_asc_by_price(seeded_session: AsyncSession) -> None:
    """Products sorted by price ASC are non-decreasing."""
    sb = SQLAlchemySortBackend()
    stmt = sb.apply_sorting(
        select(Product),
        [SortSpec(field="price", direction=SortDirection.ASC)],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=20)
    prices = [p.price for p in items]
    assert prices == sorted(prices)


async def test_sort_desc_by_price(seeded_session: AsyncSession) -> None:
    """Products sorted by price DESC are non-increasing."""
    sb = SQLAlchemySortBackend()
    stmt = sb.apply_sorting(
        select(Product),
        [SortSpec(field="price", direction=SortDirection.DESC)],
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=20)
    prices = [p.price for p in items]
    assert prices == sorted(prices, reverse=True)


async def test_sort_preserves_order_across_pages(
    seeded_session: AsyncSession,
) -> None:
    """Sorting + pagination preserves global order across pages."""
    sb = SQLAlchemySortBackend()
    stmt = sb.apply_sorting(
        select(User),
        [SortSpec(field="name", direction=SortDirection.ASC)],
    )
    backend = SQLAlchemyBackend(seeded_session)
    all_names: list[str] = []
    for page_num in range(1, 5):
        page = await paginate(
            stmt,
            OffsetParams(page=page_num, limit=7),
            backend=backend,
        )
        all_names.extend(u.name for u in page.items)
    assert all_names == sorted(all_names)
    assert len(all_names) == 20
