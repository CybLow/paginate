"""Tests for field accessor (get_value)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pypaginate.domain.exceptions import FilterError
from pypaginate.filtering.accessor import get_value


@dataclass
class _User:
    name: str
    age: int = 0


class TestDictAccess:
    def test_simple_key_returns_value(self) -> None:
        item = {"name": "Alice"}

        result = get_value(item, "name")

        assert result == "Alice"

    def test_integer_value_returns_value(self) -> None:
        item = {"age": 30}

        result = get_value(item, "age")

        assert result == 30


class TestObjectAccess:
    def test_attribute_returns_value(self) -> None:
        user = _User(name="Bob")

        result = get_value(user, "name")

        assert result == "Bob"


class TestNestedAccess:
    def test_nested_dict_path_returns_value(self) -> None:
        data = {"user": {"name": "Alice"}}

        result = get_value(data, "user.name")

        assert result == "Alice"

    def test_deep_nested_path_returns_value(self) -> None:
        data = {"a": {"b": {"c": 42}}}

        result = get_value(data, "a.b.c")

        assert result == 42


class TestMissingField:
    def test_missing_dict_key_raises_filter_error(self) -> None:
        with pytest.raises(FilterError, match="Cannot resolve"):
            get_value({"name": "Alice"}, "missing")

    def test_missing_nested_key_raises_filter_error(self) -> None:
        with pytest.raises(FilterError, match="Cannot resolve"):
            get_value({"user": {"name": "Alice"}}, "user.email")

    def test_missing_attribute_raises_filter_error(self) -> None:
        with pytest.raises(FilterError, match="Cannot resolve"):
            get_value(_User(name="Alice"), "email")


class TestEdgeCases:
    def test_none_field_value_returns_none(self) -> None:
        item = {"score": None}

        result = get_value(item, "score")

        assert result is None

    def test_empty_string_value_returns_empty(self) -> None:
        item = {"name": ""}

        result = get_value(item, "name")

        assert result == ""
