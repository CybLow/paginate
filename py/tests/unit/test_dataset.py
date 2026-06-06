"""Unit tests for the resident in-memory Dataset (marshal once, query many)."""

from __future__ import annotations

import pytest

from pypaginate import (
    Dataset,
    FilterSpec,
    OffsetParams,
    SearchSpec,
    SortSpec,
)
from pypaginate.errors import FilterError, SearchError, SortError


pytestmark = pytest.mark.unit


@pytest.fixture
def dataset(people: list[dict[str, object]]) -> Dataset[dict[str, object]]:
    return Dataset(people)


class TestConstruction:
    def test_len_reports_item_count(self, dataset: Dataset[dict[str, object]]) -> None:
        assert len(dataset) == 4

    def test_repr_mentions_item_count(self, dataset: Dataset[dict[str, object]]) -> None:
        assert repr(dataset) == "Dataset(4 items)"


class TestFilter:
    def test_filter_returns_matching_rows(self, dataset: Dataset[dict[str, object]]) -> None:
        result = dataset.filter([FilterSpec(field="age", operator="gte", value=30)])

        assert [r["name"] for r in result] == ["Alice", "Carol"]

    def test_unknown_operator_raises_filter_error(
        self, dataset: Dataset[dict[str, object]]
    ) -> None:
        with pytest.raises(FilterError):
            dataset.filter([FilterSpec(field="age", operator="bogus", value=1)])


class TestSort:
    def test_sort_orders_rows(self, dataset: Dataset[dict[str, object]]) -> None:
        result = dataset.sort([SortSpec(field="age", direction="desc")])

        assert [r["age"] for r in result] == [40, 30, 25, 25]

    def test_incomparable_values_raise_sort_error(self) -> None:
        dataset: Dataset[dict[str, object]] = Dataset([{"k": 1}, {"k": "x"}])

        with pytest.raises(SortError):
            dataset.sort([SortSpec(field="k")])


class TestSearch:
    def test_search_returns_matches(self, dataset: Dataset[dict[str, object]]) -> None:
        result = dataset.search(SearchSpec(query="alice", fields=["name"]))

        assert [r["name"] for r in result] == ["Alice"]

    def test_missing_field_yields_no_matches(self, dataset: Dataset[dict[str, object]]) -> None:
        assert dataset.search(SearchSpec(query="x", fields=["nope"])) == []

    def test_unknown_mode_raises_search_error(self, dataset: Dataset[dict[str, object]]) -> None:
        with pytest.raises(SearchError):
            dataset.search(SearchSpec(query="x", fields=["name"], mode="bogus"))


class TestPage:
    def test_page_combines_filter_sort_and_pagination(
        self, dataset: Dataset[dict[str, object]]
    ) -> None:
        page = dataset.page(
            OffsetParams(page=1, limit=2),
            filters=[FilterSpec(field="age", operator="eq", value=25)],
            sorting=[SortSpec(field="name", direction="asc")],
        )

        assert [r["name"] for r in page] == ["Dave", "bob"]
        assert page.total == 2
        assert page.pages == 1
        assert page.has_next is False

    def test_page_without_clauses_paginates_everything(
        self, dataset: Dataset[dict[str, object]]
    ) -> None:
        page = dataset.page(OffsetParams(page=1, limit=2))

        assert page.total == 4
        assert page.pages == 2
        assert len(page) == 2

    def test_page_with_search_clause(self, dataset: Dataset[dict[str, object]]) -> None:
        page = dataset.page(
            OffsetParams(page=1, limit=10),
            search=SearchSpec(query="paris", fields=["city"]),
        )

        assert {r["name"] for r in page} == {"Alice", "Dave"}
        assert page.total == 2
