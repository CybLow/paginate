"""Tests for SQLAlchemyBackend async pagination.

Mock tests verify delegation. Real DB tests verify SQL execution
against an async SQLite database with seeded data.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from tests.fixtures.models import User


# -- Fixtures ----------------------------------------------------------------


@pytest.fixture()
def mock_session() -> AsyncMock:
    """Mock AsyncSession."""
    return AsyncMock()


@pytest.fixture()
def mock_backend(mock_session: AsyncMock) -> SQLAlchemyBackend:
    """Backend with mocked session."""
    return SQLAlchemyBackend(mock_session)


# -- Mock tests: delegation -------------------------------------------------


class TestCountMock:
    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.backend._execute_count")
    async def test_count_returns_scalar_result(
        self,
        mock_exec: AsyncMock,
        mock_backend: SQLAlchemyBackend,
    ) -> None:
        mock_exec.return_value = 42

        count = await mock_backend.count(MagicMock())

        assert count == 42

    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.backend._execute_count")
    async def test_count_returns_zero_for_empty(
        self,
        mock_exec: AsyncMock,
        mock_backend: SQLAlchemyBackend,
    ) -> None:
        mock_exec.return_value = 0

        count = await mock_backend.count(MagicMock())

        assert count == 0

    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.backend._execute_count")
    async def test_count_delegates_to_execute_count(
        self,
        mock_exec: AsyncMock,
        mock_backend: SQLAlchemyBackend,
        mock_session: AsyncMock,
    ) -> None:
        mock_exec.return_value = 5
        query = MagicMock()

        await mock_backend.count(query)

        mock_exec.assert_awaited_once_with(mock_session, query)


class TestFetchMock:
    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.backend._execute_fetch")
    async def test_fetch_returns_items(
        self,
        mock_exec: AsyncMock,
        mock_backend: SQLAlchemyBackend,
    ) -> None:
        mock_exec.return_value = ["a", "b"]

        items = await mock_backend.fetch(MagicMock(), offset=10, limit=5)

        assert items == ["a", "b"]

    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.backend._execute_fetch")
    async def test_fetch_returns_empty_list(
        self,
        mock_exec: AsyncMock,
        mock_backend: SQLAlchemyBackend,
    ) -> None:
        mock_exec.return_value = []

        items = await mock_backend.fetch(MagicMock(), offset=0, limit=10)

        assert items == []

    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.backend._execute_fetch")
    async def test_fetch_delegates_with_correct_args(
        self,
        mock_exec: AsyncMock,
        mock_backend: SQLAlchemyBackend,
        mock_session: AsyncMock,
    ) -> None:
        mock_exec.return_value = [1]
        query = MagicMock()

        await mock_backend.fetch(query, offset=5, limit=3)

        mock_exec.assert_awaited_once_with(mock_session, query, 5, 3)


# -- Real DB tests -----------------------------------------------------------


class TestCountRealDB:
    @pytest.mark.asyncio()
    async def test_count_real_db(self, seeded_session: AsyncSession) -> None:
        backend = SQLAlchemyBackend(seeded_session)

        count = await backend.count(select(User))

        assert count == 10

    @pytest.mark.asyncio()
    async def test_count_empty_table(self, session: AsyncSession) -> None:
        backend = SQLAlchemyBackend(session)

        count = await backend.count(select(User))

        assert count == 0


class TestFetchRealDB:
    @pytest.mark.asyncio()
    async def test_fetch_with_offset_limit(self, seeded_session: AsyncSession) -> None:
        backend = SQLAlchemyBackend(seeded_session)

        items = await backend.fetch(select(User), offset=2, limit=3)

        assert len(items) == 3

    @pytest.mark.asyncio()
    async def test_fetch_beyond_total(self, seeded_session: AsyncSession) -> None:
        backend = SQLAlchemyBackend(seeded_session)

        items = await backend.fetch(select(User), offset=100, limit=10)

        assert items == []
