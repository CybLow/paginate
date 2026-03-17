"""Property-based sorting invariants.

Verifies algebraic properties of the sort engine:
count preserved, monotonic order, idempotent.
"""

from __future__ import annotations

from hypothesis import given

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.specs import SortSpec
from tests.property.conftest import setup_memory_sync
from tests.property.strategies import datasets, sort_specs


@given(data=datasets(min_size=1, max_size=200), spec=sort_specs())
def test_sort_preserves_count(
    data: list[dict[str, object]],
    spec: SortSpec,
) -> None:
    """Sorting never changes the number of items."""
    env = setup_memory_sync(data)
    result = env.do_sort(env.query, [spec])
    assert len(result) == len(data)


@given(data=datasets(min_size=2, max_size=200))
def test_sort_asc_monotonic(
    data: list[dict[str, object]],
) -> None:
    """ASC sort produces monotonic non-decreasing values."""
    env = setup_memory_sync(data)
    spec = SortSpec(field="age", direction=SortDirection.ASC)
    result = env.do_sort(env.query, [spec])
    ages = [env.get_field(item, "age") for item in result]
    for i in range(len(ages) - 1):
        assert ages[i] <= ages[i + 1]


@given(data=datasets(min_size=2, max_size=200))
def test_sort_desc_monotonic(
    data: list[dict[str, object]],
) -> None:
    """DESC sort produces monotonic non-increasing values."""
    env = setup_memory_sync(data)
    spec = SortSpec(field="age", direction=SortDirection.DESC)
    result = env.do_sort(env.query, [spec])
    ages = [env.get_field(item, "age") for item in result]
    for i in range(len(ages) - 1):
        assert ages[i] >= ages[i + 1]


@given(data=datasets(min_size=1, max_size=100), spec=sort_specs())
def test_sort_idempotent(
    data: list[dict[str, object]],
    spec: SortSpec,
) -> None:
    """Sorting twice gives the same result as sorting once."""
    env = setup_memory_sync(data)
    once = env.do_sort(env.query, [spec])
    twice = env.do_sort(once, [spec])
    assert len(once) == len(twice)
    for a, b in zip(once, twice, strict=True):
        assert env.get_field(a, "id") == env.get_field(b, "id")


@given(data=datasets(min_size=1, max_size=200))
def test_sort_preserves_elements(
    data: list[dict[str, object]],
) -> None:
    """Sort preserves all original element IDs."""
    env = setup_memory_sync(data)
    spec = SortSpec(field="name", direction=SortDirection.ASC)
    result = env.do_sort(env.query, [spec])
    original_ids = {env.get_field(item, "id") for item in data}
    sorted_ids = {env.get_field(item, "id") for item in result}
    assert original_ids == sorted_ids
