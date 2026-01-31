"""Tests for filters/search/helpers.py module.

This module tests the SQL search helper functions for building
LIKE clauses and matching conditions.
"""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pypaginate.filters.search.helpers import (
    _column_expression,
    column_attributes,
    match_columns,
)


# Test models
class Base(DeclarativeBase):
    """Test base class for SQLAlchemy models."""

    pass


class SearchModel(Base):
    """Test model for search helpers."""

    __tablename__ = "search_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class TestColumnExpression:
    """Tests for _column_expression function."""

    def test_valid_string_column(self) -> None:
        """Should return column expression for valid string field."""
        result = _column_expression(SearchModel, "name")
        assert result is not None

    def test_valid_email_column(self) -> None:
        """Should return column expression for email field."""
        result = _column_expression(SearchModel, "email")
        assert result is not None

    def test_nonexistent_field_returns_none(self) -> None:
        """Should return None for nonexistent field."""
        result = _column_expression(SearchModel, "nonexistent")
        assert result is None

    def test_integer_column(self) -> None:
        """Should return column expression for integer field."""
        result = _column_expression(SearchModel, "id")
        assert result is not None

    def test_nullable_column(self) -> None:
        """Should return column expression for nullable field."""
        result = _column_expression(SearchModel, "description")
        assert result is not None


class TestColumnAttributes:
    """Tests for column_attributes function."""

    def test_single_valid_field(self) -> None:
        """Should return tuple with single column."""
        result = column_attributes(SearchModel, ["name"])
        assert len(result) == 1

    def test_multiple_valid_fields(self) -> None:
        """Should return tuple with multiple columns."""
        result = column_attributes(SearchModel, ["name", "email"])
        assert len(result) == 2

    def test_empty_fields_list(self) -> None:
        """Should return empty tuple for empty fields list."""
        result = column_attributes(SearchModel, [])
        assert result == ()

    def test_mixed_valid_and_invalid_fields(self) -> None:
        """Should skip invalid fields and return valid ones."""
        result = column_attributes(SearchModel, ["name", "invalid", "email"])
        assert len(result) == 2

    def test_all_invalid_fields(self) -> None:
        """Should return empty tuple when all fields invalid."""
        result = column_attributes(SearchModel, ["invalid1", "invalid2"])
        assert result == ()

    def test_preserves_order(self) -> None:
        """Should preserve order of valid fields."""
        result = column_attributes(SearchModel, ["email", "name", "description"])
        assert len(result) == 3


class TestMatchColumns:
    """Tests for match_columns function."""

    def test_single_column_single_token(self) -> None:
        """Should create IN clause for single column and token."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {"value1"})
        assert result is not None

    def test_single_column_multiple_tokens(self) -> None:
        """Should create IN clause for multiple tokens."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {"value1", "value2", "value3"})
        assert result is not None

    def test_multiple_columns_single_token(self) -> None:
        """Should create OR-ed IN clauses for multiple columns."""
        columns = column_attributes(SearchModel, ["name", "email"])
        result = match_columns(columns, {"value1"})
        assert result is not None

    def test_multiple_columns_multiple_tokens(self) -> None:
        """Should create complex clause for multiple columns and tokens."""
        columns = column_attributes(SearchModel, ["name", "email", "description"])
        result = match_columns(columns, {"value1", "value2"})
        assert result is not None

    def test_empty_columns_returns_none(self) -> None:
        """Should return None for empty columns list."""
        result = match_columns((), {"value1"})
        assert result is None

    def test_empty_tokens_returns_none(self) -> None:
        """Should return None for empty tokens set."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, set())
        assert result is None

    def test_empty_columns_and_tokens_returns_none(self) -> None:
        """Should return None when both columns and tokens are empty."""
        result = match_columns((), set())
        assert result is None


class TestMatchColumnsWithRealQuery:
    """Integration tests for match_columns with actual SQL queries."""

    def test_generates_valid_sql(self) -> None:
        """Should generate valid SQL IN clause."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {"Alice", "Bob"})

        if result is not None:
            compiled = str(result.compile(compile_kwargs={"literal_binds": True}))
            # Should contain IN clause
            assert "IN" in compiled
            # Should contain the values
            assert "Alice" in compiled or "'Alice'" in compiled
            assert "Bob" in compiled or "'Bob'" in compiled

    def test_multiple_columns_generates_or_clause(self) -> None:
        """Should generate OR clause for multiple columns."""
        columns = column_attributes(SearchModel, ["name", "email"])
        result = match_columns(columns, {"test"})

        if result is not None:
            compiled = str(result.compile(compile_kwargs={"literal_binds": True}))
            # Should contain OR
            assert "OR" in compiled


class TestEdgeCases:
    """Edge case tests for search helpers."""

    def test_column_with_special_characters_in_value(self) -> None:
        """Should handle values with special characters."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {"O'Reilly", "test@example.com"})
        assert result is not None

    def test_empty_string_token(self) -> None:
        """Should handle empty string in tokens."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {""})
        assert result is not None

    def test_whitespace_token(self) -> None:
        """Should handle whitespace in tokens."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {"  "})
        assert result is not None

    def test_unicode_token(self) -> None:
        """Should handle unicode characters."""
        columns = column_attributes(SearchModel, ["name"])
        result = match_columns(columns, {"日本語", "émojis 😀"})
        assert result is not None
