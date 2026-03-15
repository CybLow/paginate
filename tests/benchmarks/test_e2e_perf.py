"""Benchmark tests for end-to-end pagination flows.

Measures paginate() dispatch and full pipeline.execute() performance.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import FilterSpec, OffsetParams, SortSpec, paginate
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


pytestmark = pytest.mark.benchmark


@pytest.mark.benchmark(group="e2e")
def test_paginate_auto_detect_1000(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """paginate() with auto-detect on 1000 items."""
    result = benchmark(paginate, medium_dataset, OffsetParams(page=1, limit=20))

    assert result.total == 1_000


@pytest.mark.benchmark(group="e2e")
def test_paginate_deep_page(
    benchmark: Any,
    large_dataset: list[dict[str, Any]],
) -> None:
    """paginate() page=50 on 10000 items (deep page)."""
    result = benchmark(paginate, large_dataset, OffsetParams(page=50, limit=20))

    assert result.total == 10_000


@pytest.mark.benchmark(group="e2e")
def test_pipeline_filter_sort(
    benchmark: Any,
    medium_dataset: list[dict[str, Any]],
) -> None:
    """Full pipeline.execute() with filter+sort on 1000 items."""
    paginator: Paginator[dict[str, Any]] = Paginator(MemoryBackend())
    pipeline: SyncPipeline[dict[str, Any]] = SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
    )
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age")]
    params = OffsetParams(page=1, limit=20)

    result = benchmark(
        pipeline.execute,
        medium_dataset,
        params,
        filters=filters,
        sorting=sorting,
    )

    assert result.total > 0


@pytest.mark.benchmark(group="e2e")
def test_paginate_empty_list(benchmark: Any) -> None:
    """paginate() on empty list."""
    result = benchmark(paginate, [], OffsetParams(page=1, limit=20))

    assert result.total == 0


@pytest.mark.benchmark(group="e2e")
def test_paginate_single_item(benchmark: Any) -> None:
    """paginate() on single item."""
    result = benchmark(paginate, [{"x": 1}], OffsetParams(page=1, limit=20))

    assert result.total == 1
