"""Property-based tests for sort invariants.

Verifies that sorting preserves item count, maintains ordering
invariants for ASC/DESC, and is idempotent.
"""

from __future__ import annotations

from hypothesis import given

from pypaginate import SortDirection, SortSpec
from pypaginate.sorting.engine import SortEngine

from .strategies import sortable_datasets


@given(data=sortable_datasets(min_size=0, max_size=100))
def test_sort_preserves_count(data):
    """Sorting never adds or removes items."""
    engine = SortEngine()
    spec = SortSpec(field="value", direction=SortDirection.ASC)
    result = engine.apply(data, [spec])
    assert len(result) == len(data)


@given(data=sortable_datasets(min_size=2, max_size=100))
def test_asc_sort_ordering(data):
    """ASC sort: each item's value >= previous item's value."""
    engine = SortEngine()
    spec = SortSpec(field="value", direction=SortDirection.ASC)
    result = engine.apply(data, [spec])
    for i in range(1, len(result)):
        assert result[i]["value"] >= result[i - 1]["value"]


@given(data=sortable_datasets(min_size=2, max_size=100))
def test_desc_sort_ordering(data):
    """DESC sort: each item's value <= previous item's value."""
    engine = SortEngine()
    spec = SortSpec(field="value", direction=SortDirection.DESC)
    result = engine.apply(data, [spec])
    for i in range(1, len(result)):
        assert result[i]["value"] <= result[i - 1]["value"]


@given(data=sortable_datasets(min_size=0, max_size=100))
def test_sort_is_idempotent(data):
    """Sorting already-sorted data produces the same result."""
    engine = SortEngine()
    spec = SortSpec(field="value", direction=SortDirection.ASC)
    first = engine.apply(data, [spec])
    second = engine.apply(first, [spec])
    assert first == second


@given(data=sortable_datasets(min_size=0, max_size=50))
def test_empty_sort_specs_return_copy(data):
    """No sort specs returns all items unchanged."""
    engine = SortEngine()
    result = engine.apply(data, [])
    assert result == list(data)
