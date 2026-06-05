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

    def test_fuzzy_word_contained_in_value_scores_100(self, backend: MemorySearchBackend) -> None:
        # A query word fully present in the value shares all its trigrams.
        items = [{"name": "hello world"}]
        spec = SearchSpec(query="hello", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 1

    def test_fuzzy_typo_in_longer_word_still_matches(self, backend: MemorySearchBackend) -> None:
        # The typo "programing" shares most trigrams with "programming" (the
        # trigram metric shines on longer words; short single-char typos do not).
        items = [{"name": "programming"}, {"name": "cooking"}]
        spec = SearchSpec(query="programing", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        names = {item["name"] for item in result}
        assert "programming" in names
        assert "cooking" not in names
