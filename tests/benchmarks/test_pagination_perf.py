"""Benchmark tests for pagination performance."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import OffsetParams, OverflowStrategy, paginate


pytestmark = pytest.mark.benchmark


@pytest.mark.benchmark(group="pagination")
def test_paginate_100_items(benchmark, small_dataset: list[dict[str, Any]]) -> None:
    """Paginate 100 items, first page."""
    result = benchmark(paginate, small_dataset, OffsetParams(page=1, limit=20))
    assert result.total == 100


@pytest.mark.benchmark(group="pagination")
def test_paginate_1000_items(benchmark, medium_dataset: list[dict[str, Any]]) -> None:
    """Paginate 1000 items, middle page."""
    result = benchmark(paginate, medium_dataset, OffsetParams(page=25, limit=20))
    assert result.total == 1_000


@pytest.mark.benchmark(group="pagination")
def test_paginate_10000_items(benchmark, large_dataset: list[dict[str, Any]]) -> None:
    """Paginate 10000 items, late page."""
    result = benchmark(paginate, large_dataset, OffsetParams(page=50, limit=20))
    assert result.total == 10_000


@pytest.mark.benchmark(group="pagination")
def test_paginate_with_clamp(benchmark, medium_dataset: list[dict[str, Any]]) -> None:
    """Paginate with clamp overflow on out-of-range page."""
    result = benchmark(
        paginate,
        medium_dataset,
        OffsetParams(page=999, limit=10),
        overflow=OverflowStrategy.CLAMP,
    )
    assert result.page == 100
