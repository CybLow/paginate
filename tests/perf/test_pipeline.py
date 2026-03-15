"""Pipeline perf — stress correctness + benchmark speed.

Full pipeline: filter + sort + paginate at scale.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.models import OffsetParams
from pypaginate.domain.specs import FilterSpec, SortSpec
from tests.perf.conftest import _setup_memory_sync


# -- Stress: correctness at scale -------------------------------------------


@pytest.mark.slow
def test_pipeline_100k_correctness(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Full pipeline on 100K: filter + sort + paginate."""
    env = _setup_memory_sync(dataset_100k)
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=50)
    page = env.do_pipeline(
        env.query,
        params,
        filters=filters,
        sorting=sorting,
    )
    assert page.total > 0
    assert len(page.items) <= 50
    ages = [env.get_field(item, "age") for item in page.items]
    assert all(a >= 30 for a in ages)


@pytest.mark.slow
def test_pipeline_100k_all_filtered_pages(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Iterate all pipeline pages, verify completeness."""
    env = _setup_memory_sync(dataset_100k)
    filters = [FilterSpec(field="age", operator="gte", value=40)]
    params_limit = 500
    collected = 0
    page_num = 1
    while True:
        page = env.do_pipeline(
            env.query,
            OffsetParams(page=page_num, limit=params_limit),
            filters=filters,
        )
        collected += len(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert collected == page.total


# -- Benchmark: speed -------------------------------------------------------


@pytest.mark.benchmark(group="pipeline-memory")
def test_bench_pipeline_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Benchmark full pipeline on 10K items."""
    env = _setup_memory_sync(dataset_10k)
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)
    result = benchmark(
        env.do_pipeline,
        env.query,
        params,
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="pipeline-memory")
def test_bench_pipeline_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Benchmark full pipeline on 100K items."""
    env = _setup_memory_sync(dataset_100k)
    filters = [FilterSpec(field="age", operator="gte", value=30)]
    sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
    params = OffsetParams(page=1, limit=20)
    result = benchmark(
        env.do_pipeline,
        env.query,
        params,
        filters=filters,
        sorting=sorting,
    )
    assert result.total > 0
