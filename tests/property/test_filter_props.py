"""Property-based tests for filter invariants.

Verifies that filtering never adds items, that eq/gte operators
produce correct results, and that filtering is idempotent.
"""

from __future__ import annotations

from hypothesis import given

from pypaginate import FilterSpec
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry

from .strategies import datasets, eq_filter_specs, gte_filter_specs


def _make_engine() -> FilterEngine:
    return FilterEngine(create_default_registry())


@given(data=datasets(min_size=0, max_size=100), spec=eq_filter_specs())
def test_filter_never_adds_items(data, spec):
    """Filtered result is never larger than input."""
    engine = _make_engine()
    result = engine.apply(data, [spec])
    assert len(result) <= len(data)


@given(data=datasets(min_size=1, max_size=100), spec=eq_filter_specs())
def test_eq_filter_all_results_match(data, spec):
    """Every item in eq-filtered results has field == value."""
    engine = _make_engine()
    result = engine.apply(data, [spec])
    for item in result:
        assert item["value"] == spec.value


@given(data=datasets(min_size=1, max_size=100), spec=gte_filter_specs())
def test_gte_filter_all_results_satisfy(data, spec):
    """Every item in gte-filtered results has field >= value."""
    engine = _make_engine()
    result = engine.apply(data, [spec])
    for item in result:
        assert item["value"] >= spec.value


@given(data=datasets(min_size=0, max_size=100), spec=eq_filter_specs())
def test_filter_is_idempotent(data, spec):
    """Filtering the same data twice yields the same result."""
    engine = _make_engine()
    first = engine.apply(data, [spec])
    second = engine.apply(first, [spec])
    assert first == second


@given(data=datasets(min_size=0, max_size=50))
def test_empty_filters_return_all(data):
    """No filters applied returns all items."""
    engine = _make_engine()
    result = engine.apply(data, [])
    assert result == list(data)


@given(data=datasets(min_size=1, max_size=50))
def test_lt_filter_excludes_gte(data):
    """Items filtered by lt(0) all have value < 0."""
    engine = _make_engine()
    spec = FilterSpec(field="value", operator="lt", value=0)
    result = engine.apply(data, [spec])
    for item in result:
        assert item["value"] < 0
