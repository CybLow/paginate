"""Benchmark tests for sort engine performance."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import SortDirection, SortSpec
from pypaginate.sorting.engine import SortEngine


pytestmark = pytest.mark.benchmark


@pytest.fixture(scope="session")
def sort_engine() -> SortEngine:
    """Stateless SortEngine instance."""
    return SortEngine()


@pytest.mark.benchmark(group="sort")
def test_sort_ascending(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    sort_engine: SortEngine,
) -> None:
    """Sort 1000 items ascending by age."""
    specs = [SortSpec(field="age")]
    result = benchmark(sort_engine.apply, medium_dataset, specs)
    assert result[0]["age"] <= result[-1]["age"]


@pytest.mark.benchmark(group="sort")
def test_sort_descending(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    sort_engine: SortEngine,
) -> None:
    """Sort 1000 items descending by age."""
    specs = [SortSpec(field="age", direction=SortDirection.DESC)]
    result = benchmark(sort_engine.apply, medium_dataset, specs)
    assert result[0]["age"] >= result[-1]["age"]


@pytest.mark.benchmark(group="sort")
def test_sort_multi_key(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    sort_engine: SortEngine,
) -> None:
    """Sort 1000 items by age then name."""
    specs = [SortSpec(field="age"), SortSpec(field="name")]
    result = benchmark(sort_engine.apply, medium_dataset, specs)
    assert len(result) == len(medium_dataset)
