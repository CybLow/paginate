"""Property-based filter invariant: the result is an order-preserving subset.

Filtering may only drop rows -- never add, reorder, or mutate them. Each item
carries a unique ``id`` equal to its input position, so a correct filter yields
items whose ids form a strictly increasing subsequence of ``range(n)`` and whose
contents are unchanged from the input.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from pypaginate import FilterSpec, filter as filter_items


pytestmark = pytest.mark.property


_NUMERIC_OPS = ("eq", "ne", "gt", "gte", "lt", "lte")


@st.composite
def _rows(draw: st.DrawFn) -> list[dict[str, int]]:
    """Rows with a unique positional ``id`` and a small (dup-prone) ``age``."""
    ages = draw(st.lists(st.integers(min_value=0, max_value=9), max_size=60))
    return [{"id": i, "age": age} for i, age in enumerate(ages)]


@given(rows=_rows(), operator=st.sampled_from(_NUMERIC_OPS), value=st.integers(0, 9))
def test_result_is_strictly_increasing_subsequence(
    rows: list[dict[str, int]], operator: str, value: int
) -> None:
    # Act
    result = filter_items(rows, FilterSpec(field="age", operator=operator, value=value))

    # Assert
    ids = [row["id"] for row in result]
    assert ids == sorted(set(ids))
    assert all(0 <= i < len(rows) for i in ids)


@given(rows=_rows(), operator=st.sampled_from(_NUMERIC_OPS), value=st.integers(0, 9))
def test_result_items_are_unmodified_inputs(
    rows: list[dict[str, int]], operator: str, value: int
) -> None:
    # Act
    result = filter_items(rows, FilterSpec(field="age", operator=operator, value=value))

    # Assert
    assert all(row is rows[row["id"]] for row in result)


@given(rows=_rows())
def test_empty_filter_list_keeps_every_row(rows: list[dict[str, int]]) -> None:
    # Act
    result = filter_items(rows, [])

    # Assert
    assert result == rows
