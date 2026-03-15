"""Tests for OffsetPage and CursorPage domain models."""

from __future__ import annotations

import pytest

from pypaginate.domain.pages import CursorPage, OffsetPage
from pypaginate.domain.params import CursorParams, OffsetParams


class TestOffsetPageCreate:
    def test_total_and_page_set_correctly(self) -> None:
        params = OffsetParams(page=1, limit=5)

        page = OffsetPage.create(["a", "b", "c"], total=12, params=params)

        assert page.total == 12
        assert page.page == 1

    def test_has_next_when_more_pages_exist(self) -> None:
        params = OffsetParams(page=1, limit=5)

        page = OffsetPage.create(["a"] * 5, total=10, params=params)

        assert page.has_next is True

    def test_no_previous_on_first_page(self) -> None:
        params = OffsetParams(page=1, limit=5)

        page = OffsetPage.create(["a"] * 5, total=10, params=params)

        assert page.has_previous is False

    def test_has_previous_on_second_page(self) -> None:
        params = OffsetParams(page=2, limit=5)

        page = OffsetPage.create(["a"] * 5, total=10, params=params)

        assert page.has_previous is True

    def test_no_next_on_last_page(self) -> None:
        params = OffsetParams(page=2, limit=5)

        page = OffsetPage.create(["a"] * 5, total=10, params=params)

        assert page.has_next is False


class TestOffsetPagePages:
    @pytest.mark.parametrize(
        ("total", "limit", "expected_pages"),
        [
            (12, 5, 3),
            (10, 5, 2),
            (1, 5, 1),
            (0, 5, 0),
            (5, 5, 1),
        ],
        ids=["partial", "exact", "single_item", "empty", "exact_one"],
    )
    def test_pages_computed_correctly(
        self,
        total: int,
        limit: int,
        expected_pages: int,
    ) -> None:
        items = ["a"] * min(total, limit)
        params = OffsetParams(page=1, limit=limit)

        page = OffsetPage.create(items, total=total, params=params)

        assert page.pages == expected_pages


class TestOffsetPageSerialization:
    def test_no_cursor_fields_in_dict(self) -> None:
        params = OffsetParams(page=1, limit=5)
        page = OffsetPage.create(["a"], total=1, params=params)

        data = page.model_dump()

        assert "next_cursor" not in data
        assert "previous_cursor" not in data


class TestCursorPageCreate:
    def test_has_next_when_cursor_provided(self) -> None:
        params = CursorParams(limit=5)

        page = CursorPage.create(["a"] * 5, params, next_cursor="abc")

        assert page.has_next is True
        assert page.next_cursor == "abc"

    def test_no_next_without_cursor(self) -> None:
        params = CursorParams(limit=5)

        page = CursorPage.create(["a"] * 5, params)

        assert page.has_next is False
        assert page.next_cursor is None

    def test_has_previous_with_cursor(self) -> None:
        params = CursorParams(limit=5, after="prev")

        page = CursorPage.create(["a"] * 5, params, previous_cursor="xyz")

        assert page.has_previous is True


class TestCursorPageSerialization:
    def test_no_offset_fields_in_dict(self) -> None:
        params = CursorParams(limit=5)
        page = CursorPage.create(["a"], params)

        data = page.model_dump()

        assert "total" not in data
        assert "page" not in data


class TestEmptyPage:
    def test_empty_offset_page_has_no_navigation(self) -> None:
        params = OffsetParams(page=1, limit=10)

        page = OffsetPage.create([], total=0, params=params)

        assert page.items == []
        assert page.total == 0
        assert page.has_next is False
        assert page.has_previous is False

    def test_empty_cursor_page_has_no_navigation(self) -> None:
        params = CursorParams(limit=10)

        page = CursorPage.create([], params)

        assert page.items == []
        assert page.has_next is False
        assert page.has_previous is False
