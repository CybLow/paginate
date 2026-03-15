"""Benchmark tests for individual adapter operations.

Measures filter, sort, and search backend performance
on 1000-item datasets with varying spec complexity.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import FilterSpec, SearchSpec, SortDirection, SortSpec
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend


pytestmark = pytest.mark.benchmark


@pytest.mark.benchmark(group="adapter-filter")
def test_filter_single_spec(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Filter 1000 items with a single gte spec."""
    backend = MemoryFilterBackend()
    specs = [FilterSpec(field="age", operator="gte", value=30)]

    result = benchmark(backend.apply_filters, medium_dataset, specs)

    assert len(result) > 0


@pytest.mark.benchmark(group="adapter-filter")
def test_filter_five_specs(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Filter 1000 items with 5 AND conditions."""
    backend = MemoryFilterBackend()
    specs = [
        FilterSpec(field="age", operator="gte", value=25),
        FilterSpec(field="age", operator="lte", value=60),
        FilterSpec(field="name", operator="starts_with", value="user_"),
        FilterSpec(field="id", operator="gte", value=10),
        FilterSpec(field="id", operator="lte", value=900),
    ]

    result = benchmark(backend.apply_filters, medium_dataset, specs)

    assert len(result) > 0


@pytest.mark.benchmark(group="adapter-sort")
def test_sort_single_field(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Sort 1000 items by a single field."""
    backend = MemorySortBackend()
    specs = [SortSpec(field="age")]

    result = benchmark(backend.apply_sorting, medium_dataset, specs)

    assert result[0]["age"] <= result[-1]["age"]


@pytest.mark.benchmark(group="adapter-sort")
def test_sort_three_fields(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Sort 1000 items by 3 fields."""
    backend = MemorySortBackend()
    specs = [
        SortSpec(field="age"),
        SortSpec(field="name"),
        SortSpec(field="id", direction=SortDirection.DESC),
    ]

    result = benchmark(backend.apply_sorting, medium_dataset, specs)

    assert len(result) == len(medium_dataset)


@pytest.mark.benchmark(group="adapter-search")
def test_search_contains(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Search 1000 items with CONTAINS mode."""
    backend = MemorySearchBackend()
    spec = SearchSpec(query="user_5", fields=("name",))

    result = benchmark(backend.apply_search, medium_dataset, spec)

    assert len(result) > 0


@pytest.mark.benchmark(group="adapter-chain")
def test_full_adapter_chain(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Full chain: filter -> sort -> search on 1000 items."""
    fb = MemoryFilterBackend()
    sb = MemorySortBackend()
    srch = MemorySearchBackend()
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age")]
    search = SearchSpec(query="user_5", fields=("name",))

    def chain() -> object:
        filtered = fb.apply_filters(medium_dataset, filters)
        sorted_data = sb.apply_sorting(filtered, sorting)
        return srch.apply_search(sorted_data, search)

    result = benchmark(chain)

    assert isinstance(result, list)
