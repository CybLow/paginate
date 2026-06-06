"""Unit tests for the one-shot filter / sort / search query helpers."""

from __future__ import annotations

import pytest

from pypaginate import (
    And,
    FilterSpec,
    Or,
    SearchSpec,
    SortSpec,
    filter,
    search,
    sort,
)
from pypaginate.errors import FilterError, SortError


pytestmark = pytest.mark.unit


@pytest.mark.filters
class TestFilter:
    def test_single_spec(self, people: list[dict[str, object]]) -> None:
        result = filter(people, FilterSpec(field="age", operator="gte", value=30))

        assert [r["name"] for r in result] == ["Alice", "Carol"]

    def test_preserves_original_order(self, people: list[dict[str, object]]) -> None:
        result = filter(people, FilterSpec(field="age", operator="eq", value=25))

        assert [r["name"] for r in result] == ["bob", "Dave"]

    def test_list_of_specs_is_anded(self, people: list[dict[str, object]]) -> None:
        result = filter(
            people,
            [
                FilterSpec(field="age", operator="eq", value=25),
                FilterSpec(field="city", operator="eq", value="Paris"),
            ],
        )

        assert [r["name"] for r in result] == ["Dave"]

    def test_or_group(self, people: list[dict[str, object]]) -> None:
        group = Or(
            FilterSpec(field="age", operator="eq", value=40),
            FilterSpec(field="city", operator="eq", value="Lyon"),
        )

        result = filter(people, group)

        assert {r["name"] for r in result} == {"bob", "Carol"}

    def test_nested_and_or_group(self, people: list[dict[str, object]]) -> None:
        group = And(
            FilterSpec(field="age", operator="eq", value=25),
            Or(
                FilterSpec(field="city", operator="eq", value="Paris"),
                FilterSpec(field="city", operator="eq", value="Berlin"),
            ),
        )

        result = filter(people, group)

        assert [r["name"] for r in result] == ["Dave"]

    def test_not_in_operator(self, people: list[dict[str, object]]) -> None:
        result = filter(people, FilterSpec(field="city", operator="not_in", value=["Paris"]))

        assert {r["name"] for r in result} == {"bob", "Carol"}

    def test_reads_object_attributes(self, person_objects: list[object]) -> None:
        result = filter(person_objects, FilterSpec(field="age", operator="gte", value=30))

        assert [p.name for p in result] == ["Alice", "Carol"]  # type: ignore[attr-defined]

    def test_unknown_operator_raises_filter_error(self) -> None:
        with pytest.raises(FilterError, match="operator"):
            filter([{"a": 1}], FilterSpec(field="a", operator="bogus", value=1))


@pytest.mark.sorting
class TestSort:
    def test_single_key_ascending_by_default(self, people: list[dict[str, object]]) -> None:
        result = sort(people, SortSpec(field="age"))

        assert [r["age"] for r in result] == [25, 25, 30, 40]

    def test_descending(self, people: list[dict[str, object]]) -> None:
        result = sort(people, SortSpec(field="age", direction="desc"))

        assert [r["age"] for r in result] == [40, 30, 25, 25]

    def test_nulls_last_by_default(self) -> None:
        rows = [{"n": 3}, {"n": None}, {"n": 1}]

        result = sort(rows, SortSpec(field="n", direction="asc"))

        assert [r["n"] for r in result] == [1, 3, None]

    def test_nulls_first(self) -> None:
        rows = [{"n": 3}, {"n": None}, {"n": 1}]

        result = sort(rows, SortSpec(field="n", direction="asc", nulls="first"))

        assert [r["n"] for r in result] == [None, 1, 3]

    def test_multi_key_priority_order(self) -> None:
        rows = [
            {"a": 1, "b": 2},
            {"a": 1, "b": 1},
            {"a": 0, "b": 9},
        ]

        result = sort(rows, [SortSpec(field="a"), SortSpec(field="b")])

        assert result == [
            {"a": 0, "b": 9},
            {"a": 1, "b": 1},
            {"a": 1, "b": 2},
        ]

    def test_stable_for_equal_keys(self) -> None:
        rows = [{"k": 1, "id": "x"}, {"k": 1, "id": "y"}, {"k": 1, "id": "z"}]

        result = sort(rows, SortSpec(field="k"))

        assert [r["id"] for r in result] == ["x", "y", "z"]

    def test_incomparable_values_raise_sort_error(self) -> None:
        rows = [{"k": 1}, {"k": "text"}]

        with pytest.raises(SortError):
            sort(rows, SortSpec(field="k"))


@pytest.mark.search
class TestSearch:
    def test_field_weights_drive_relevance_order(self) -> None:
        rows = [
            {"title": "alice", "body": "filler"},
            {"title": "filler", "body": "alice"},
        ]

        weighted_title = search(
            rows,
            SearchSpec(
                query="alice",
                fields=["title", "body"],
                weights={"title": 5.0, "body": 1.0},
            ),
        )
        weighted_body = search(
            rows,
            SearchSpec(
                query="alice",
                fields=["title", "body"],
                weights={"title": 1.0, "body": 5.0},
            ),
        )

        assert weighted_title[0]["title"] == "alice"
        assert weighted_body[0]["body"] == "alice"

    def test_non_matches_are_excluded(self) -> None:
        rows = [{"name": "alice"}, {"name": "bob"}, {"name": "carol"}]

        result = search(rows, SearchSpec(query="alice", fields=["name"]))

        assert [r["name"] for r in result] == ["alice"]

    def test_is_case_insensitive(self) -> None:
        rows = [{"name": "ALICE"}]

        result = search(rows, SearchSpec(query="alice", fields=["name"]))

        assert [r["name"] for r in result] == ["ALICE"]

    def test_max_results_caps_output(self) -> None:
        rows = [{"t": f"alpha {i}"} for i in range(10)]

        result = search(rows, SearchSpec(query="alpha", fields=["t"], max_results=3))

        assert len(result) == 3

    def test_short_query_below_min_length_returns_all(self) -> None:
        rows = [{"name": "alice"}, {"name": "bob"}]

        result = search(rows, SearchSpec(query="al", fields=["name"], min_length=3))

        assert result == rows

    def test_fuzzy_matches_typos(self) -> None:
        rows = [{"name": "alice"}, {"name": "zzzz"}]

        result = search(
            rows,
            SearchSpec(query="alise", fields=["name"], fuzzy="fuzzy", threshold=40),
        )

        assert [r["name"] for r in result] == ["alice"]
