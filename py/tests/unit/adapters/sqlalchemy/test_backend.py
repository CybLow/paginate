"""Tests for SQLAlchemy offset pagination backends (async and sync).

Real DB tests verify SQL execution against in-memory SQLite databases
with seeded data.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from pypaginate.adapters.sqlalchemy.backend import (
    SQLAlchemyBackend,
    SyncSQLAlchemyBackend,
)
from tests.fixtures.models import User


# -- Async real DB tests -----------------------------------------------------


class TestAsyncCountRealDB:
    @pytest.mark.asyncio()
    async def test_count_real_db(
        self,
        seeded_session: AsyncSession,
    ) -> None:
        backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(seeded_session)

        count = await backend.count(select(User))

        assert count == 10

    @pytest.mark.asyncio()
    async def test_count_empty_table(
        self,
        session: AsyncSession,
    ) -> None:
        backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(session)

        count = await backend.count(select(User))

        assert count == 0


class TestAsyncFetchRealDB:
    @pytest.mark.asyncio()
    async def test_fetch_with_offset_limit(
        self,
        seeded_session: AsyncSession,
    ) -> None:
        backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(seeded_session)

        items = await backend.fetch(select(User), offset=2, limit=3)

        assert len(items) == 3

    @pytest.mark.asyncio()
    async def test_fetch_beyond_total(
        self,
        seeded_session: AsyncSession,
    ) -> None:
        backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(seeded_session)

        items = await backend.fetch(select(User), offset=100, limit=10)

        assert items == []


# -- Sync real DB tests ------------------------------------------------------


class TestSyncCountRealDB:
    def test_sync_count_real_db(
        self,
        sync_seeded_session: Session,
    ) -> None:
        backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(
            sync_seeded_session,
        )

        count = backend.count(select(User))

        assert count == 10

    def test_sync_count_empty_table(
        self,
        sync_session: Session,
    ) -> None:
        backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(
            sync_session,
        )

        count = backend.count(select(User))

        assert count == 0


class TestSyncFetchRealDB:
    def test_sync_fetch_real_db(
        self,
        sync_seeded_session: Session,
    ) -> None:
        backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(
            sync_seeded_session,
        )

        items = backend.fetch(select(User), offset=2, limit=3)

        assert len(items) == 3

    def test_sync_fetch_empty(
        self,
        sync_session: Session,
    ) -> None:
        backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(
            sync_session,
        )

        items = backend.fetch(select(User), offset=0, limit=10)

        assert items == []

    def test_sync_fetch_beyond_total(
        self,
        sync_seeded_session: Session,
    ) -> None:
        backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(
            sync_seeded_session,
        )

        items = backend.fetch(select(User), offset=100, limit=10)

        assert items == []
