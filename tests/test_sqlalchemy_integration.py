"""SQLAlchemy integration tests for pagination engine.

Tests for SqlPaginator, count builders, and collations using async SQLite.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from pypaginate.core.context import PaginationContext
from pypaginate.core.pages import PageParams
from pypaginate.database.collations import (
    CollationPlan,
    _apply_plan,
    _execute_statements,
    _log_notes,
    ensure_database_collations,
)
from pypaginate.engines.sql import SqlPaginator, get_pagination_strategy
from pypaginate.exceptions import PaginationConfigurationError
from pypaginate.query.builders.count_builder import (
    build_count_statement,
    fetch_count,
    strip_ordering,
)

from .conftest import User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


pytestmark = [pytest.mark.sqlalchemy, pytest.mark.integration]


class TestSqlPaginatorOffsetPagination:
    """Test SqlPaginator offset-based pagination."""

    async def test_first_page(self, populated_session: AsyncSession) -> None:
        """Should return first page correctly."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=1, limit=3)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert len(snapshot.items) == 3
        assert snapshot.total == 10
        assert snapshot.params.page == 1
        assert snapshot.items[0].name == "Alice"
        assert snapshot.items[2].name == "Charlie"

    async def test_second_page(self, populated_session: AsyncSession) -> None:
        """Should return second page correctly."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=2, limit=3)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert len(snapshot.items) == 3
        assert snapshot.items[0].name == "David"

    async def test_last_page_partial(self, populated_session: AsyncSession) -> None:
        """Should handle partial last page."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=4, limit=3)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert len(snapshot.items) == 1
        assert snapshot.items[0].name == "Jack"

    async def test_page_beyond_total(self, populated_session: AsyncSession) -> None:
        """Should return empty for page beyond total."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=10, limit=3)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert len(snapshot.items) == 0
        assert snapshot.total == 10

    async def test_empty_table(self, async_session: AsyncSession) -> None:
        """Should handle empty table."""
        paginator: SqlPaginator[User] = SqlPaginator(async_session, clamp=False)
        params = PageParams(page=1, limit=10)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert len(snapshot.items) == 0
        assert snapshot.total == 0


class TestSqlPaginatorWithClamping:
    """Test SqlPaginator with clamping enabled."""

    async def test_clamp_page_beyond_total(self, populated_session: AsyncSession) -> None:
        """Should clamp page number to valid bounds."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=True)
        params = PageParams(page=100, limit=3)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        # Clamped to last valid page
        assert snapshot.params.page <= 4
        assert snapshot.total == 10

    async def test_no_clamp_when_disabled(self, populated_session: AsyncSession) -> None:
        """Should not clamp when disabled."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=100, limit=3)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        # Page not clamped - returns empty
        assert len(snapshot.items) == 0
        assert snapshot.params.page == 100


class TestSqlPaginatorUnique:
    """Test SqlPaginator unique row handling."""

    async def test_unique_true(self, populated_session: AsyncSession) -> None:
        """Should deduplicate rows when unique=True."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=1, limit=5)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=True,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert len(snapshot.items) == 5
        assert snapshot.total == 10


class TestSqlPaginatorNonScalars:
    """Test SqlPaginator with scalars=False."""

    async def test_non_scalar_results(self, populated_session: AsyncSession) -> None:
        """Should return row tuples when scalars=False."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        params = PageParams(page=1, limit=2)
        context: PaginationContext[PageParams] = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )
        query = select(User).order_by(User.id)

        snapshot = await paginator.paginate(query, context, scalars=False)

        assert len(snapshot.items) == 2
        # Items are row tuples, not User instances
        assert snapshot.total == 10


class TestCountBuilder:
    """Test count builder functions."""

    async def test_strip_ordering(self) -> None:
        """Should remove ORDER BY from query."""
        query = select(User).order_by(User.id, User.name.desc())
        stripped = strip_ordering(query)

        # Verify ORDER BY is removed
        compiled = str(stripped.compile())
        assert "ORDER BY" not in compiled

    async def test_build_count_statement_basic(self) -> None:
        """Should build count statement from query."""
        query = select(User).order_by(User.id)
        count_stmt = build_count_statement(query, None, unique=False)

        compiled = str(count_stmt.compile())
        assert "count" in compiled.lower()

    async def test_build_count_statement_unique(self) -> None:
        """Should build unique count statement."""
        query = select(User).order_by(User.id)
        count_stmt = build_count_statement(query, None, unique=True)

        compiled = str(count_stmt.compile())
        assert "count" in compiled.lower()

    async def test_build_count_statement_explicit(self) -> None:
        """Should use explicit count query when provided."""
        query = select(User)
        explicit = select(User.id).where(User.name.like("A%"))
        count_stmt = build_count_statement(query, explicit, unique=False)

        # Should return the explicit query
        assert count_stmt is explicit

    async def test_fetch_count(self, populated_session: AsyncSession) -> None:
        """Should fetch count from database."""
        query = select(User)
        count_stmt = build_count_statement(query, None, unique=False)

        count = await fetch_count(populated_session, count_stmt)

        assert count == 10

    async def test_fetch_count_empty(self, async_session: AsyncSession) -> None:
        """Should return 0 for empty table."""
        query = select(User)
        count_stmt = build_count_statement(query, None, unique=False)

        count = await fetch_count(async_session, count_stmt)

        assert count == 0


class TestCollations:
    """Test database collation functions."""

    async def test_ensure_database_collations_sqlite(self, async_engine: AsyncEngine) -> None:
        """Should return SQLite plan for SQLite engine."""
        plan = await ensure_database_collations(async_engine)

        assert plan is not None
        assert isinstance(plan, CollationPlan)
        # SQLite plan has no statements (notes only)
        assert len(plan.statements) == 0
        assert len(plan.notes) > 0

    async def test_apply_plan_with_statements(self, async_engine: AsyncEngine) -> None:
        """Should execute plan statements."""
        # Create a simple plan with a no-op statement
        plan = CollationPlan(
            statements=("SELECT 1",),
            notes=("Test note",),
        )

        # Should not raise
        await _apply_plan(async_engine, plan)

    async def test_apply_plan_empty(self, async_engine: AsyncEngine) -> None:
        """Should handle empty plan."""
        plan = CollationPlan(statements=(), notes=())

        # Should not raise
        await _apply_plan(async_engine, plan)

    async def test_execute_statements(self, async_engine: AsyncEngine) -> None:
        """Should execute SQL statements."""
        statements = ("SELECT 1", "SELECT 2")

        # Should not raise
        await _execute_statements(async_engine, statements)

    def test_log_notes_with_notes(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should log notes at debug level."""
        import logging

        with caplog.at_level(logging.DEBUG):
            _log_notes(("Note 1", "Note 2"))

        assert "Note 1" in caplog.text
        assert "Note 2" in caplog.text

    def test_log_notes_empty(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should not log when no notes."""
        import logging

        with caplog.at_level(logging.DEBUG):
            _log_notes(())

        assert caplog.text == ""


class TestGetPaginationStrategy:
    """Test get_pagination_strategy function."""

    def test_offset_strategy(self) -> None:
        """Should return offset strategy."""
        strategy = get_pagination_strategy("offset")
        assert strategy is SqlPaginator.paginate

    def test_keyset_strategy(self) -> None:
        """Should return keyset strategy."""
        strategy = get_pagination_strategy("keyset")
        assert strategy is SqlPaginator.paginate_keyset

    def test_unknown_strategy_raises(self) -> None:
        """Should raise for unknown strategy."""
        with pytest.raises(PaginationConfigurationError) as exc_info:
            get_pagination_strategy("unknown")

        assert "Unknown pagination strategy" in str(exc_info.value)
