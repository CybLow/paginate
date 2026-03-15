"""Tests for SearchEngine."""

from __future__ import annotations

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.domain.specs import SearchSpec
from pypaginate.search.engine import SearchEngine


class TestSearchContains:
    def test_contains_match_returns_matching_item(
        self,
        search_engine: SearchEngine,
        search_items: list[dict[str, object]],
    ) -> None:
        spec = SearchSpec(query="alice", fields=("name",))
        result = search_engine.apply(search_items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"


class TestSearchPrefix:
    def test_prefix_match_returns_matching_item(
        self,
        search_engine: SearchEngine,
        search_items: list[dict[str, object]],
    ) -> None:
        spec = SearchSpec(query="bob", fields=("name",), mode=SearchFieldMode.PREFIX)
        result = search_engine.apply(search_items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "Bob Smith"


class TestSearchMultiField:
    def test_multi_field_search_finds_all_matches(self, search_engine: SearchEngine) -> None:
        items = [
            {"name": "Bob", "bio": "Alice is a friend"},
            {"name": "Alice", "bio": "Software developer"},
        ]
        spec = SearchSpec(query="alice", fields=("name", "bio"))

        assert len(search_engine.apply(items, spec)) == 2


class TestSearchExact:
    def test_exact_mode_returns_exact_match(self, search_engine: SearchEngine) -> None:
        items = [{"name": "alice"}, {"name": "alice johnson"}]
        spec = SearchSpec(query="alice", fields=("name",), mode=SearchFieldMode.EXACT)

        result = search_engine.apply(items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "alice"


class TestSearchFuzzy:
    def test_fuzzy_mode_returns_approximate_matches(self, search_engine: SearchEngine) -> None:
        items = [{"name": "Alice"}, {"name": "Alce"}, {"name": "Zebra"}]
        spec = SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=50)

        result = search_engine.apply(items, spec)

        assert "Alice" in {r["name"] for r in result}
        assert "Zebra" not in {r["name"] for r in result}


class TestSearchMultiToken:
    def test_multi_token_requires_all_tokens(self, search_engine: SearchEngine) -> None:
        items = [
            {"name": "Alice Test"},
            {"name": "Alice Other"},
            {"name": "Bob Test"},
        ]
        spec = SearchSpec(query="alice test", fields=("name",))
        result = search_engine.apply(items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "Alice Test"


class TestSearchRelevance:
    def test_multi_token_match_scores_higher(self, search_engine: SearchEngine) -> None:
        items = [
            {"name": "Alice Other"},
            {"name": "Alice Johnson"},
        ]
        spec = SearchSpec(query="alice johnson", fields=("name",))
        result = search_engine.apply(items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"


class TestSearchEdgeCases:
    def test_no_matches_returns_empty_list(
        self,
        search_engine: SearchEngine,
        search_items: list[dict[str, object]],
    ) -> None:
        spec = SearchSpec(query="zzzznotfound", fields=("name",))
        assert search_engine.apply(search_items, spec) == []

    def test_empty_query_returns_all_items(
        self,
        search_engine: SearchEngine,
        search_items: list[dict[str, object]],
    ) -> None:
        spec = SearchSpec(query="", fields=("name",))
        assert len(search_engine.apply(search_items, spec)) == len(search_items)

    def test_empty_items_returns_empty_list(self, search_engine: SearchEngine) -> None:
        spec = SearchSpec(query="alice", fields=("name",))
        assert search_engine.apply([], spec) == []

    def test_single_item_match(self, search_engine: SearchEngine) -> None:
        spec = SearchSpec(query="alice", fields=("name",))
        assert len(search_engine.apply([{"name": "Alice"}], spec)) == 1

    def test_special_characters_in_query(
        self,
        search_engine: SearchEngine,
        search_items: list[dict[str, object]],
    ) -> None:
        spec = SearchSpec(query="@example.com", fields=("email",))
        assert len(search_engine.apply(search_items, spec)) >= 1

    def test_non_string_field_returns_zero_score(self, search_engine: SearchEngine) -> None:
        items = [{"name": 12345}, {"name": "Alice"}]
        spec = SearchSpec(query="alice", fields=("name",))
        result = search_engine.apply(items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_missing_field_returns_zero_score(self, search_engine: SearchEngine) -> None:
        items = [{"other": "x"}, {"name": "Alice"}]
        spec = SearchSpec(query="alice", fields=("name",))
        result = search_engine.apply(items, spec)

        assert len(result) == 1
        assert result[0]["name"] == "Alice"
