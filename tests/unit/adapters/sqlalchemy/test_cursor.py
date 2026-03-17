"""Tests for SQLAlchemy cursor backends (async and sync).

Uses an in-memory SQLite database with real SQLAlchemy ORM objects
to validate keyset pagination end-to-end.
"""

from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from pypaginate.adapters.sqlalchemy.cursor import (
    SQLAlchemyCursorBackend,
    SyncSQLAlchemyCursorBackend,
    _compute_cursors,
    _prepare_query,
)
from pypaginate.engine.cursor_codec import decode_cursor
from pypaginate.adapters.sqlalchemy.keyset import OrderColumn


# -- ORM setup ---------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


# -- Fixtures ----------------------------------------------------------------


@pytest.fixture()
def sync_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def sync_session(sync_engine):
    with Session(sync_engine) as session:
        _seed_items(session)
        yield session


@pytest.fixture()
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


@pytest.fixture()
async def async_session(async_engine):
    async with AsyncSession(async_engine) as session:
        await _async_seed_items(session)
        yield session


def _seed_items(session: Session) -> None:
    session.add_all([Item(id=i, name=f"item-{i}") for i in range(1, 11)])
    session.commit()


async def _async_seed_items(session: AsyncSession) -> None:
    session.add_all([Item(id=i, name=f"item-{i}") for i in range(1, 11)])
    await session.commit()


# -- Sync backend tests ------------------------------------------------------


class TestSyncFetchPage:
    def test_first_page(self, sync_session: Session) -> None:
        backend = SyncSQLAlchemyCursorBackend(sync_session)
        query = select(Item).order_by(Item.id.asc())

        items, nxt, prev = backend.fetch_page(query, limit=3)

        assert len(items) == 3
        assert [i.id for i in items] == [1, 2, 3]
        assert nxt is not None
        assert prev is None

    def test_second_page_via_after(self, sync_session: Session) -> None:
        backend = SyncSQLAlchemyCursorBackend(sync_session)
        query = select(Item).order_by(Item.id.asc())

        _, nxt, _ = backend.fetch_page(query, limit=3)
        items, nxt2, prev = backend.fetch_page(query, limit=3, after=nxt)

        assert [i.id for i in items] == [4, 5, 6]
        assert nxt2 is not None
        assert prev is not None

    def test_last_page_no_next(self, sync_session: Session) -> None:
        backend = SyncSQLAlchemyCursorBackend(sync_session)
        query = select(Item).order_by(Item.id.asc())

        # Navigate to page 4 (items 10 only)
        _, c1, _ = backend.fetch_page(query, limit=3)
        _, c2, _ = backend.fetch_page(query, limit=3, after=c1)
        _, c3, _ = backend.fetch_page(query, limit=3, after=c2)
        items, nxt, prev = backend.fetch_page(query, limit=3, after=c3)

        assert [i.id for i in items] == [10]
        assert nxt is None
        assert prev is not None

    def test_backward_navigation(self, sync_session: Session) -> None:
        backend = SyncSQLAlchemyCursorBackend(sync_session)
        query = select(Item).order_by(Item.id.asc())

        _, nxt, _ = backend.fetch_page(query, limit=3)
        _, _, prev = backend.fetch_page(query, limit=3, after=nxt)
        items, _, _ = backend.fetch_page(query, limit=3, before=prev)

        assert [i.id for i in items] == [1, 2, 3]

    def test_empty_result(self, sync_session: Session) -> None:
        backend = SyncSQLAlchemyCursorBackend(sync_session)
        query = select(Item).where(Item.id > 100).order_by(Item.id.asc())

        items, nxt, prev = backend.fetch_page(query, limit=3)

        assert items == []
        assert nxt is None
        assert prev is None

    def test_descending_order(self, sync_session: Session) -> None:
        backend = SyncSQLAlchemyCursorBackend(sync_session)
        query = select(Item).order_by(Item.id.desc())

        items, nxt, prev = backend.fetch_page(query, limit=3)

        assert [i.id for i in items] == [10, 9, 8]
        assert nxt is not None
        assert prev is None


# -- Async backend tests -----------------------------------------------------


class TestAsyncFetchPage:
    @pytest.mark.asyncio()
    async def test_first_page(self, async_session: AsyncSession) -> None:
        backend = SQLAlchemyCursorBackend(async_session)
        query = select(Item).order_by(Item.id.asc())

        items, nxt, prev = await backend.fetch_page(query, limit=3)

        assert len(items) == 3
        assert [i.id for i in items] == [1, 2, 3]
        assert nxt is not None
        assert prev is None

    @pytest.mark.asyncio()
    async def test_forward_then_back(
        self,
        async_session: AsyncSession,
    ) -> None:
        backend = SQLAlchemyCursorBackend(async_session)
        query = select(Item).order_by(Item.id.asc())

        _, nxt, _ = await backend.fetch_page(query, limit=3)
        _, _, prev = await backend.fetch_page(query, limit=3, after=nxt)
        items, _, _ = await backend.fetch_page(query, limit=3, before=prev)

        assert [i.id for i in items] == [1, 2, 3]

    @pytest.mark.asyncio()
    async def test_empty_result(
        self,
        async_session: AsyncSession,
    ) -> None:
        backend = SQLAlchemyCursorBackend(async_session)
        query = select(Item).where(Item.id > 100).order_by(Item.id.asc())

        items, nxt, prev = await backend.fetch_page(query, limit=5)

        assert items == []
        assert nxt is None
        assert prev is None


# -- Helper function tests ---------------------------------------------------


class TestPrepareQuery:
    def test_no_cursor(self) -> None:
        query = select(Item).order_by(Item.id.asc())
        stmt, cols, backwards = _prepare_query(
            query, limit=5, after=None, before=None,
        )
        assert not backwards
        assert len(cols) == 1

    def test_with_after_cursor(self) -> None:
        from pypaginate.engine.cursor_codec import encode_cursor

        query = select(Item).order_by(Item.id.asc())
        cursor = encode_cursor((3,))
        stmt, cols, backwards = _prepare_query(
            query, limit=5, after=cursor, before=None,
        )
        assert not backwards
        assert len(cols) == 1


class TestComputeCursors:
    def test_empty_rows(self) -> None:
        nxt, prev = _compute_cursors(
            [], [],
            has_more=False, backwards=False, has_cursor=False,
        )
        assert nxt is None
        assert prev is None
