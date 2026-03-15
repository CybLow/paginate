"""Property-based tests for pagination invariants.

Verifies structural properties of offset pagination that must hold
for all valid inputs: totals, coverage, navigation, clamping, and
empty-data handling.
"""

from __future__ import annotations

import math

from hypothesis import given

from pypaginate import OffsetParams, paginate

from .strategies import datasets, offset_params


@given(data=datasets(min_size=0, max_size=200), params=offset_params())
def test_total_equals_data_length(data, params):
    """Total always equals the original data length."""
    page = paginate(data, params)
    assert page.total == len(data)


@given(data=datasets(min_size=1, max_size=100))
def test_all_items_returned_across_pages(data):
    """Summing items across all pages equals total."""
    limit = max(1, len(data) // 3)
    total_pages = math.ceil(len(data) / limit)
    collected = []
    for p in range(1, total_pages + 1):
        page = paginate(data, OffsetParams(page=p, limit=limit))
        collected.extend(page.items)
    assert len(collected) == len(data)


@given(data=datasets(min_size=1, max_size=100), params=offset_params())
def test_has_next_navigation_consistency(data, params):
    """has_next is True iff current page < total pages."""
    page = paginate(data, params)
    expected = page.page < page.pages
    assert page.has_next == expected


@given(data=datasets(min_size=0, max_size=200), params=offset_params())
def test_clamp_never_exceeds_bounds(data, params):
    """Clamped page never exceeds ceil(total / limit)."""
    total = len(data)
    clamped = params.clamp(total)
    if total == 0:
        assert clamped.page == 1
    else:
        max_page = math.ceil(total / clamped.limit)
        assert clamped.page <= max_page


@given(params=offset_params())
def test_empty_data_always_empty_page(params):
    """Paginating empty data always returns empty items."""
    page = paginate([], params)
    assert page.items == []
    assert page.total == 0


@given(data=datasets(min_size=1, max_size=100), params=offset_params())
def test_page_items_are_contiguous_slice(data, params):
    """Page items are a contiguous slice of the original data."""
    page = paginate(data, params)
    if not page.items:
        return
    offset = (params.page - 1) * params.limit
    expected = data[offset : offset + params.limit]
    assert page.items == expected


@given(data=datasets(min_size=0, max_size=100), params=offset_params())
def test_page_size_never_exceeds_limit(data, params):
    """No page ever returns more items than the limit."""
    page = paginate(data, params)
    assert len(page.items) <= params.limit


@given(data=datasets(min_size=1, max_size=50))
def test_has_previous_false_on_first_page(data):
    """First page never has previous."""
    page = paginate(data, OffsetParams(page=1, limit=10))
    assert page.has_previous is False
