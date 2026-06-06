"""Property-based parity: resident Dataset pipeline == per-stage native path.

The resident :class:`pypaginate.Dataset` answers a query two ways — the native
one-call ``_core`` pipeline (``_core.Dataset.page``) and the per-stage path that
runs the ``_core`` filter and sort one stage at a time — and the library
guarantees they return an **identical** page. The example-based proof lives in
``tests/unit/test_dataset.py``; this widens it to randomized flat queries
(filter + sort + offset-paginate) over generated datasets, so the two paths
cannot silently drift.

Scope: numeric fields and operators that order byte-identically, so ordering
and tie-breaks match exactly. String collation and ``Decimal`` are pinned by the
example tests, not fuzzed here.
"""

from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given, settings, strategies as st

from pypaginate import Dataset, FilterSpec, OffsetParams, SortSpec
from pypaginate.dataset import _HAS_NATIVE
from pypaginate.domain.enums import SortDirection
from tests.property.strategies import datasets, offset_params


pytestmark = pytest.mark.skipif(
    not _HAS_NATIVE,
    reason="native _core extension not installed",
)

_NUMERIC_FIELDS = ("id", "age")
_FILTER_OPS = ("gte", "gt", "lte", "lt", "eq", "ne")
_DIRECTIONS = (SortDirection.ASC, SortDirection.DESC)


@st.composite
def _flat_filters(draw: st.DrawFn) -> list[FilterSpec]:
    """0-3 flat filters over numeric fields (the pipeline ANDs them)."""
    count = draw(st.integers(min_value=0, max_value=3))
    return [draw(_one_filter()) for _ in range(count)]


@st.composite
def _one_filter(draw: st.DrawFn) -> FilterSpec:
    """A single numeric-field filter spec."""
    field = draw(st.sampled_from(_NUMERIC_FIELDS))
    operator = draw(st.sampled_from(_FILTER_OPS))
    value = draw(st.integers(min_value=18, max_value=72))
    return FilterSpec(field=field, operator=operator, value=value)


@st.composite
def _sorts(draw: st.DrawFn) -> list[SortSpec]:
    """0-2 sorts over distinct numeric fields (stable order is comparable)."""
    fields = draw(st.lists(st.sampled_from(_NUMERIC_FIELDS), unique=True, max_size=2))
    return [SortSpec(field=f, direction=draw(st.sampled_from(_DIRECTIONS))) for f in fields]


def _fields(page: Any) -> tuple[Any, ...]:
    """A comparable tuple of a page's items + metadata."""
    return (
        list(page.items),
        page.total,
        page.page,
        page.pages,
        page.has_next,
        page.has_previous,
    )


@settings(max_examples=150, deadline=None)
@given(
    items=datasets(max_size=120),
    params=offset_params(),
    filters=_flat_filters(),
    sorting=_sorts(),
)
def test_native_pipeline_matches_pure(
    items: list[dict[str, Any]],
    params: OffsetParams,
    filters: list[FilterSpec],
    sorting: list[SortSpec],
) -> None:
    """Resident one-call pipeline and per-stage path yield an identical page."""
    native_ds: Dataset[Any] = Dataset(items)
    assert native_ds._native is not None  # the native path must actually run
    native = native_ds.paginate(params, filters=filters, sorting=sorting)

    pure_ds: Dataset[Any] = Dataset(items)
    pure_ds._native = None
    pure = pure_ds.paginate(params, filters=filters, sorting=sorting)

    assert _fields(native) == _fields(pure)
