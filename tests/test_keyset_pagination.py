"""Tests for keyset (cursor-based) pagination.

Integration tests for keyset pagination with SQLAlchemy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from pypaginate.core.pages import KeysetPageParams
from pypaginate.engines.keyset import _keyset_kwargs, select_keyset_page
from pypaginate.engines.sql import SqlPaginator

from .conftest import User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = [pytest.mark.sqlalchemy, pytest.mark.integration]


class TestKeysetKwargs:
    """Test _keyset_kwargs helper function."""

    def test_basic_params(self) -> None:
        """Should build kwargs from basic params."""
        params = KeysetPageParams(limit=10)
        kwargs = _keyset_kwargs(params, unique=False)

        assert kwargs["per_page"] == 10
        assert kwargs["unique"] is False
        assert kwargs["after"] is None
        assert kwargs["before"] is None
        assert kwargs["page"] is None

    def test_with_unique(self) -> None:
        """Should set unique flag."""
        params = KeysetPageParams(limit=5)
        kwargs = _keyset_kwargs(params, unique=True)

        assert kwargs["unique"] is True

    def test_with_page(self) -> None:
        """Should pass page parameter."""
        params = KeysetPageParams(limit=10, page="some_bookmark")
        kwargs = _keyset_kwargs(params, unique=False)

        assert kwargs["page"] == "some_bookmark"


class TestSelectKeysetPage:
    """Test select_keyset_page function."""

    async def test_first_page(self, populated_session: AsyncSession) -> None:
        """Should return first page of results."""
        query = select(User).order_by(User.id)
        params = KeysetPageParams(limit=3)

        page = await select_keyset_page(populated_session, query, params, unique=False)

        assert len(list(page)) == 3

    async def test_with_unique(self, populated_session: AsyncSession) -> None:
        """Should work with unique=True."""
        query = select(User).order_by(User.id)
        params = KeysetPageParams(limit=5)

        page = await select_keyset_page(populated_session, query, params, unique=True)

        assert len(list(page)) == 5


class TestSqlPaginatorKeyset:
    """Test SqlPaginator keyset pagination method."""

    async def test_keyset_first_page(self, populated_session: AsyncSession) -> None:
        """Should return first page with keyset pagination."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = KeysetPageParams(limit=3)
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate_keyset(query, params, unique=False, scalars=True)

        assert len(snapshot.items) == 3
        assert snapshot.params.limit == 3
        # Should have next bookmark for more pages
        assert snapshot.next is not None
        # Should not have previous on first page
        assert snapshot.previous is None

    async def test_keyset_navigation(self, populated_session: AsyncSession) -> None:
        """Should navigate using bookmarks."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        query = select(User).order_by(User.id)

        # Get first page
        first_params = KeysetPageParams(limit=3)
        first_snapshot = await paginator.paginate_keyset(
            query, first_params, unique=False, scalars=True
        )

        # Navigate to second page using 'after' bookmark
        assert first_snapshot.next is not None
        second_params = KeysetPageParams(limit=3, after=first_snapshot.next)
        second_snapshot = await paginator.paginate_keyset(
            query, second_params, unique=False, scalars=True
        )

        assert len(second_snapshot.items) == 3
        # Second page should have previous bookmark
        assert second_snapshot.previous is not None

    async def test_keyset_with_unique(self, populated_session: AsyncSession) -> None:
        """Should work with unique=True."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = KeysetPageParams(limit=5)
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate_keyset(query, params, unique=True, scalars=True)

        assert len(snapshot.items) == 5

    async def test_keyset_non_scalars(self, populated_session: AsyncSession) -> None:
        """Should return row tuples when scalars=False."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = KeysetPageParams(limit=2)
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate_keyset(query, params, unique=False, scalars=False)

        assert len(snapshot.items) == 2

    async def test_keyset_empty_results(self, async_session: AsyncSession) -> None:
        """Should handle empty table."""
        paginator: SqlPaginator[User] = SqlPaginator(async_session, clamp=False)
        params = KeysetPageParams(limit=10)
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate_keyset(query, params, unique=False, scalars=True)

        assert len(snapshot.items) == 0
        assert snapshot.next is None
