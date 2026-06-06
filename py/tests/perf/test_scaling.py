"""Scaling-curve benchmarks: one op across growing dataset sizes.

Each core op is benchmarked at 1K, 10K, and 100K rows so the CI dashboard can
plot how latency grows with size. The whole module is ``slow`` (and benchmark),
so it only runs under ``--run-benchmark --run-slow`` (the CI Benchmarks lane).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from tests.factories.data import make_users

from pypaginate import (
    Dataset,
    FilterSpec,
    OffsetParams,
    SearchSpec,
    SortSpec,
    filter,
    paginate,
    search,
    sort,
)


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture


pytestmark = pytest.mark.slow

_SIZES = [
    pytest.param(1_000, id="1k"),
    pytest.param(10_000, id="10k"),
    pytest.param(100_000, id="100k"),
]
_PARAMS = OffsetParams(page=1, limit=20)


@pytest.mark.benchmark(group="scale-filter")
@pytest.mark.parametrize("size", _SIZES)
def test_filter_scaling(benchmark: BenchmarkFixture, size: int) -> None:
    """``filter()`` latency across growing sizes."""
    rows = make_users(size)
    specs = [FilterSpec(field="age", operator="gte", value=30)]
    result = benchmark(filter, rows, specs)
    assert len(result) <= size


@pytest.mark.benchmark(group="scale-sort")
@pytest.mark.parametrize("size", _SIZES)
def test_sort_scaling(benchmark: BenchmarkFixture, size: int) -> None:
    """``sort()`` latency across growing sizes."""
    rows = make_users(size)
    specs = [SortSpec(field="age", direction="asc")]
    result = benchmark(sort, rows, specs)
    assert len(result) == size


@pytest.mark.benchmark(group="scale-search")
@pytest.mark.parametrize("size", _SIZES)
def test_search_scaling(benchmark: BenchmarkFixture, size: int) -> None:
    """``search()`` latency across growing sizes."""
    rows = make_users(size)
    spec = SearchSpec(query="Alice", fields=["name"])
    result = benchmark(search, rows, spec)
    assert len(result) >= 0


@pytest.mark.benchmark(group="scale-paginate")
@pytest.mark.parametrize("size", _SIZES)
def test_paginate_scaling(benchmark: BenchmarkFixture, size: int) -> None:
    """``paginate()`` latency across growing sizes."""
    rows = make_users(size)
    result = benchmark(paginate, rows, _PARAMS)
    assert result.total == size


@pytest.mark.benchmark(group="scale-pipeline")
@pytest.mark.parametrize("size", _SIZES)
def test_pipeline_scaling(benchmark: BenchmarkFixture, size: int) -> None:
    """``Dataset.page`` (filter + sort + paginate) latency across growing sizes."""
    native = Dataset(make_users(size))
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction="asc")]
    result = benchmark(native.page, _PARAMS, filters=filters, sorting=sorting)
    assert result.total > 0
