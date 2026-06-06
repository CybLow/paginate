"""Dataset parity: the native :class:`Dataset` agrees with a pure-Python oracle.

Where ``test_cross_language_parity`` pins the engine to a frozen cross-language
golden, this lane pins it to an *independent* reference implemented in plain
Python over the very same deterministic rows (``make_users``). Filter, sort, and
the combined ``page`` pass are compared order-for-order; ranked search is compared
as a membership set (the engine owns relevance order, the oracle only the match
set). If the native engine drifts from the obvious semantics, this fails.
"""

from __future__ import annotations

from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st
from tests.factories.data import make_users
from tests.fixtures.helpers import ids_of

from pypaginate import Dataset, FilterSpec, OffsetParams, SearchSpec, SortSpec


pytestmark = pytest.mark.property


# --------------------------------------------------------------------------- #
# Pure-Python reference (the oracle).
# --------------------------------------------------------------------------- #
_OPS = {
    "eq": lambda v, t: v == t,
    "ne": lambda v, t: v != t,
    "gt": lambda v, t: v > t,
    "gte": lambda v, t: v >= t,
    "lt": lambda v, t: v < t,
    "lte": lambda v, t: v <= t,
    "in": lambda v, t: v in t,
    "not_in": lambda v, t: v not in t,
    "between": lambda v, t: t[0] <= v <= t[1],
    "contains": lambda v, t: str(t) in str(v),
}


def _naive_filter(rows: list[dict[str, Any]], specs: list[FilterSpec]) -> list[dict[str, Any]]:
    """Rows matching every spec (AND), in original order."""
    return [r for r in rows if all(_OPS[s.operator](r[s.field], s.value) for s in specs)]


def _naive_sort(rows: list[dict[str, Any]], specs: list[SortSpec]) -> list[dict[str, Any]]:
    """Stable multi-key sort applying keys in priority order (least-significant first)."""
    out = list(rows)
    for spec in reversed(specs):
        out.sort(key=lambda r, f=spec.field: r[f], reverse=spec.direction == "desc")
    return out


def _naive_search_ids(rows: list[dict[str, Any]], query: str, field: str) -> list[int]:
    """Ids of rows whose ``field`` contains ``query`` (case-insensitive)."""
    needle = query.lower()
    return sorted(r["id"] for r in rows if needle in str(r[field]).lower())


# --------------------------------------------------------------------------- #
# Filter parity — order-for-order.
# --------------------------------------------------------------------------- #
_FILTER_CASES: list[list[dict[str, Any]]] = [
    [{"field": "age", "operator": "gt", "value": 40}],
    [{"field": "age", "operator": "between", "value": [30, 50]}],
    [{"field": "active", "operator": "eq", "value": True}],
    [{"field": "id", "operator": "in", "value": [1, 5, 10, 20]}],
    [{"field": "id", "operator": "not_in", "value": [1, 2, 3]}],
    [{"field": "name", "operator": "contains", "value": "Adams"}],
    [{"field": "score", "operator": "lte", "value": 50.0}],
    [{"field": "id", "operator": "ne", "value": 1}],
    [
        {"field": "age", "operator": "gte", "value": 30},
        {"field": "active", "operator": "eq", "value": True},
    ],
]


@pytest.mark.filters
@pytest.mark.parametrize("raw_specs", _FILTER_CASES)
def test_filter_parity(
    dataset: Dataset[dict[str, Any]],
    users: list[dict[str, Any]],
    raw_specs: list[dict[str, Any]],
) -> None:
    specs = [FilterSpec(**spec) for spec in raw_specs]

    assert ids_of(dataset.filter(specs)) == ids_of(_naive_filter(users, specs))


# --------------------------------------------------------------------------- #
# Sort parity — order-for-order.
# --------------------------------------------------------------------------- #
_SORT_CASES: list[list[tuple[str, str]]] = [
    [("age", "asc")],
    [("age", "desc"), ("id", "asc")],
    [("name", "desc"), ("age", "asc")],
    [("active", "asc"), ("score", "desc")],
    [("created_at", "desc")],
    [("score", "asc"), ("id", "asc")],
]


@pytest.mark.sorting
@pytest.mark.parametrize("keys", _SORT_CASES)
def test_sort_parity(
    dataset: Dataset[dict[str, Any]],
    users: list[dict[str, Any]],
    keys: list[tuple[str, str]],
) -> None:
    specs = [SortSpec(field=field, direction=direction) for field, direction in keys]

    assert ids_of(dataset.sort(specs)) == ids_of(_naive_sort(users, specs))


# --------------------------------------------------------------------------- #
# Search parity — membership set (engine owns relevance order).
# --------------------------------------------------------------------------- #
@pytest.mark.search
@pytest.mark.parametrize(
    ("query", "field"),
    [("adams", "name"), ("brown", "name"), ("example", "email"), ("alice", "name")],
)
def test_search_parity(
    dataset: Dataset[dict[str, Any]],
    users: list[dict[str, Any]],
    query: str,
    field: str,
) -> None:
    spec = SearchSpec(query=query, fields=[field], mode="contains")

    assert sorted(ids_of(dataset.search(spec))) == _naive_search_ids(users, query, field)


# --------------------------------------------------------------------------- #
# Combined page parity — filter + sort + offset in one native call.
# --------------------------------------------------------------------------- #
@pytest.mark.filters
@pytest.mark.sorting
@pytest.mark.parametrize("page", [1, 2, 3])
def test_page_parity(
    dataset: Dataset[dict[str, Any]],
    users: list[dict[str, Any]],
    page: int,
) -> None:
    filters = [FilterSpec(field="active", operator="eq", value=True)]
    sorting = [SortSpec(field="age", direction="desc"), SortSpec(field="id", direction="asc")]
    params = OffsetParams(page=page, limit=5)

    result = dataset.page(params, filters=filters, sorting=sorting)
    expected = _naive_sort(_naive_filter(users, filters), sorting)
    window = expected[params.offset : params.offset + params.limit]

    assert ids_of(result.items) == ids_of(window)
    assert result.total == len(expected)


# --------------------------------------------------------------------------- #
# Property-based filter parity — Hypothesis-generated thresholds/operators.
# --------------------------------------------------------------------------- #
@settings(deadline=None, max_examples=60, suppress_health_check=[HealthCheck.too_slow])
@given(
    operator=st.sampled_from(["gt", "gte", "lt", "lte", "eq", "ne"]),
    threshold=st.integers(min_value=10, max_value=90),
)
def test_filter_age_property_parity(operator: str, threshold: int) -> None:
    rows = make_users(80)
    spec = FilterSpec(field="age", operator=operator, value=threshold)

    native = ids_of(Dataset(rows).filter([spec]))

    assert native == ids_of(_naive_filter(rows, [spec]))
