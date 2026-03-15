"""Integration tests for SQLAlchemy search backend with real SQLite.

Validates SQLAlchemySearchBackend ILIKE queries against actual rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from pypaginate import OffsetParams, SearchFieldMode, SearchSpec, paginate
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.search import SQLAlchemySearchBackend
from tests.fixtures.models import User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_search_contains_partial(seeded_session: AsyncSession) -> None:
    """CONTAINS search for 'User_1' matches User_1 plus User_10..19."""
    sb = SQLAlchemySearchBackend()
    stmt = sb.apply_search(
        select(User),
        SearchSpec(query="User_1", fields=("name",)),
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt.order_by(User.id), offset=0, limit=30)
    assert len(items) == 11  # User_1, User_10..User_19


async def test_search_prefix_by_email(seeded_session: AsyncSession) -> None:
    """PREFIX search on email matches the expected subset."""
    sb = SQLAlchemySearchBackend()
    stmt = sb.apply_search(
        select(User),
        SearchSpec(
            query="user1",
            fields=("email",),
            mode=SearchFieldMode.PREFIX,
        ),
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=30)
    assert all(u.email.startswith("user1") for u in items)
    assert len(items) >= 1


async def test_search_no_match_returns_empty(seeded_session: AsyncSession) -> None:
    """Search with non-existent term yields zero rows."""
    sb = SQLAlchemySearchBackend()
    stmt = sb.apply_search(
        select(User),
        SearchSpec(query="ZZZZNOTFOUND", fields=("name",)),
    )
    backend = SQLAlchemyBackend(seeded_session)
    count = await backend.count(stmt)
    assert count == 0


async def test_search_multiple_fields(seeded_session: AsyncSession) -> None:
    """Search across name and email returns matches from either."""
    sb = SQLAlchemySearchBackend()
    stmt = sb.apply_search(
        select(User),
        SearchSpec(query="user0", fields=("name", "email")),
    )
    backend = SQLAlchemyBackend(seeded_session)
    items = await backend.fetch(stmt, offset=0, limit=30)
    assert len(items) >= 1


async def test_search_plus_paginate(seeded_session: AsyncSession) -> None:
    """Search then paginate returns correct page from filtered set."""
    sb = SQLAlchemySearchBackend()
    stmt = sb.apply_search(
        select(User).order_by(User.id),
        SearchSpec(query="User_1", fields=("name",)),
    )
    backend = SQLAlchemyBackend(seeded_session)
    page = await paginate(stmt, OffsetParams(page=1, limit=5), backend=backend)
    assert page.total == 11
    assert len(page.items) == 5


async def test_search_empty_query_returns_all(seeded_session: AsyncSession) -> None:
    """Empty search query returns the full dataset unchanged."""
    sb = SQLAlchemySearchBackend()
    stmt = sb.apply_search(
        select(User),
        SearchSpec(query="", fields=("name",)),
    )
    backend = SQLAlchemyBackend(seeded_session)
    count = await backend.count(stmt)
    assert count == 20
