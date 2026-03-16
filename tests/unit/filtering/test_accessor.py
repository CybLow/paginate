"""Tests for compiled field accessor."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pypaginate.domain.exceptions import FilterError
from pypaginate.filtering.accessor import compile_accessor


@dataclass
class _User:
    name: str
    age: int = 0


class TestSingleSegmentDict:
    def test_simple_key_returns_value(self) -> None:
        accessor = compile_accessor("name")

        assert accessor({"name": "Alice"}) == "Alice"

    def test_integer_value_returns_value(self) -> None:
        accessor = compile_accessor("age")

        assert accessor({"age": 30}) == 30


class TestSingleSegmentObject:
    def test_attribute_returns_value(self) -> None:
        accessor = compile_accessor("name")

        assert accessor(_User(name="Bob")) == "Bob"


class TestMultiSegmentDict:
    def test_nested_dict_path_returns_value(self) -> None:
        accessor = compile_accessor("user.name")

        assert accessor({"user": {"name": "Alice"}}) == "Alice"

    def test_deep_nested_path_returns_value(self) -> None:
        accessor = compile_accessor("a.b.c")

        assert accessor({"a": {"b": {"c": 42}}}) == 42


class TestMissingField:
    def test_missing_dict_key_raises_filter_error(self) -> None:
        accessor = compile_accessor("missing")

        with pytest.raises(FilterError, match="Cannot resolve"):
            accessor({"name": "Alice"})

    def test_missing_nested_key_raises_filter_error(self) -> None:
        accessor = compile_accessor("user.email")

        with pytest.raises(FilterError, match="Cannot resolve"):
            accessor({"user": {"name": "Alice"}})

    def test_missing_attribute_raises_filter_error(self) -> None:
        accessor = compile_accessor("email")

        with pytest.raises(FilterError, match="Cannot resolve"):
            accessor(_User(name="Alice"))


class TestEdgeCases:
    def test_none_field_value_returns_none(self) -> None:
        accessor = compile_accessor("score")

        assert accessor({"score": None}) is None

    def test_empty_string_value_returns_empty(self) -> None:
        accessor = compile_accessor("name")

        assert accessor({"name": ""}) == ""


class TestReusability:
    def test_compiled_accessor_reusable_across_items(self) -> None:
        accessor = compile_accessor("age")
        items = [{"age": 10}, {"age": 20}, {"age": 30}]

        results = [accessor(item) for item in items]

        assert results == [10, 20, 30]

    def test_compiled_multi_reusable_across_items(self) -> None:
        accessor = compile_accessor("profile.score")
        items = [
            {"profile": {"score": 80}},
            {"profile": {"score": 90}},
        ]

        results = [accessor(item) for item in items]

        assert results == [80, 90]

    def test_nested_none_value_returned(self) -> None:
        accessor = compile_accessor("user.score")

        assert accessor({"user": {"score": None}}) is None
