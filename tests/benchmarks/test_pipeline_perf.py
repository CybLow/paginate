"""Benchmark tests for full pipeline: filter + sort + paginate."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import FilterSpec, OffsetParams, SortSpec, paginate
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry
from pypaginate.sorting.engine import SortEngine


pytestmark = pytest.mark.benchmark


@pytest.fixture(scope="session")
def filter_engine() -> FilterEngine:
    """FilterEngine backed by the default registry."""
    return FilterEngine(create_default_registry())


@pytest.fixture(scope="session")
def sort_engine() -> SortEngine:
    """Stateless SortEngine instance."""
    return SortEngine()


def _run_pipeline(
    data: list[dict[str, Any]],
    fe: FilterEngine,
    se: SortEngine,
) -> object:
    """Execute filter -> sort -> paginate pipeline."""
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    filtered = fe.apply(data, specs)
    sorted_items = se.apply(filtered, [SortSpec(field="age")])
    return paginate(sorted_items, OffsetParams(page=1, limit=20))


@pytest.mark.benchmark(group="pipeline")
def test_pipeline_medium(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    filter_engine: FilterEngine,
    sort_engine: SortEngine,
) -> None:
    """Full pipeline on 1000 items."""
    result = benchmark(_run_pipeline, medium_dataset, filter_engine, sort_engine)
    assert result.total > 0


@pytest.mark.benchmark(group="pipeline")
def test_pipeline_large(
    benchmark,
    large_dataset: list[dict[str, Any]],
    filter_engine: FilterEngine,
    sort_engine: SortEngine,
) -> None:
    """Full pipeline on 10000 items."""
    result = benchmark(_run_pipeline, large_dataset, filter_engine, sort_engine)
    assert result.total > 0
