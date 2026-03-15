"""Benchmark tests for filter engine performance."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import FilterSpec
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry


pytestmark = pytest.mark.benchmark


@pytest.fixture(scope="session")
def filter_engine() -> FilterEngine:
    """FilterEngine backed by the default registry."""
    return FilterEngine(create_default_registry())


@pytest.mark.benchmark(group="filter")
def test_filter_single_spec(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    filter_engine: FilterEngine,
) -> None:
    """Filter 1000 items with a single gte spec."""
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(filter_engine.apply, medium_dataset, specs)
    assert all(item["age"] >= 30 for item in result)


@pytest.mark.benchmark(group="filter")
def test_filter_multiple_specs(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    filter_engine: FilterEngine,
) -> None:
    """Filter 1000 items with two specs (range)."""
    specs = [
        FilterSpec(field="age", operator="gte", value=25),
        FilterSpec(field="age", operator="lt", value=40),
    ]
    result = benchmark(filter_engine.apply, medium_dataset, specs)
    assert all(25 <= item["age"] < 40 for item in result)


@pytest.mark.benchmark(group="filter")
def test_filter_equality(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    filter_engine: FilterEngine,
) -> None:
    """Filter 1000 items with equality check."""
    specs = [FilterSpec(field="age", operator="eq", value=30)]
    result = benchmark(filter_engine.apply, medium_dataset, specs)
    assert all(item["age"] == 30 for item in result)
