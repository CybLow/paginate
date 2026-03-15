"""Tests for SQLAlchemyFilterBackend — real async SQLite database tests."""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import Executable, select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.specs import FilterSpec
from tests.fixtures.models import Product, User


async def _fetch_filtered(
    session: AsyncSession,
    model: type,
    filters: list[FilterSpec],
) -> list[Any]:
    """Apply filters and execute, returning scalar results."""
    backend = SQLAlchemyFilterBackend()
    stmt: Executable = backend.apply_filters(select(model), filters)  # type: ignore[assignment]
    result = await session.execute(stmt)
    return list(result.scalars().all())


class TestFilterEqRealDB:
    @pytest.mark.asyncio()
    async def test_filter_eq_returns_one(self, seeded_session: AsyncSession) -> None:
        filters = [FilterSpec(field="name", operator="eq", value="Alice")]

        rows = await _fetch_filtered(seeded_session, User, filters)

        assert len(rows) == 1
        assert rows[0].name == "Alice"


class TestFilterComparisonRealDB:
    @pytest.mark.asyncio()
    async def test_filter_gte_price(self, seeded_session: AsyncSession) -> None:
        filters = [FilterSpec(field="price", operator="gte", value=200)]

        rows = await _fetch_filtered(seeded_session, Product, filters)

        assert all(row.price >= 200 for row in rows)
        assert len(rows) == 3


class TestFilterTextRealDB:
    @pytest.mark.asyncio()
    async def test_filter_contains_name(self, seeded_session: AsyncSession) -> None:
        filters = [FilterSpec(field="name", operator="ilike", value="%e%")]

        rows = await _fetch_filtered(seeded_session, User, filters)

        names = {r.name for r in rows}
        assert {"Alice", "Eve", "Henry"} <= names


class TestFilterInRealDB:
    @pytest.mark.asyncio()
    async def test_filter_in_categories(self, seeded_session: AsyncSession) -> None:
        filters = [FilterSpec(field="category", operator="in", value=["Electronics", "Furniture"])]

        rows = await _fetch_filtered(seeded_session, Product, filters)

        assert {r.category for r in rows} == {"Electronics", "Furniture"}
        assert len(rows) == 6


class TestFilterCombinedRealDB:
    @pytest.mark.asyncio()
    async def test_filter_and_combined(self, seeded_session: AsyncSession) -> None:
        filters = [
            FilterSpec(field="category", operator="eq", value="Electronics"),
            FilterSpec(field="price", operator="gte", value=100),
        ]
        rows = await _fetch_filtered(seeded_session, Product, filters)

        assert all(r.category == "Electronics" and r.price >= 100 for r in rows)


class TestFilterNoMatchRealDB:
    @pytest.mark.asyncio()
    async def test_filter_no_match(self, seeded_session: AsyncSession) -> None:
        filters = [FilterSpec(field="name", operator="eq", value="Nobody")]

        rows = await _fetch_filtered(seeded_session, User, filters)

        assert rows == []


class TestFilterOrLogicRealDB:
    @pytest.mark.asyncio()
    async def test_or_logic_matches_either(self, seeded_session: AsyncSession) -> None:
        filters = [
            FilterSpec(field="name", operator="eq", value="Alice", logic=FilterLogic.OR),
            FilterSpec(field="name", operator="eq", value="Bob", logic=FilterLogic.OR),
        ]
        rows = await _fetch_filtered(seeded_session, User, filters)

        names = {r.name for r in rows}
        assert "Alice" in names
        assert "Bob" in names
