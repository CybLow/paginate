"""Property-based offset-pagination invariants.

For any 1-based ``page``, ``limit`` in [1, MAX_LIMIT], and ``total`` >= 0 the
derived metadata must satisfy: ``pages == ceil(total / limit)`` (0 when empty),
``0 <= len(items) <= limit``, ``has_previous == (page > 1)``, and
``has_next == (page < pages)`` -- and the page's items must be exactly the
corresponding native slice of the input.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given, strategies as st

from pypaginate import MAX_LIMIT, OffsetParams, paginate


pytestmark = pytest.mark.property


_pages = st.integers(min_value=1, max_value=40)
_limits = st.integers(min_value=1, max_value=MAX_LIMIT)
_totals = st.integers(min_value=0, max_value=250)


@given(total=_totals, page=_pages, limit=_limits)
def test_pages_equals_ceil_total_over_limit(total: int, page: int, limit: int) -> None:
    # Arrange
    items = list(range(total))

    # Act
    result = paginate(items, OffsetParams(page=page, limit=limit))

    # Assert
    expected = 0 if total == 0 else math.ceil(total / limit)
    assert result.pages == expected
    assert result.total == total


@given(total=_totals, page=_pages, limit=_limits)
def test_item_count_within_limit(total: int, page: int, limit: int) -> None:
    # Arrange
    items = list(range(total))

    # Act
    result = paginate(items, OffsetParams(page=page, limit=limit))

    # Assert
    assert 0 <= len(result) <= limit


@given(total=_totals, page=_pages, limit=_limits)
def test_has_previous_and_has_next_flags(total: int, page: int, limit: int) -> None:
    # Arrange
    items = list(range(total))

    # Act
    result = paginate(items, OffsetParams(page=page, limit=limit))

    # Assert
    assert result.has_previous == (result.page > 1)
    assert result.has_next == (result.page < result.pages)


@given(total=_totals, page=_pages, limit=_limits)
def test_items_are_the_native_slice(total: int, page: int, limit: int) -> None:
    # Arrange
    items = list(range(total))
    params = OffsetParams(page=page, limit=limit)

    # Act
    result = paginate(items, params)

    # Assert
    start = params.offset
    assert list(result) == items[start : start + limit]
