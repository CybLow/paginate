"""Tests for the top-level one-shot query helpers (``search`` / ``filter`` / ``sort``).

These are the ergonomic, item-returning wrappers over the native engine; the
strict-token tests pin the fail-fast behavior at the ``_core`` boundary (an
unknown enum token raises instead of silently defaulting).
"""

from __future__ import annotations

import pytest

from pypaginate import (
    And,
    FilterSpec,
    Or,
    SearchSpec,
    SortDirection,
    SortSpec,
    _core,
    filter as pp_filter,
    search,
    sort,
)


USERS = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Alicia", "age": 40},
]


class TestFilter:
    def test_single_spec(self) -> None:
        result = pp_filter(USERS, FilterSpec(field="age", operator="gte", value=30))
        assert [u["name"] for u in result] == ["Alice", "Alicia"]

    def test_list_of_specs_anded(self) -> None:
        result = pp_filter(
            USERS,
            [
                FilterSpec(field="age", operator="gte", value=26),
                FilterSpec(field="age", operator="lt", value=40),
            ],
        )
        assert [u["name"] for u in result] == ["Alice"]

    def test_filter_group(self) -> None:
        group = And(
            Or(
                FilterSpec(field="name", operator="eq", value="Alice"),
                FilterSpec(field="name", operator="eq", value="Alicia"),
            ),
            FilterSpec(field="age", operator="gte", value=35),
        )
        result = pp_filter(USERS, group)
        assert [u["name"] for u in result] == ["Alicia"]

    def test_preserves_original_order(self) -> None:
        result = pp_filter(USERS, FilterSpec(field="age", operator="gte", value=0))
        assert result == USERS


class TestSort:
    def test_single_key_desc(self) -> None:
        result = sort(USERS, SortSpec(field="age", direction=SortDirection.DESC))
        assert [u["name"] for u in result] == ["Alicia", "Alice", "Bob"]

    def test_list_is_stable(self) -> None:
        data = [{"g": 1, "id": 2}, {"g": 1, "id": 1}, {"g": 0, "id": 9}]
        result = sort(data, [SortSpec(field="g"), SortSpec(field="id")])
        assert [d["id"] for d in result] == [9, 1, 2]


class TestSearch:
    def test_ranked_contains(self) -> None:
        result = search(USERS, SearchSpec(query="ali", fields=("name",)))
        assert [u["name"] for u in result] == ["Alice", "Alicia"]

    def test_returns_items_not_indices(self) -> None:
        result = search(USERS, SearchSpec(query="bob", fields=("name",)))
        assert result == [{"name": "Bob", "age": 25}]


class TestStrictTokenAtBoundary:
    """The typed public API can't pass a bad token (the enums guard it), but the
    raw ``_core`` binding now fails fast rather than silently defaulting."""

    def test_invalid_search_mode_raises(self) -> None:
        # _core.SearchError subclasses ValueError, so this catches the typed raise.
        with pytest.raises(ValueError):
            _core.search_indices(USERS, "ali", ["name"], mode="bogus")

    def test_invalid_sort_direction_raises(self) -> None:
        with pytest.raises(ValueError):
            _core.sort_indices(USERS, [("age", "upward", "last")])

    def test_invalid_filter_logic_raises(self) -> None:
        with pytest.raises(ValueError):
            _core.filter_indices(USERS, [("age", "eq", 30, "nand")])
