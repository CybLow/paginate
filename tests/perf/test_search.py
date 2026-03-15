"""Search perf — stress correctness + benchmark speed.

Verifies search matches at 100K scale and benchmarks
search throughput.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.specs import SearchSpec
from tests.perf.conftest import _setup_memory_sync


# -- Stress: correctness at scale -------------------------------------------


@pytest.mark.slow
def test_search_100k_finds_matches(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Search 100K items for 'User_42', verify matches found."""
    env = _setup_memory_sync(dataset_100k)
    spec = SearchSpec(query="User_42", fields=("name",))
    result = env.do_search(env.query, spec)
    assert len(result) > 0
    names = [env.get_field(item, "name") for item in result]
    assert any("User_42" in n for n in names)


@pytest.mark.slow
def test_search_100k_no_match(
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Search 100K for nonexistent term returns empty."""
    env = _setup_memory_sync(dataset_100k)
    spec = SearchSpec(query="ZZZNOTFOUND", fields=("name",))
    result = env.do_search(env.query, spec)
    assert len(result) == 0


# -- Benchmark: speed -------------------------------------------------------


@pytest.mark.benchmark(group="search-memory")
def test_bench_search_10k(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Benchmark search on 10K items."""
    env = _setup_memory_sync(dataset_10k)
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(env.do_search, env.query, spec)
    assert len(result) >= 0


@pytest.mark.benchmark(group="search-memory")
def test_bench_search_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Benchmark search on 100K items."""
    env = _setup_memory_sync(dataset_100k)
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(env.do_search, env.query, spec)
    assert len(result) >= 0
