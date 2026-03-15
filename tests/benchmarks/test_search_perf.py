"""Benchmark tests for search engine performance."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import SearchSpec
from pypaginate.search.engine import SearchEngine


pytestmark = pytest.mark.benchmark


@pytest.fixture(scope="session")
def search_engine() -> SearchEngine:
    """SearchEngine with default TokenParser."""
    return SearchEngine()


@pytest.mark.benchmark(group="search")
def test_search_single_field(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    search_engine: SearchEngine,
) -> None:
    """Search 1000 items by name field."""
    spec = SearchSpec(query="user_50", fields=("name",))
    result = benchmark(search_engine.apply, medium_dataset, spec)
    assert len(result) > 0


@pytest.mark.benchmark(group="search")
def test_search_multiple_fields(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    search_engine: SearchEngine,
) -> None:
    """Search 1000 items across name and email."""
    spec = SearchSpec(query="user_10", fields=("name", "email"))
    result = benchmark(search_engine.apply, medium_dataset, spec)
    assert len(result) > 0


@pytest.mark.benchmark(group="search")
def test_search_no_results(
    benchmark,
    medium_dataset: list[dict[str, Any]],
    search_engine: SearchEngine,
) -> None:
    """Search 1000 items with no matches."""
    spec = SearchSpec(query="zzz_nonexistent", fields=("name",))
    result = benchmark(search_engine.apply, medium_dataset, spec)
    assert len(result) == 0
