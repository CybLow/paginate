"""Unit tests for in-memory offset pagination (slicing + derived metadata)."""

from __future__ import annotations

import pytest

from pypaginate import OffsetPage, OffsetParams, paginate


pytestmark = pytest.mark.unit


class TestSlicing:
    def test_first_page_slices_from_start(self) -> None:
        page = paginate(list(range(1, 26)), OffsetParams(page=1, limit=10))

        assert list(page) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_middle_page_uses_offset(self) -> None:
        page = paginate(list(range(1, 26)), OffsetParams(page=2, limit=10))

        assert list(page) == [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    def test_last_page_is_partial(self) -> None:
        page = paginate(list(range(1, 26)), OffsetParams(page=3, limit=10))

        assert list(page) == [21, 22, 23, 24, 25]

    def test_returns_offset_page_instance(self) -> None:
        page = paginate([1, 2], OffsetParams(page=1, limit=10))

        assert isinstance(page, OffsetPage)


class TestMetadata:
    def test_first_page_metadata(self) -> None:
        page = paginate(list(range(25)), OffsetParams(page=1, limit=10))

        assert page.total == 25
        assert page.pages == 3
        assert page.page == 1
        assert page.limit == 10
        assert page.has_next is True
        assert page.has_previous is False

    def test_middle_page_has_both_neighbours(self) -> None:
        page = paginate(list(range(25)), OffsetParams(page=2, limit=10))

        assert page.has_next is True
        assert page.has_previous is True

    def test_last_page_has_no_next(self) -> None:
        page = paginate(list(range(25)), OffsetParams(page=3, limit=10))

        assert page.has_next is False
        assert page.has_previous is True

    def test_single_page_dataset(self) -> None:
        page = paginate([1, 2, 3], OffsetParams(page=1, limit=10))

        assert page.pages == 1
        assert page.has_next is False
        assert page.has_previous is False


class TestEdgeCases:
    def test_empty_dataset(self) -> None:
        page = paginate([], OffsetParams(page=1, limit=10))

        assert list(page) == []
        assert page.total == 0
        assert page.pages == 0
        assert page.has_next is False
        assert page.has_previous is False

    def test_page_beyond_range_is_empty_but_keeps_total(self) -> None:
        page = paginate(list(range(25)), OffsetParams(page=99, limit=10))

        assert list(page) == []
        assert page.total == 25
        assert page.pages == 3
        assert page.has_next is False
        assert page.has_previous is True

    def test_accepts_any_sequence(self) -> None:
        page = paginate(("a", "b", "c"), OffsetParams(page=1, limit=2))

        assert list(page) == ["a", "b"]
        assert page.total == 3
