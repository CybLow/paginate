"""PostgreSQL integration tests — real async I/O against a live database.

Drives the SQLAlchemy adapter end-to-end over a *real* PostgreSQL instance
(reached via ``$PYPAGINATE_PG_URL``; the whole module is skipped when the
variable is unset, so it no-ops locally and runs in CI). Two data sets are used:

* the deterministic 50-row :func:`make_users` set on the shared foundation
  ``User`` model (via the ``postgres_session`` fixture) for offset pagination,
  keyset/cursor pagination, filtering operators, sorting, and the full
  filter + sort + paginate pipeline; and
* a tiny, locally-managed ``Contact`` table with a *nullable* column for the
  ``is_null`` / ``is_not_null`` operators and ``NULLS FIRST`` / ``NULLS LAST``
  placement — behaviour that only a genuinely nullable column can exercise.

Every expected ordering is computed in Python over the same rows, so the
assertions verify the SQL the adapter emits actually executes correctly on
PostgreSQL rather than echoing hand-written magic numbers.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import Select
from tests.factories.data import make_users
from tests.fixtures.helpers import ids_of
from tests.fixtures.models import User

from pypaginate import CursorParams, FilterSpec, OffsetParams, SortSpec
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemyCursorBackend,
    build_filter,
    build_order_by,
)


_PG_URL = os.environ.get("PYPAGINATE_PG_URL")

pytestmark = [
    pytest.mark.skipif(not _PG_URL, reason="PYPAGINATE_PG_URL is not set"),
    pytest.mark.postgres,
    pytest.mark.sqlalchemy,
]


#: The same deterministic rows the ``postgres_session`` fixture seeds.
_USERS: list[dict[str, object]] = make_users(50)


def _expected_ids(predicate: Callable[[dict[str, object]], bool]) -> list[int]:
    """Ascending ids of the seeded users matching ``predicate`` (the SQL oracle)."""
    return sorted(int(row["id"]) for row in _USERS if predicate(row))


async def _scalars(session: AsyncSession, stmt: Select[Any]) -> list[Any]:
    """Execute ``stmt`` and return its scalar column as a list."""
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def _filter_ids(session: AsyncSession, model: type, spec: FilterSpec) -> list[int]:
    """Ascending ids matching a single ``spec`` translated by the adapter."""
    condition = build_filter(model, [spec])
    stmt = select(model.id).where(condition).order_by(model.id)
    return await _scalars(session, stmt)


# -- Offset pagination ------------------------------------------------------- #


async def test_offset_first_page(postgres_session: AsyncSession) -> None:
    backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(postgres_session)
    query = select(User).order_by(User.id)

    page = await backend.paginate(query, OffsetParams(page=1, limit=20))

    assert ids_of(page.items) == list(range(1, 21))
    assert page.total == 50
    assert page.pages == 3
    assert page.has_next is True
    assert page.has_previous is False


async def test_offset_last_page(postgres_session: AsyncSession) -> None:
    backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(postgres_session)
    query = select(User).order_by(User.id)

    page = await backend.paginate(query, OffsetParams(page=3, limit=20))

    assert ids_of(page.items) == list(range(41, 51))
    assert page.has_next is False
    assert page.has_previous is True


# -- Keyset / cursor pagination ---------------------------------------------- #


async def test_keyset_walks_every_row_in_order(postgres_session: AsyncSession) -> None:
    backend: SQLAlchemyCursorBackend[User] = SQLAlchemyCursorBackend(postgres_session)
    query = select(User).order_by(User.id)

    seen: list[int] = []
    cursor: str | None = None
    while True:
        page = await backend.fetch_page(query, CursorParams(limit=10, after=cursor))
        seen.extend(ids_of(page.items))
        if not page.has_next:
            break
        cursor = page.next_cursor

    assert seen == list(range(1, 51))


async def test_keyset_cursor_is_stable_across_inserts(postgres_session: AsyncSession) -> None:
    backend: SQLAlchemyCursorBackend[User] = SQLAlchemyCursorBackend(postgres_session)
    query = select(User).order_by(User.id)

    first = await backend.fetch_page(query, CursorParams(limit=10))
    assert ids_of(first.items) == list(range(1, 11))

    # Insert a row that sorts *before* the cursor: an OFFSET page would now shift
    # and re-show id 10, but a keyset cursor stays anchored to the last id seen.
    postgres_session.add(_new_user(0))
    await postgres_session.commit()

    second = await backend.fetch_page(query, CursorParams(limit=10, after=first.next_cursor))

    assert ids_of(second.items) == list(range(11, 21))
    assert 10 not in ids_of(second.items)
    assert 0 not in ids_of(second.items)


def _new_user(user_id: int) -> User:
    """A valid extra ``User`` row that sorts ahead of the seeded ids."""
    return User(
        id=user_id,
        name="Zeta Newcomer",
        email=f"zeta{user_id}@example.com",
        age=99,
        score=1.0,
        active=True,
        created_at="2019-01-01T00:00:00+00:00",
    )


# -- Filtering operators (correct WHERE on real PostgreSQL) ------------------ #


async def test_filter_gte(postgres_session: AsyncSession) -> None:
    spec = FilterSpec(field="age", operator="gte", value=50)

    ids = await _filter_ids(postgres_session, User, spec)

    assert ids == _expected_ids(lambda r: int(r["age"]) >= 50)


async def test_filter_in(postgres_session: AsyncSession) -> None:
    spec = FilterSpec(field="age", operator="in", value=[25, 32])

    ids = await _filter_ids(postgres_session, User, spec)

    assert ids == _expected_ids(lambda r: r["age"] in (25, 32))


async def test_filter_between(postgres_session: AsyncSession) -> None:
    spec = FilterSpec(field="age", operator="between", value=[30, 40])

    ids = await _filter_ids(postgres_session, User, spec)

    assert ids == _expected_ids(lambda r: 30 <= int(r["age"]) <= 40)


async def test_filter_ilike_is_case_insensitive(postgres_session: AsyncSession) -> None:
    spec = FilterSpec(field="name", operator="ilike", value="%alice%")

    ids = await _filter_ids(postgres_session, User, spec)

    assert ids == _expected_ids(lambda r: "alice" in str(r["name"]).lower())
    assert ids == [1, 11, 21, 31, 41]


# -- Sorting (no nulls on this model) ---------------------------------------- #


async def test_sort_age_descending(postgres_session: AsyncSession) -> None:
    clauses = build_order_by(User, [SortSpec(field="age", direction="desc")])
    stmt = select(User.id).order_by(*clauses, User.id)

    ids = await _scalars(postgres_session, stmt)

    expected = [int(r["id"]) for r in sorted(_USERS, key=lambda r: (-int(r["age"]), int(r["id"])))]
    assert ids == expected


# -- Full filter + sort + paginate pipeline ---------------------------------- #


async def test_filter_sort_paginate_pipeline(postgres_session: AsyncSession) -> None:
    condition = build_filter(User, [FilterSpec(field="active", operator="eq", value=True)])
    clauses = build_order_by(User, [SortSpec(field="score", direction="desc")])
    query = select(User).where(condition).order_by(*clauses, User.id)

    page = await SQLAlchemyBackend(postgres_session).paginate(query, OffsetParams(page=1, limit=10))

    active = [r for r in _USERS if r["active"]]
    ordered = sorted(active, key=lambda r: (-float(r["score"]), int(r["id"])))
    assert ids_of(page.items) == [int(r["id"]) for r in ordered[:10]]
    assert page.total == len(active)


# -- Null-aware filtering and placement (dedicated nullable model) ----------- #


class _ContactBase(DeclarativeBase):
    """Isolated declarative base for the nullable-column test model."""


class Contact(_ContactBase):
    """A minimal row with a nullable ``nickname`` for null-aware assertions."""

    __tablename__ = "pg_contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)


#: (id, nickname) — a deterministic mix of present and NULL nicknames.
_CONTACTS: tuple[tuple[int, str | None], ...] = (
    (1, "Al"),
    (2, None),
    (3, "Caz"),
    (4, None),
    (5, "Evie"),
    (6, "Bo"),
)


@pytest.fixture
async def contact_session() -> AsyncIterator[AsyncSession]:
    """An async PG session seeded with the nullable ``Contact`` rows."""
    engine = create_async_engine(os.environ["PYPAGINATE_PG_URL"])
    async with engine.begin() as conn:
        await conn.run_sync(_ContactBase.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        session.add_all(Contact(id=i, nickname=n) for i, n in _CONTACTS)
        await session.commit()
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(_ContactBase.metadata.drop_all)
    await engine.dispose()


async def test_filter_is_null(contact_session: AsyncSession) -> None:
    spec = FilterSpec(field="nickname", operator="is_null", value=None)

    ids = await _filter_ids(contact_session, Contact, spec)

    assert ids == [2, 4]


async def test_filter_is_not_null(contact_session: AsyncSession) -> None:
    spec = FilterSpec(field="nickname", operator="is_not_null", value=None)

    ids = await _filter_ids(contact_session, Contact, spec)

    assert ids == [1, 3, 5, 6]


async def test_sort_nulls_first(contact_session: AsyncSession) -> None:
    clauses = build_order_by(Contact, [SortSpec(field="nickname", direction="asc", nulls="first")])
    stmt = select(Contact.id).order_by(*clauses, Contact.id)

    ids = await _scalars(contact_session, stmt)

    # NULLs (2, 4) lead, then nicknames ascending: Al(1), Bo(6), Caz(3), Evie(5).
    assert ids == [2, 4, 1, 6, 3, 5]


async def test_sort_nulls_last(contact_session: AsyncSession) -> None:
    clauses = build_order_by(Contact, [SortSpec(field="nickname", direction="asc", nulls="last")])
    stmt = select(Contact.id).order_by(*clauses, Contact.id)

    ids = await _scalars(contact_session, stmt)

    assert ids == [1, 6, 3, 5, 2, 4]
