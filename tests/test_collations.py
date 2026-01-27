"""Tests for database collations module."""

from __future__ import annotations

import pytest

from pypaginator.database.collations import (
    CollationPlan,
    recommend_collation_plan,
)


class TestCollationPlan:
    """Test CollationPlan dataclass."""

    def test_creation(self) -> None:
        """Should create plan."""
        plan = CollationPlan(
            statements=("CREATE EXTENSION IF NOT EXISTS unaccent",),
            notes=("Some note",),
        )
        assert plan.statements == ("CREATE EXTENSION IF NOT EXISTS unaccent",)
        assert plan.notes == ("Some note",)

    def test_default_notes(self) -> None:
        """Notes should default to empty tuple."""
        plan = CollationPlan(statements=())
        assert plan.notes == ()

    def test_frozen(self) -> None:
        """Plan should be frozen."""
        plan = CollationPlan(statements=())
        with pytest.raises(Exception):
            plan.statements = ()  # type: ignore[misc]


class TestRecommendCollationPlan:
    """Test recommend_collation_plan function."""

    def test_postgresql(self) -> None:
        """Should return PostgreSQL plan."""
        plan = recommend_collation_plan("postgresql")
        assert plan is not None
        assert isinstance(plan, CollationPlan)
        assert len(plan.statements) > 0

    def test_sqlite(self) -> None:
        """Should return SQLite plan."""
        plan = recommend_collation_plan("sqlite")
        assert plan is not None
        assert isinstance(plan, CollationPlan)

    def test_unknown_returns_none(self) -> None:
        """Unknown dialect should return None."""
        plan = recommend_collation_plan("unknown_database")
        assert plan is None

    def test_mysql_returns_none(self) -> None:
        """MySQL not yet supported."""
        plan = recommend_collation_plan("mysql")
        assert plan is None

    def test_postgres_has_unaccent(self) -> None:
        """PostgreSQL plan should include unaccent extension."""
        plan = recommend_collation_plan("postgresql")
        assert plan is not None
        assert any("unaccent" in stmt for stmt in plan.statements)

    def test_sqlite_has_notes(self) -> None:
        """SQLite plan should have FTS5 notes."""
        plan = recommend_collation_plan("sqlite")
        assert plan is not None
        assert len(plan.notes) > 0
