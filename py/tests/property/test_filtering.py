"""Property-based filtering invariants.

Verifies algebraic properties of the filter engine:
filter never adds, eq results match, idempotent.
"""

from __future__ import annotations

from hypothesis import given

from pypaginate.domain.specs import FilterSpec
from tests.property.conftest import setup_memory_sync
from tests.property.strategies import datasets, eq_filter_specs, gte_filter_specs


@given(data=datasets(min_size=1, max_size=200), spec=gte_filter_specs())
def test_filter_never_adds(
    data: list[dict[str, object]],
    spec: FilterSpec,
) -> None:
    """Filtering never produces more items than input."""
    env = setup_memory_sync(data)
    result = env.do_filter(env.query, [spec])
    assert len(result) <= len(data)


@given(data=datasets(min_size=1, max_size=200), spec=eq_filter_specs())
def test_eq_filter_all_match(
    data: list[dict[str, object]],
    spec: FilterSpec,
) -> None:
    """Every result of an eq filter has the target value."""
    env = setup_memory_sync(data)
    result = env.do_filter(env.query, [spec])
    for item in result:
        assert env.get_field(item, spec.field) == spec.value


@given(data=datasets(min_size=1, max_size=200), spec=gte_filter_specs())
def test_gte_filter_all_match(
    data: list[dict[str, object]],
    spec: FilterSpec,
) -> None:
    """Every result of a gte filter has field >= value."""
    env = setup_memory_sync(data)
    result = env.do_filter(env.query, [spec])
    for item in result:
        assert env.get_field(item, spec.field) >= spec.value


@given(data=datasets(min_size=1, max_size=100), spec=gte_filter_specs())
def test_filter_idempotent(
    data: list[dict[str, object]],
    spec: FilterSpec,
) -> None:
    """Applying the same filter twice gives the same result."""
    env = setup_memory_sync(data)
    once = env.do_filter(env.query, [spec])
    twice = env.do_filter(once, [spec])
    assert len(once) == len(twice)
    for a, b in zip(once, twice, strict=True):
        assert env.get_field(a, "id") == env.get_field(b, "id")


@given(data=datasets(min_size=0, max_size=50))
def test_filter_empty_specs_returns_all(
    data: list[dict[str, object]],
) -> None:
    """No filter specs returns all items unchanged."""
    env = setup_memory_sync(data)
    result = env.do_filter(env.query, [])
    assert len(result) == len(data)
