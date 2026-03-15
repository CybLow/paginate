"""Tests for MemorySearchBackend — fuzzy, relevance, edge cases."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.domain.enums import FuzzyMode
from pypaginate.domain.specs import SearchSpec


@pytest.fixture()
def backend() -> MemorySearchBackend:
    """MemorySearchBackend instance."""
    return MemorySearchBackend()


class TestSearchFuzzy:
    def test_fuzzy_mode_returns_approximate_matches(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "Alice"}, {"name": "Alce"}, {"name": "Zebra"}]
        spec = SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        names = {item["name"] for item in result}
        assert "Alice" in names
        assert "Zebra" not in names


class TestSearchRelevanceOrder:
    def test_results_ordered_by_relevance(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "Zebra"}, {"name": "alice"}, {"name": "Alice"}]
        spec = SearchSpec(query="alice", fields=("name",))

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert "Zebra" not in [r["name"] for r in result]
        assert len(result) == 2


class TestSearchFuzzyFallback:
    def test_fuzzy_low_similarity_no_match(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "abcdefgh"}]
        spec = SearchSpec(query="zzzzz", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=90)

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert result == []

    def test_fuzzy_empty_value_no_match(self, backend: MemorySearchBackend) -> None:
        items = [{"name": ""}]
        spec = SearchSpec(query="test", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert result == []

    def test_fuzzy_substring_scores_100(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "hello world"}]
        spec = SearchSpec(query="hello", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 1

    def test_fuzzy_value_shorter_in_query_scores_100(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "ab"}]
        spec = SearchSpec(query="xabx", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 1
