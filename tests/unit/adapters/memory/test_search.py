"""Tests for MemorySearchBackend — basic search modes."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.domain.enums import SearchFieldMode
from pypaginate.domain.specs import SearchSpec


@pytest.fixture()
def backend() -> MemorySearchBackend:
    """MemorySearchBackend instance."""
    return MemorySearchBackend()


class TestSearchContains:
    def test_contains_returns_matching_items(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Alicia"}]
        spec = SearchSpec(query="ali", fields=("name",))

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 2

    def test_no_matches_returns_empty(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "Alice"}, {"name": "Bob"}]
        spec = SearchSpec(query="zzzzz", fields=("name",))

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert result == []


class TestSearchPrefix:
    def test_prefix_returns_items_starting_with_token(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Alicia"}]
        spec = SearchSpec(query="ali", fields=("name",), mode=SearchFieldMode.PREFIX)

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 2


class TestSearchNormalization:
    def test_accent_insensitive_match(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "cafe"}, {"name": "caf\u00e9"}]
        spec = SearchSpec(query="cafe", fields=("name",))

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 2

    def test_case_insensitive_match(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "HELLO"}, {"name": "world"}]
        spec = SearchSpec(query="hello", fields=("name",))

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 1
        assert result[0]["name"] == "HELLO"


class TestSearchExactMode:
    def test_exact_mode_matches_only_equal(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "alice"}, {"name": "alice bob"}]
        spec = SearchSpec(query="alice", fields=("name",), mode=SearchFieldMode.EXACT)

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 1
        assert result[0]["name"] == "alice"


class TestSearchMultiToken:
    def test_multi_token_matches_all_tokens(self, backend: MemorySearchBackend) -> None:
        items = [
            {"name": "Alice Johnson"},
            {"name": "Alice Smith"},
            {"name": "Bob Johnson"},
        ]
        spec = SearchSpec(query="alice", fields=("name",))

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 2
        assert {r["name"] for r in result} == {"Alice Johnson", "Alice Smith"}


class TestSearchNoneField:
    def test_none_field_value_skipped(self, backend: MemorySearchBackend) -> None:
        items = [{"name": None}, {"name": "Alice"}]
        spec = SearchSpec(query="alice", fields=("name",))

        result: list[dict[str, Any]] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 1
        assert result[0]["name"] == "Alice"


class TestSearchEdgeCases:
    def test_empty_query_returns_all(self, backend: MemorySearchBackend) -> None:
        items = [{"name": "A"}, {"name": "B"}]
        spec = SearchSpec(query="", fields=("name",))

        result: list[Any] = backend.apply_search(items, spec)  # type: ignore[assignment]

        assert len(result) == 2
