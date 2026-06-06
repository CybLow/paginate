"""Pagination throughput benchmarks over the core ``paginate`` op.

In-memory ``paginate()`` over plain lists at 1K and 10K rows, covering both a
shallow first page and a deep page offset, from the deterministic factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pypaginate import OffsetParams, paginate


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture


_FIRST = OffsetParams(page=1, limit=20)
_DEEP = OffsetParams(page=100, limit=20)


@pytest.mark.benchmark(group="paginate")
def test_paginate_1k(benchmark: BenchmarkFixture, dataset_1k: list[dict[str, object]]) -> None:
    """First-page offset pagination over 1K rows."""
    result = benchmark(paginate, dataset_1k, _FIRST)
    assert result.total == 1_000


@pytest.mark.benchmark(group="paginate")
def test_paginate_10k(benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]) -> None:
    """First-page offset pagination over 10K rows."""
    result = benchmark(paginate, dataset_10k, _FIRST)
    assert result.total == 10_000


@pytest.mark.benchmark(group="paginate")
def test_paginate_10k_deep(
    benchmark: BenchmarkFixture, dataset_10k: list[dict[str, object]]
) -> None:
    """Deep-offset (page 100) offset pagination over 10K rows."""
    result = benchmark(paginate, dataset_10k, _DEEP)
    assert result.total == 10_000
