"""Tests for field accessor module."""

from __future__ import annotations

import pytest

from pypaginator.filters.predicates.field_accessor import FieldAccessor


class TestFieldAccessor:
    """Test FieldAccessor class."""

    def test_creation(self) -> None:
        """Should create accessor."""
        accessor = FieldAccessor.from_string("name")
        assert accessor is not None

    def test_resolve_dict(self) -> None:
        """Should resolve dict field."""
        accessor = FieldAccessor.from_string("name")
        result = accessor.resolve({"name": "John"})
        assert result == "John"

    def test_resolve_nested_dict(self) -> None:
        """Should resolve nested dict field."""
        accessor = FieldAccessor.from_string("user.name")
        result = accessor.resolve({"user": {"name": "John"}})
        assert result == "John"

    def test_missing_field_returns_none(self) -> None:
        """Missing field should return None."""
        accessor = FieldAccessor.from_string("missing")
        result = accessor.resolve({"name": "John"})
        assert result is None

    def test_deeply_nested(self) -> None:
        """Should resolve deeply nested fields."""
        accessor = FieldAccessor.from_string("a.b.c")
        result = accessor.resolve({"a": {"b": {"c": "value"}}})
        assert result == "value"

    def test_from_string_simple(self) -> None:
        """from_string should work with simple field."""
        accessor = FieldAccessor.from_string("id")
        result = accessor.resolve({"id": 123})
        assert result == 123

    def test_from_string_nested(self) -> None:
        """from_string should work with nested path."""
        accessor = FieldAccessor.from_string("user.profile.age")
        data = {"user": {"profile": {"age": 30}}}
        result = accessor.resolve(data)
        assert result == 30

    def test_none_input(self) -> None:
        """Should handle None input."""
        accessor = FieldAccessor.from_string("name")
        result = accessor.resolve(None)
        assert result is None

    def test_int_value(self) -> None:
        """Should resolve int value."""
        accessor = FieldAccessor.from_string("count")
        result = accessor.resolve({"count": 42})
        assert result == 42

    def test_bool_value(self) -> None:
        """Should resolve bool value."""
        accessor = FieldAccessor.from_string("active")
        result = accessor.resolve({"active": True})
        assert result is True
