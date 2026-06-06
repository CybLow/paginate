"""Unit tests for the OffsetPage / CursorPage generic containers."""

from __future__ import annotations

import pytest

from pypaginate import CursorPage, OffsetPage


pytestmark = pytest.mark.unit


def _offset_page() -> OffsetPage[str]:
    return OffsetPage(
        items=["a", "b", "c"],
        total=9,
        page=1,
        pages=3,
        limit=3,
        has_next=True,
        has_previous=False,
    )


def _cursor_page() -> CursorPage[int]:
    return CursorPage(
        items=[1, 2, 3],
        limit=3,
        has_next=True,
        has_previous=False,
        next_cursor="next",
    )


class TestOffsetPage:
    def test_fields(self) -> None:
        page = _offset_page()

        assert page.items == ["a", "b", "c"]
        assert page.total == 9
        assert page.page == 1
        assert page.pages == 3
        assert page.limit == 3
        assert page.has_next is True
        assert page.has_previous is False

    def test_len_counts_items(self) -> None:
        assert len(_offset_page()) == 3

    def test_iteration_yields_items_in_order(self) -> None:
        assert list(_offset_page()) == ["a", "b", "c"]

    def test_indexing_returns_item(self) -> None:
        page = _offset_page()

        assert page[0] == "a"
        assert page[-1] == "c"


class TestCursorPage:
    def test_fields_with_cursor_defaults(self) -> None:
        page = _cursor_page()

        assert page.items == [1, 2, 3]
        assert page.limit == 3
        assert page.has_next is True
        assert page.has_previous is False
        assert page.next_cursor == "next"
        assert page.previous_cursor is None

    def test_len_iter_index(self) -> None:
        page = _cursor_page()

        assert len(page) == 3
        assert list(page) == [1, 2, 3]
        assert page[1] == 2
