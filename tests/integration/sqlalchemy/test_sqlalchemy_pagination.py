"""Integration tests for SQLAlchemy offset pagination with real SQLite.

Validates SQLAlchemyBackend count, fetch, and full paginate() calls
against an actual async in-memory database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from pypaginate import OffsetParams, OverflowStrategy, paginate
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from tests.fixtures.models import User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_count_returns_total_users(seeded_session: AsyncSession) -> None:
    """Backend count reflects seeded row count."""
    backend = SQLAlchemyBackend(seeded_session)
    count = await backend.count(select(User))
    assert count == 20


async def test_fetch_returns_correct_slice(seeded_session: AsyncSession) -> None:
    """Fetch with offset/limit returns the right rows."""
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(select(User).order_by(User.id), offset=5, limit=3)
    assert len(items) == 3
    assert items[0].id == 6


async def test_fetch_beyond_total_returns_empty(seeded_session: AsyncSession) -> None:
    """Fetch past the last row yields an empty list."""
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(select(User).order_by(User.id), offset=100, limit=5)
    assert items == []


async def test_paginate_first_page(seeded_session: AsyncSession) -> None:
    """First page contains the first N users."""
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=1, limit=5),
        backend=backend,
    )
    assert page.total == 20
    assert page.page == 1
    assert len(page.items) == 5
    assert page.items[0].id == 1


async def test_paginate_middle_page(seeded_session: AsyncSession) -> None:
    """Middle page returns offset-correct items."""
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=2, limit=5),
        backend=backend,
    )
    assert page.page == 2
    assert len(page.items) == 5
    assert page.items[0].id == 6


async def test_paginate_last_page_partial(seeded_session: AsyncSession) -> None:
    """Last page may contain fewer items than limit."""
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=3, limit=7),
        backend=backend,
    )
    assert page.page == 3
    assert len(page.items) == 6
    assert not page.has_next


async def test_paginate_all_pages_completeness(seeded_session: AsyncSession) -> None:
    """Iterating all pages returns every user exactly once."""
    backend = SQLAlchemyBackend(seeded_session)
    all_items: list[User] = []
    page_num = 1
    while True:
        page = await paginate(
            select(User).order_by(User.id),
            OffsetParams(page=page_num, limit=7),
            backend=backend,
        )
        all_items.extend(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert len(all_items) == 20
    assert len({u.id for u in all_items}) == 20


async def test_paginate_overflow_clamp(seeded_session: AsyncSession) -> None:
    """Clamp overflow redirects to the last valid page."""
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=999, limit=5),
        backend=backend,
        overflow=OverflowStrategy.CLAMP,
    )
    assert page.page == 4
    assert len(page.items) == 5


async def test_paginate_overflow_empty(seeded_session: AsyncSession) -> None:
    """Default overflow returns empty items for out-of-range page."""
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(
        select(User).order_by(User.id),
        OffsetParams(page=999, limit=5),
        backend=backend,
    )
    assert page.items == []
    assert page.total == 20
