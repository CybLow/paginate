"""Tests for query tokens module."""

from __future__ import annotations

import pytest

from pypaginate.filters.search.parser import QueryTokens, TokenParser


class TestQueryTokens:
    """Test QueryTokens dataclass."""

    def test_empty_tokens(self) -> None:
        """Empty tokens should have no content."""
        tokens = QueryTokens(terms=(), phrases=(), raw=())
        assert not tokens.has_content()

    def test_tokens_with_terms(self) -> None:
        """Tokens with terms should have content."""
        tokens = QueryTokens(terms=("hello",), phrases=(), raw=())
        assert tokens.has_content()

    def test_tokens_with_phrases(self) -> None:
        """Tokens with phrases should have content."""
        tokens = QueryTokens(terms=(), phrases=("hello world",), raw=())
        assert tokens.has_content()

    def test_tokens_with_raw(self) -> None:
        """Tokens with raw should have content."""
        tokens = QueryTokens(terms=(), phrases=(), raw=("test",))
        assert tokens.has_content()

    def test_all_combined(self) -> None:
        """Tokens with all should have content."""
        tokens = QueryTokens(terms=("apple",), phrases=("red delicious",), raw=("app",))
        assert tokens.has_content()

    def test_terms_tuple(self) -> None:
        """Terms should be a tuple."""
        tokens = QueryTokens(terms=("a", "b"), phrases=(), raw=())
        assert tokens.terms == ("a", "b")

    def test_phrases_tuple(self) -> None:
        """Phrases should be a tuple."""
        tokens = QueryTokens(terms=(), phrases=("hello world",), raw=())
        assert tokens.phrases == ("hello world",)


class TestTokenParser:
    """Test TokenParser class."""

    @pytest.fixture
    def parser(self) -> TokenParser:
        """Create parser."""
        return TokenParser()

    def test_creation(self, parser: TokenParser) -> None:
        """Should create parser."""
        assert parser is not None

    def test_parse_returns_query_tokens(self, parser: TokenParser) -> None:
        """Parse should return QueryTokens."""
        result = parser.parse("hello", lambda x: x.lower())
        assert isinstance(result, QueryTokens)

    def test_parse_simple_term(self, parser: TokenParser) -> None:
        """Should parse simple term."""
        result = parser.parse("hello", lambda x: x.lower())
        assert result.has_content()

    def test_parse_multiple_terms(self, parser: TokenParser) -> None:
        """Should parse multiple terms."""
        result = parser.parse("hello world", lambda x: x.lower())
        assert result.has_content()

    def test_parse_quoted_phrase(self, parser: TokenParser) -> None:
        """Should parse quoted phrase."""
        result = parser.parse('"hello world"', lambda x: x.lower())
        assert result.has_content()
        assert len(result.phrases) >= 1

    def test_parse_empty(self, parser: TokenParser) -> None:
        """Should handle empty query."""
        result = parser.parse("", lambda x: x.lower())
        assert not result.has_content()

    def test_parse_whitespace_only(self, parser: TokenParser) -> None:
        """Should handle whitespace only query."""
        result = parser.parse("   ", lambda x: x.lower())
        assert not result.has_content()

    def test_parse_mixed_content(self, parser: TokenParser) -> None:
        """Should parse mixed content."""
        result = parser.parse('apple "red delicious"', lambda x: x.lower())
        assert result.has_content()
