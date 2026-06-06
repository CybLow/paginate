"""Marshalling overhead of a single ``paginate()`` call.

Isolates the fixed per-call cost of the in-memory entry point — what one
``paginate()`` spends crossing into the Rust core to build the page metadata,
both at a realistic size and on a tiny list where the data cost is negligible —
plus the one-time cost of marshalling a resident :class:`Dataset` and the native
``Dataset.page`` call it enables.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from tests.factories.data import make_users

from pypaginate import Dataset, OffsetParams, paginate


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture


_PARAMS = OffsetParams(page=1, limit=20)
_TINY = make_users(10)


@pytest.mark.benchmark(group="overhead-paginate")
def test_paginate_fixed_cost_tiny(benchmark: BenchmarkFixture) -> None:
    """Per-call ``paginate()`` cost with negligible data (10 rows)."""
    result = benchmark(paginate, _TINY, _PARAMS)
    assert result.total == 10


@pytest.mark.benchmark(group="overhead-paginate")
def test_paginate_single_call_1k(
    benchmark: BenchmarkFixture, dataset_1k: list[dict[str, object]]
) -> None:
    """A single ``paginate()`` call over 1K rows."""
    result = benchmark(paginate, dataset_1k, _PARAMS)
    assert result.total == 1_000


@pytest.mark.benchmark(group="overhead-marshal")
def test_dataset_marshal_1k(
    benchmark: BenchmarkFixture, dataset_1k: list[dict[str, object]]
) -> None:
    """One-time cost of marshalling 1K rows into a resident ``Dataset``."""
    result = benchmark(Dataset, dataset_1k)
    assert len(result) == 1_000


@pytest.mark.benchmark(group="overhead-marshal")
def test_native_page_single_call(
    benchmark: BenchmarkFixture, native_1k: Dataset[dict[str, object]]
) -> None:
    """A single native ``Dataset.page`` call over the marshalled 1K rows."""
    result = benchmark(native_1k.page, _PARAMS)
    assert result.total == 1_000
