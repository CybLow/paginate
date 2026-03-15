"""Pagination perf — stress correctness + benchmark speed.

Stress tests verify correctness at scale (100K+).
Benchmarks measure throughput at various dataset sizes.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.models import OffsetParams
from tests.perf.conftest import _setup_memory_sync


# -- Stress: correctness at scale -------------------------------------------


@pytest.mark.slow
def test_paginate_100k_total(dataset_100k: list[dict[str, Any]]) -> None:
    """Paginate 100K items, verify total is correct."""
    env = _setup_memory_sync(dataset_100k)
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=100))
    assert page.total == 100_000


@pytest.mark.slow
def test_paginate_100k_all_pages(dataset_100k: list[dict[str, Any]]) -> None:
    """Iterate ALL pages of 100K items, verify completeness."""
    env = _setup_memory_sync(dataset_100k)
    collected = 0
    page_num = 1
    while True:
        page = env.do_paginate(env.query, OffsetParams(page=page_num, limit=1000))
        collected += len(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert collected == 100_000


@pytest.mark.slow
def test_paginate_100k_no_duplicates(dataset_100k: list[dict[str, Any]]) -> None:
    """All pages combined have no duplicate IDs."""
    env = _setup_memory_sync(dataset_100k)
    ids: set[int] = set()
    page_num = 1
    while True:
        page = env.do_paginate(env.query, OffsetParams(page=page_num, limit=1000))
        for item in page.items:
            ids.add(env.get_field(item, "id"))
        if not page.has_next:
            break
        page_num += 1
    assert len(ids) == 100_000


# -- Benchmark: speed -------------------------------------------------------


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_1k(
    benchmark: Any,
    dataset_1k: list[dict[str, Any]],
) -> None:
    """Benchmark paginate on 1K items."""
    env = _setup_memory_sync(dataset_1k)
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 1_000


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Benchmark paginate on 10K items."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 10_000


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Benchmark paginate on 100K items."""
    env = _setup_memory_sync(dataset_100k)
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 100_000


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_500k(
    benchmark: Any,
    dataset_500k: list[dict[str, Any]],
) -> None:
    """Benchmark paginate on 500K items."""
    env = _setup_memory_sync(dataset_500k)
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 500_000


@pytest.mark.benchmark(group="paginate-memory")
def test_bench_paginate_1m(
    benchmark: Any,
    dataset_1m: list[dict[str, Any]],
) -> None:
    """Benchmark paginate on 1M items."""
    env = _setup_memory_sync(dataset_1m)
    result = benchmark(env.do_paginate, env.query, OffsetParams(page=1, limit=20))
    assert result.total == 1_000_000
