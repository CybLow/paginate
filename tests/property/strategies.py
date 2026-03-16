"""Hypothesis strategies for property-based tests.

Reusable composite strategies for pagination params,
filter/sort/search specs, and datasets.
"""

from __future__ import annotations

from typing import Any

from hypothesis import strategies as st

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SortSpec
from tests.factories.data import make_users


@st.composite
def offset_params(draw: st.DrawFn) -> OffsetParams:
    """Generate valid OffsetParams."""
    page = draw(st.integers(min_value=1, max_value=50))
    limit = draw(st.integers(min_value=1, max_value=100))
    return OffsetParams(page=page, limit=limit)


@st.composite
def datasets(
    draw: st.DrawFn,
    min_size: int = 0,
    max_size: int = 200,
) -> list[dict[str, Any]]:
    """Generate user datasets of random size."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    return make_users(size)


@st.composite
def user_ages(draw: st.DrawFn) -> int:
    """Generate ages in the range make_users produces (20-69)."""
    return draw(st.integers(min_value=20, max_value=69))


@st.composite
def sort_directions(draw: st.DrawFn) -> SortDirection:
    """Generate a sort direction."""
    return draw(st.sampled_from([SortDirection.ASC, SortDirection.DESC]))


@st.composite
def eq_filter_specs(draw: st.DrawFn) -> FilterSpec:
    """Generate eq FilterSpec for the age field."""
    age = draw(user_ages())
    return FilterSpec(field="age", operator="eq", value=age)


@st.composite
def gte_filter_specs(draw: st.DrawFn) -> FilterSpec:
    """Generate gte FilterSpec for the age field."""
    age = draw(user_ages())
    return FilterSpec(field="age", operator="gte", value=age)


@st.composite
def sort_specs(draw: st.DrawFn) -> SortSpec:
    """Generate a SortSpec for sortable fields."""
    field = draw(st.sampled_from(["id", "name", "age"]))
    direction = draw(sort_directions())
    return SortSpec(field=field, direction=direction)


__all__ = [
    "datasets",
    "eq_filter_specs",
    "gte_filter_specs",
    "offset_params",
    "sort_directions",
    "sort_specs",
    "user_ages",
]
