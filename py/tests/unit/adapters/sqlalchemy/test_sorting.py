"""Tests for SQLAlchemySortBackend.

Mock tests verify direction/nulls delegation.
Real DB tests verify ORDER BY against async SQLite.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import Executable, select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.domain.specs import SortSpec
from tests.fixtures.models import Product, User


@pytest.fixture()
def sort_backend() -> SQLAlchemySortBackend:
    """Sort backend instance."""
    return SQLAlchemySortBackend()


# -- Mock tests: direction & nulls ------------------------------------------


class TestDirectionMock:
    @patch("pypaginate.adapters.sqlalchemy.sorting.resolve_column")
    def test_asc_direction_applied(
        self,
        mock_resolve: MagicMock,
        sort_backend: SQLAlchemySortBackend,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = SortSpec(field="name", direction=SortDirection.ASC)

        sort_backend.apply_sorting(MagicMock(), [spec])

        col.asc.assert_called_once()

    @patch("pypaginate.adapters.sqlalchemy.sorting.resolve_column")
    def test_desc_direction_applied(
        self,
        mock_resolve: MagicMock,
        sort_backend: SQLAlchemySortBackend,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = SortSpec(field="name", direction=SortDirection.DESC)

        sort_backend.apply_sorting(MagicMock(), [spec])

        col.desc.assert_called_once()


class TestNullsMock:
    @patch("pypaginate.adapters.sqlalchemy.sorting.resolve_column")
    def test_nulls_first_applied(
        self,
        mock_resolve: MagicMock,
        sort_backend: SQLAlchemySortBackend,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = SortSpec(field="age", nulls=NullsPosition.FIRST)

        sort_backend.apply_sorting(MagicMock(), [spec])

        col.asc.return_value.nulls_first.assert_called_once()

    @patch("pypaginate.adapters.sqlalchemy.sorting.resolve_column")
    def test_nulls_last_applied(
        self,
        mock_resolve: MagicMock,
        sort_backend: SQLAlchemySortBackend,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = SortSpec(field="age", nulls=NullsPosition.LAST)

        sort_backend.apply_sorting(MagicMock(), [spec])

        col.asc.return_value.nulls_last.assert_called_once()


class TestEdgeCasesMock:
    def test_empty_sorting_returns_unchanged_query(
        self,
        sort_backend: SQLAlchemySortBackend,
    ) -> None:
        query = MagicMock()

        result = sort_backend.apply_sorting(query, [])

        assert result is query

    @patch("pypaginate.adapters.sqlalchemy.sorting.resolve_column")
    def test_multiple_specs_apply_order_by(
        self,
        mock_resolve: MagicMock,
        sort_backend: SQLAlchemySortBackend,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        specs = [
            SortSpec(field="name"),
            SortSpec(field="age", direction=SortDirection.DESC),
        ]
        query = MagicMock()

        sort_backend.apply_sorting(query, specs)

        query.order_by.assert_called_once()


# -- Real DB tests -----------------------------------------------------------


async def _fetch_sorted(
    session: AsyncSession,
    model: type,
    specs: list[SortSpec],
) -> list[Any]:
    """Apply sorting and execute, returning scalar results."""
    backend = SQLAlchemySortBackend()
    stmt: Executable = backend.apply_sorting(select(model), specs)  # type: ignore[assignment]
    result = await session.execute(stmt)
    return list(result.scalars().all())


class TestSortAscRealDB:
    @pytest.mark.asyncio()
    async def test_sort_asc_by_name(self, seeded_session: AsyncSession) -> None:
        specs = [SortSpec(field="name", direction=SortDirection.ASC)]

        rows = await _fetch_sorted(seeded_session, User, specs)

        names = [r.name for r in rows]
        assert names == sorted(names)


class TestSortDescRealDB:
    @pytest.mark.asyncio()
    async def test_sort_desc_by_price(self, seeded_session: AsyncSession) -> None:
        specs = [SortSpec(field="price", direction=SortDirection.DESC)]

        rows = await _fetch_sorted(seeded_session, Product, specs)

        prices = [r.price for r in rows]
        assert prices == sorted(prices, reverse=True)


class TestSortNullsRealDB:
    @pytest.mark.asyncio()
    async def test_sort_nullable_description(self, seeded_session: AsyncSession) -> None:
        specs = [SortSpec(field="description", nulls=NullsPosition.LAST)]

        rows = await _fetch_sorted(seeded_session, Product, specs)

        assert all(r.description is None for r in rows)


class TestSortMultipleFieldsRealDB:
    @pytest.mark.asyncio()
    async def test_sort_by_category_then_name(self, seeded_session: AsyncSession) -> None:
        specs = [
            SortSpec(field="category", direction=SortDirection.ASC),
            SortSpec(field="name", direction=SortDirection.ASC),
        ]

        rows = await _fetch_sorted(seeded_session, Product, specs)

        pairs = [(r.category, r.name) for r in rows]
        assert pairs == sorted(pairs)
