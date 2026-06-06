"""Filtering throughput benchmarks over the core ``filter`` op.

Single- and multi-spec ``filter()`` over plain lists, plus the resident
``Dataset.filter`` path, at 1K and 10K rows from the deterministic factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pypaginate import FilterSpec, filter


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

    from pypaginate import Dataset


_SINGLE = [FilterSpec(field="age", operator="gte", value=30)]
_MULTI = [
    FilterSpec(field="age", operator="gte", value=25),
    FilterSpec(field="age", operator="lte", value=50),
    FilterSpec(field="active", operator="eq", value=True),
]


@pytest.mark.benchmark(group="filter")
def test_filter_1k_single(benchmark: BenchmarkFixture, dataset_1k: list[dict[str, object]]) -> None:
    """Single-spec filter over 1K rows."""
    result = benchmark(filter, dataset_1k, _SINGLE)
    assert len(result) <= 1_000


@pytest.mark.benchmark(group="filter")
def test_filter_10k_single(
    benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]
) -> None:
    """Single-spec filter over 10K rows."""
    result = benchmark(filter, dataset_10k, _SINGLE)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="filter")
def test_filter_10k_multi(
    benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]
) -> None:
    """Three-spec AND filter over 10K rows."""
    result = benchmark(filter, dataset_10k, _MULTI)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="filter-dataset")
def test_dataset_filter_10k(
    benchmark: BenchmarkFixture, native_10k: Dataset[dict[str, object]]
) -> None:
    """Resident-dataset filter over the marshalled 10K rows."""
    result = benchmark(native_10k.filter, _SINGLE)
    assert len(result) <= 10_000
