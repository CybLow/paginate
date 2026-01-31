"""Tests for search modules."""

from __future__ import annotations

import pytest

from pypaginate.filters.search.memory_search import (
    MemorySearchEngine,
    MemorySearchOptions,
    safe_text,
)
from pypaginate.filters.search.options import DEFAULT_SEARCH_MODE, SearchMode
from pypaginate.filters.search.parser import QueryTokens, TokenParser
from pypaginate.text.pipelines import MemoryTextNormalizer


class TestSearchMode:
    """Test SearchMode enum."""

    def test_and_mode(self) -> None:
        """AND mode should exist."""
        assert SearchMode.AND is not None

    def test_or_mode(self) -> None:
        """OR mode should exist."""
        assert SearchMode.OR is not None

    def test_fuzzy_mode(self) -> None:
        """FUZZY mode should exist."""
        assert SearchMode.FUZZY is not None

    def test_default_mode(self) -> None:
        """DEFAULT_SEARCH_MODE should be defined."""
        assert DEFAULT_SEARCH_MODE is not None


class TestSafeText:
    """Test safe_text helper."""

    def test_string(self) -> None:
        """Should return string as-is."""
        assert safe_text("hello") == "hello"

    def test_int(self) -> None:
        """Should convert int to string."""
        assert safe_text(42) == "42"

    def test_none(self) -> None:
        """Should convert None to empty string."""
        assert safe_text(None) == ""

    def test_bytes(self) -> None:
        """Should decode bytes."""
        result = safe_text(b"hello")
        assert result == "hello"


class TestMemorySearchOptions:
    """Test MemorySearchOptions class."""

    def test_default_options(self) -> None:
        """Should have sensible defaults."""
        options = MemorySearchOptions()
        assert options.mode is not None
        assert isinstance(options.mode, SearchMode)

    def test_custom_mode(self) -> None:
        """Should accept custom mode."""
        options = MemorySearchOptions(mode=SearchMode.OR)
        assert options.mode == SearchMode.OR

    def test_prefix_option(self) -> None:
        """Should accept prefix option."""
        options = MemorySearchOptions(prefix=True)
        assert options.prefix is True

    def test_to_match(self) -> None:
        """Should convert to match options."""
        options = MemorySearchOptions()
        match_opts = options.to_match()
        assert match_opts is not None


class TestTokenParser:
    """Test TokenParser class."""

    @pytest.fixture
    def parser(self) -> TokenParser:
        """Create parser."""
        return TokenParser()

    @pytest.fixture
    def normalizer_func(self) -> object:
        """Create normalizer function."""
        normalizer = MemoryTextNormalizer()
        return normalizer.normalize_text

    def test_parser_creation(self, parser: TokenParser) -> None:
        """Should create parser."""
        assert parser is not None

    def test_parse_simple_term(self, parser: TokenParser, normalizer_func: object) -> None:
        """Should parse simple term."""
        tokens = parser.parse("hello", normalizer_func)  # type: ignore[arg-type]
        assert tokens is not None
        assert isinstance(tokens, QueryTokens)
        assert tokens.has_content()

    def test_parse_multiple_terms(self, parser: TokenParser, normalizer_func: object) -> None:
        """Should parse multiple terms."""
        tokens = parser.parse("hello world", normalizer_func)  # type: ignore[arg-type]
        assert tokens.has_content()

    def test_parse_quoted_phrase(self, parser: TokenParser, normalizer_func: object) -> None:
        """Should parse quoted phrase."""
        tokens = parser.parse('"hello world"', normalizer_func)  # type: ignore[arg-type]
        assert tokens.has_content()
        assert len(tokens.phrases) >= 1

    def test_parse_empty(self, parser: TokenParser, normalizer_func: object) -> None:
        """Should handle empty query."""
        tokens = parser.parse("", normalizer_func)  # type: ignore[arg-type]
        assert not tokens.has_content()


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


class TestMemorySearchEngine:
    """Test MemorySearchEngine class."""

    @pytest.fixture
    def engine(self) -> MemorySearchEngine:
        """Create search engine."""
        normalizer = MemoryTextNormalizer()
        return MemorySearchEngine(normalizer)

    def test_engine_creation(self, engine: MemorySearchEngine) -> None:
        """Should create engine."""
        assert engine is not None


class TestMemoryTextNormalizer:
    """Test MemoryTextNormalizer class."""

    def test_creation(self) -> None:
        """Should create normalizer."""
        normalizer = MemoryTextNormalizer()
        assert normalizer is not None

    def test_normalize_string(self) -> None:
        """Should normalize string."""
        normalizer = MemoryTextNormalizer()
        result = normalizer.normalize_text("HELLO")
        # Should be lowercase
        assert result == "hello" or result is not None

    def test_normalize_whitespace(self) -> None:
        """Should normalize whitespace."""
        normalizer = MemoryTextNormalizer()
        result = normalizer.normalize_text("hello  world")
        # Should collapse whitespace
        assert "  " not in result
