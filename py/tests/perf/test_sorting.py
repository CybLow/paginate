"""Sorting throughput benchmarks over the core ``sort`` op.

Single- and multi-key ``sort()`` over plain lists, plus the resident
``Dataset.sort`` path, at 1K and 10K rows from the deterministic factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pypaginate import SortSpec, sort


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

    from pypaginate import Dataset


_BY_AGE = [SortSpec(field="age", direction="asc")]
_MULTI = [
    SortSpec(field="active", direction="desc"),
    SortSpec(field="age", direction="asc"),
]


@pytest.mark.benchmark(group="sort")
def test_sort_1k(benchmark: BenchmarkFixture, dataset_1k: list[dict[str, object]]) -> None:
    """Single-key sort over 1K rows."""
    result = benchmark(sort, dataset_1k, _BY_AGE)
    assert len(result) == 1_000


@pytest.mark.benchmark(group="sort")
def test_sort_10k(benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]) -> None:
    """Single-key sort over 10K rows."""
    result = benchmark(sort, dataset_10k, _BY_AGE)
    assert len(result) == 10_000


@pytest.mark.benchmark(group="sort")
def test_sort_10k_multi(benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]) -> None:
    """Two-key sort over 10K rows."""
    result = benchmark(sort, dataset_10k, _MULTI)
    assert len(result) == 10_000


@pytest.mark.benchmark(group="sort-dataset")
def test_dataset_sort_10k(
    benchmark: BenchmarkFixture, native_10k: Dataset[dict[str, object]]
) -> None:
    """Resident-dataset sort over the marshalled 10K rows."""
    result = benchmark(native_10k.sort, _BY_AGE)
    assert len(result) == 10_000
