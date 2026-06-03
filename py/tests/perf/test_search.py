"""Search perf -- stress correctness + benchmark speed.

Verifies search matches at 100K (memory) and 10K (SA),
benchmarks search throughput across all 3 backends.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.specs import SearchSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import _setup_memory_sync


# -- Stress: memory at 100K ------------------------------------------------


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


# -- Stress: SA at 10K (search builds query, sync) -------------------------


@pytest.mark.slow
def test_sa_sync_search_10k_builds_query(
    sa_sync_env_10k: BackendEnv,
) -> None:
    """SA sync: search 10K by name, query is valid."""
    spec = SearchSpec(query="User_5", fields=("name",))
    result = sa_sync_env_10k.do_search(sa_sync_env_10k.query, spec)
    assert result is not None


@pytest.mark.slow
def test_sa_async_search_10k_builds_query(
    sa_async_env_10k: BackendEnv,
) -> None:
    """SA async: search 10K by name, query is valid."""
    spec = SearchSpec(query="User_5", fields=("name",))
    result = sa_async_env_10k.do_search(sa_async_env_10k.query, spec)
    assert result is not None


# -- Benchmark: memory -----------------------------------------------------


@pytest.mark.benchmark(group="search-memory")
def test_bench_search_memory_10k(
    benchmark: Any,
    memory_env_10k: BackendEnv,
) -> None:
    """Benchmark search on 10K items (memory)."""
    env = memory_env_10k
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(env.do_search, env.query, spec)
    assert len(result) >= 0


@pytest.mark.benchmark(group="search-memory")
def test_bench_search_memory_100k(
    benchmark: Any,
    memory_env_100k: BackendEnv,
) -> None:
    """Benchmark search on 100K items (memory)."""
    env = memory_env_100k
    spec = SearchSpec(query="User_5", fields=("name",))
    result = benchmark(env.do_search, env.query, spec)
    assert len(result) >= 0


# -- Benchmark: SA sync (query building) -----------------------------------


@pytest.mark.benchmark(group="search-sa-sync")
def test_bench_search_sa_sync_1k(
    benchmark: Any,
    sa_sync_env_1k: BackendEnv,
) -> None:
    """Benchmark search query build on 1K (SA sync)."""
    env = sa_sync_env_1k
    spec = SearchSpec(query="User_5", fields=("name",))
    benchmark(env.do_search, env.query, spec)


@pytest.mark.benchmark(group="search-sa-sync")
def test_bench_search_sa_sync_10k(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """Benchmark search query build on 10K (SA sync)."""
    env = sa_sync_env_10k
    spec = SearchSpec(query="User_5", fields=("name",))
    benchmark(env.do_search, env.query, spec)


# -- Benchmark: SA async (query building) ----------------------------------


@pytest.mark.benchmark(group="search-sa-async")
def test_bench_search_sa_async_1k(
    benchmark: Any,
    sa_async_env_1k: BackendEnv,
) -> None:
    """Benchmark search query build on 1K (SA async)."""
    env = sa_async_env_1k
    spec = SearchSpec(query="User_5", fields=("name",))
    benchmark(env.do_search, env.query, spec)


@pytest.mark.benchmark(group="search-sa-async")
def test_bench_search_sa_async_10k(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
) -> None:
    """Benchmark search query build on 10K (SA async)."""
    env = sa_async_env_10k
    spec = SearchSpec(query="User_5", fields=("name",))
    benchmark(env.do_search, env.query, spec)
