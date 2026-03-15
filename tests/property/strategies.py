"""Reusable Hypothesis strategies for property-based tests.

Provides composable strategies for generating pagination parameters,
filter/sort specs, and datasets of varying size.
"""

from __future__ import annotations

from hypothesis import strategies as st

from pypaginate import (
    FilterSpec,
    OffsetParams,
    SortDirection,
    SortSpec,
)


@st.composite
def offset_params(
    draw: st.DrawFn,
    max_page: int = 100,
    max_limit: int = 100,
) -> OffsetParams:
    """Generate valid OffsetParams with bounded page and limit."""
    page = draw(st.integers(min_value=1, max_value=max_page))
    limit = draw(st.integers(min_value=1, max_value=max_limit))
    return OffsetParams(page=page, limit=limit)


@st.composite
def datasets(
    draw: st.DrawFn,
    min_size: int = 0,
    max_size: int = 200,
) -> list[dict[str, int | str]]:
    """Generate a list of dicts with id, name, and value fields."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    return [
        {
            "id": i,
            "name": f"item_{i}",
            "value": draw(st.integers(min_value=-1000, max_value=1000)),
        }
        for i in range(size)
    ]


@st.composite
def eq_filter_specs(draw: st.DrawFn) -> FilterSpec:
    """Generate an eq FilterSpec targeting the 'value' field."""
    value = draw(st.integers(min_value=-1000, max_value=1000))
    return FilterSpec(field="value", operator="eq", value=value)


@st.composite
def gte_filter_specs(draw: st.DrawFn) -> FilterSpec:
    """Generate a gte FilterSpec targeting the 'value' field."""
    value = draw(st.integers(min_value=-1000, max_value=1000))
    return FilterSpec(field="value", operator="gte", value=value)


@st.composite
def sort_specs(draw: st.DrawFn) -> SortSpec:
    """Generate a SortSpec for the 'value' field."""
    direction = draw(st.sampled_from([SortDirection.ASC, SortDirection.DESC]))
    return SortSpec(field="value", direction=direction)


@st.composite
def sortable_datasets(
    draw: st.DrawFn,
    min_size: int = 0,
    max_size: int = 100,
) -> list[dict[str, int | str]]:
    """Generate datasets with unique integer values for sorting."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    values = draw(
        st.lists(
            st.integers(min_value=-1000, max_value=1000),
            min_size=size,
            max_size=size,
        )
    )
    return [{"id": i, "name": f"item_{i}", "value": v} for i, v in enumerate(values)]
