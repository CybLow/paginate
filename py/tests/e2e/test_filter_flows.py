"""End-to-end filter flows, including boolean ``And`` / ``Or`` groups.

Exercises :func:`pypaginate.filter` (single spec, flat list, and nested groups)
the way callers compose it — narrowing a dataset and then paginating the subset —
asserting every result against a pure-Python reference predicate over the same
deterministic rows.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from tests.fixtures.helpers import ids_of

from pypaginate import And, FilterSpec, OffsetParams, Or, filter, paginate


pytestmark = [pytest.mark.e2e, pytest.mark.filters]

Row = dict[str, object]
Predicate = Callable[[Row], bool]


def _matching_ids(rows: list[Row], predicate: Predicate) -> list[int]:
    """Reference ids of every row satisfying ``predicate`` (original order)."""
    return [int(row["id"]) for row in rows if predicate(row)]


def test_single_spec_filter(users: list[Row]) -> None:
    """A lone ``FilterSpec`` keeps only the rows it matches, in order."""
    result = filter(users, FilterSpec(field="name", operator="contains", value="Alice"))
    assert ids_of(result) == _matching_ids(users, lambda r: "Alice" in str(r["name"]))
    assert result


def test_flat_list_filter_is_conjunctive(users: list[Row]) -> None:
    """A flat list of specs ANDs together (active AND adult)."""
    result = filter(
        users,
        [
            FilterSpec(field="active", operator="eq", value=True),
            FilterSpec(field="age", operator="gte", value=40),
        ],
    )
    expected = _matching_ids(users, lambda r: bool(r["active"]) and int(r["age"]) >= 40)
    assert ids_of(result) == expected


def test_and_group(users: list[Row]) -> None:
    """An explicit ``And`` group matches the intersection of its conditions."""
    result = filter(
        users,
        And(
            FilterSpec(field="active", operator="eq", value=True),
            FilterSpec(field="age", operator="gte", value=40),
        ),
    )
    expected = _matching_ids(users, lambda r: bool(r["active"]) and int(r["age"]) >= 40)
    assert ids_of(result) == expected


def test_or_group(users: list[Row]) -> None:
    """An ``Or`` group matches the union of its conditions."""
    result = filter(
        users,
        Or(
            FilterSpec(field="age", operator="lt", value=25),
            FilterSpec(field="age", operator="gte", value=70),
        ),
    )
    expected = _matching_ids(users, lambda r: int(r["age"]) < 25 or int(r["age"]) >= 70)
    assert ids_of(result) == expected


def test_nested_group(users: list[Row]) -> None:
    """A nested ``And(Or(...), ...)`` tree composes correctly."""
    result = filter(
        users,
        And(
            Or(
                FilterSpec(field="name", operator="contains", value="Alice"),
                FilterSpec(field="name", operator="contains", value="Bob"),
            ),
            FilterSpec(field="active", operator="eq", value=True),
        ),
    )
    expected = _matching_ids(
        users,
        lambda r: ("Alice" in str(r["name"]) or "Bob" in str(r["name"])) and bool(r["active"]),
    )
    assert ids_of(result) == expected


def test_progressive_narrowing(users: list[Row]) -> None:
    """Each added condition can only keep or shrink the result set."""
    none = filter(users, [])
    one = filter(users, [FilterSpec(field="name", operator="contains", value="a")])
    two = filter(
        users,
        [
            FilterSpec(field="name", operator="contains", value="a"),
            FilterSpec(field="active", operator="eq", value=True),
        ],
    )
    assert len(none) >= len(one) >= len(two)


def test_filter_to_empty(users: list[Row]) -> None:
    """A spec that matches nothing yields an empty list."""
    result = filter(users, FilterSpec(field="name", operator="eq", value="__nobody__"))
    assert result == []


def test_filter_then_paginate(users: list[Row]) -> None:
    """Filtering then paginating the subset preserves order and counts."""
    active = filter(users, FilterSpec(field="active", operator="eq", value=True))
    page = paginate(active, OffsetParams(page=1, limit=5))
    assert page.total == len(active)
    assert ids_of(page.items) == ids_of(active)[:5]
    assert all(row["active"] for row in page)
