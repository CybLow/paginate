"""Property-based sort invariants: a stable permutation of the input.

A sort must return every input row exactly once (a permutation) ordered by the
key, breaking ties by original position (stability). Both guarantees are pinned
at once by comparing against Python's stable :func:`sorted` (``reverse=True``
for descending), which the native engine must reproduce row-for-row.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from pypaginate import SortSpec, sort as sort_items


pytestmark = pytest.mark.property


@st.composite
def _rows(draw: st.DrawFn) -> list[dict[str, int]]:
    """Rows with a unique positional ``id`` and a dup-prone integer ``key``."""
    keys = draw(st.lists(st.integers(min_value=-5, max_value=5), max_size=60))
    return [{"id": i, "key": key} for i, key in enumerate(keys)]


@given(rows=_rows(), direction=st.sampled_from(("asc", "desc")))
def test_result_is_a_permutation_of_input(rows: list[dict[str, int]], direction: str) -> None:
    # Act
    result = sort_items(rows, SortSpec(field="key", direction=direction))

    # Assert
    assert sorted(row["id"] for row in result) == list(range(len(rows)))


@given(rows=_rows(), direction=st.sampled_from(("asc", "desc")))
def test_result_is_key_ordered(rows: list[dict[str, int]], direction: str) -> None:
    # Act
    result = sort_items(rows, SortSpec(field="key", direction=direction))

    # Assert
    keys = [row["key"] for row in result]
    expected = sorted(keys, reverse=(direction == "desc"))
    assert keys == expected


@given(rows=_rows(), direction=st.sampled_from(("asc", "desc")))
def test_ties_break_by_original_position(rows: list[dict[str, int]], direction: str) -> None:
    # Act
    result = sort_items(rows, SortSpec(field="key", direction=direction))

    # Assert
    expected = sorted(rows, key=lambda r: r["key"], reverse=(direction == "desc"))
    assert [row["id"] for row in result] == [row["id"] for row in expected]
