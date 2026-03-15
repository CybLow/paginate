"""End-to-end tests for offset pagination workflows.

Verifies complete pagination through datasets using the
paginate() dispatch function with OffsetParams.
"""

from __future__ import annotations

import pytest

from pypaginate import OffsetPage, OffsetParams, OverflowStrategy, paginate


class TestPaginateThroughAllPages:
    """Iterate all pages and verify completeness."""

    def test_collect_all_items_across_pages(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """All 100 items appear exactly once across all pages."""
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            page = paginate(large_dataset, OffsetParams(page=page_num, limit=15))
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        assert len(collected) == 100
        assert {item["id"] for item in collected} == set(range(100))

    def test_page_counts_are_consistent(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Total and pages metadata stays constant across requests."""
        pages_seen: list[int] = []

        for p in range(1, 6):
            page = paginate(large_dataset, OffsetParams(page=p, limit=20))
            pages_seen.append(page.pages)

        assert all(p == 5 for p in pages_seen)


class TestEdgeCases:
    """Edge-case datasets for offset pagination."""

    def test_single_item_dataset(self) -> None:
        """One-item dataset yields one page with no navigation."""
        page = paginate([{"x": 1}], OffsetParams(page=1, limit=10))

        assert len(page.items) == 1
        assert page.has_next is False
        assert page.has_previous is False

    def test_dataset_size_equals_limit(self) -> None:
        """Dataset size == limit fills exactly one page."""
        data = [{"i": i} for i in range(10)]

        page = paginate(data, OffsetParams(page=1, limit=10))

        assert len(page.items) == 10
        assert page.pages == 1
        assert page.has_next is False

    def test_empty_dataset(self) -> None:
        """Empty dataset returns zero-item page."""
        page: OffsetPage[dict[str, object]] = paginate(
            [],
            OffsetParams(page=1, limit=10),
        )

        assert page.items == []
        assert page.total == 0
        assert page.pages == 0

    def test_overflow_clamp_returns_last_page(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """CLAMP overflow returns the last page for out-of-range request."""
        page = paginate(
            large_dataset,
            OffsetParams(page=999, limit=20),
            overflow=OverflowStrategy.CLAMP,
        )

        assert len(page.items) > 0
        assert page.page <= page.pages

    def test_overflow_empty_returns_no_items(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """EMPTY overflow returns empty page for out-of-range request."""
        page = paginate(
            large_dataset,
            OffsetParams(page=999, limit=20),
            overflow=OverflowStrategy.EMPTY,
        )

        assert page.items == []


class TestNavigationFlags:
    """Verify has_next / has_previous across page positions."""

    @pytest.mark.parametrize(
        ("page_num", "has_prev", "has_nxt"),
        [
            (1, False, True),
            (3, True, True),
            (5, True, False),
        ],
    )
    def test_navigation_at_position(
        self,
        large_dataset: list[dict[str, object]],
        page_num: int,
        has_prev: bool,
        has_nxt: bool,
    ) -> None:
        """Navigation flags match expected values per position."""
        page = paginate(large_dataset, OffsetParams(page=page_num, limit=20))

        assert page.has_previous is has_prev
        assert page.has_next is has_nxt
