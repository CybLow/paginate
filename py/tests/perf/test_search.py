"""Search throughput benchmarks over the core ``search`` op.

Ranked ``search()`` over plain lists (single- and multi-field), plus the resident
``Dataset.search`` path, at 1K and 10K rows from the deterministic factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pypaginate import SearchSpec, search


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

    from pypaginate import Dataset


_BY_NAME = SearchSpec(query="Alice", fields=["name"])
_MULTI_FIELD = SearchSpec(query="alice", fields=["name", "email"])


@pytest.mark.benchmark(group="search")
def test_search_1k(benchmark: BenchmarkFixture, dataset_1k: list[dict[str, object]]) -> None:
    """Single-field search over 1K rows."""
    result = benchmark(search, dataset_1k, _BY_NAME)
    assert len(result) >= 0


@pytest.mark.benchmark(group="search")
def test_search_10k(benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]) -> None:
    """Single-field search over 10K rows."""
    result = benchmark(search, dataset_10k, _BY_NAME)
    assert len(result) >= 0


@pytest.mark.benchmark(group="search")
def test_search_10k_multi_field(
    benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]
) -> None:
    """Two-field search over 10K rows."""
    result = benchmark(search, dataset_10k, _MULTI_FIELD)
    assert len(result) >= 0


@pytest.mark.benchmark(group="search-dataset")
def test_dataset_search_10k(
    benchmark: BenchmarkFixture, native_10k: Dataset[dict[str, object]]
) -> None:
    """Resident-dataset search over the marshalled 10K rows."""
    result = benchmark(native_10k.search, _BY_NAME)
    assert len(result) >= 0
