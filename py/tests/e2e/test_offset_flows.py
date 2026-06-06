"""End-to-end offset pagination flows over in-memory data.

Drives :func:`pypaginate.paginate` the way a caller would: walking every page to
completeness, inspecting the :class:`~pypaginate.OffsetPage` metadata on the
first/last page, and covering the edge shapes (single item, exact-limit match,
empty dataset, and an out-of-range overflow page).
"""

from __future__ import annotations

import math

import pytest
from tests.fixtures.helpers import ids_of

from pypaginate import OffsetParams, paginate


pytestmark = pytest.mark.e2e


def test_walk_all_pages_collects_every_row(big_users: list[dict[str, object]]) -> None:
    """Iterating until ``has_next`` is false yields exactly ``total`` rows once."""
    limit, collected, page_num = 7, [], 1
    while True:
        page = paginate(big_users, OffsetParams(page=page_num, limit=limit))
        collected.extend(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert len(collected) == len(big_users)
    assert ids_of(collected) == ids_of(big_users)


def test_no_duplicate_ids_across_pages(big_users: list[dict[str, object]]) -> None:
    """No row appears on two pages when walking the whole dataset."""
    limit, seen, page_num = 9, set(), 1
    while True:
        page = paginate(big_users, OffsetParams(page=page_num, limit=limit))
        for row in page:
            assert row["id"] not in seen
            seen.add(row["id"])
        if not page.has_next:
            break
        page_num += 1
    assert len(seen) == len(big_users)


def test_first_page_metadata(users: list[dict[str, object]]) -> None:
    """Page one has no previous, has a next, and reports the full total/pages."""
    page = paginate(users, OffsetParams(page=1, limit=10))
    assert page.page == 1
    assert page.total == 50
    assert page.pages == 5
    assert page.limit == 10
    assert page.has_next is True
    assert page.has_previous is False
    assert len(page) == 10


def test_last_page_metadata(users: list[dict[str, object]]) -> None:
    """The final page has a previous, no next, and the trailing rows."""
    page = paginate(users, OffsetParams(page=5, limit=10))
    assert page.has_next is False
    assert page.has_previous is True
    assert ids_of(page.items) == list(range(41, 51))


def test_ragged_last_page_has_remainder(users: list[dict[str, object]]) -> None:
    """A limit that does not divide the total leaves a short final page."""
    limit = 7
    last = math.ceil(len(users) / limit)
    page = paginate(users, OffsetParams(page=last, limit=limit))
    assert page.pages == last
    assert len(page) == len(users) - (last - 1) * limit
    assert page.has_next is False


def test_exact_limit_match_is_single_page(users: list[dict[str, object]]) -> None:
    """A limit equal to the total collapses to exactly one full page."""
    page = paginate(users, OffsetParams(page=1, limit=len(users)))
    assert page.pages == 1
    assert len(page) == len(users)
    assert page.has_next is False
    assert page.has_previous is False


def test_single_item_dataset() -> None:
    """One row produces a single page with no neighbours."""
    page = paginate([{"id": 1}], OffsetParams(page=1, limit=10))
    assert page.total == 1
    assert page.pages == 1
    assert len(page) == 1
    assert page.has_next is False
    assert page.has_previous is False


def test_empty_dataset() -> None:
    """An empty input yields zero rows, zero pages, and no neighbours."""
    page = paginate([], OffsetParams(page=1, limit=10))
    assert page.total == 0
    assert page.pages == 0
    assert list(page.items) == []
    assert page.has_next is False
    assert page.has_previous is False


def test_overflow_page_is_empty_but_keeps_request(users: list[dict[str, object]]) -> None:
    """Requesting past the last page returns no rows yet preserves the request."""
    page = paginate(users, OffsetParams(page=999, limit=10))
    assert list(page.items) == []
    assert page.page == 999
    assert page.pages == 5
    assert page.has_next is False
    assert page.has_previous is True


def test_offset_page_indexing(users: list[dict[str, object]]) -> None:
    """``OffsetPage`` supports ``len`` and positional indexing over its rows."""
    page = paginate(users, OffsetParams(page=2, limit=10))
    assert len(page) == 10
    assert page[0]["id"] == 11
    assert page[-1]["id"] == 20
