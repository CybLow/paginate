"""Tests for text API module."""

from __future__ import annotations

from pypaginate.text.api import (
    FilterTextNormalizer,
    MemoryTextNormalizer,
    SqlTextNormalizer,
    Utf8Normalizer,
    create_search_normalizer,
    normalize_utf8,
)


class TestFilterTextNormalizer:
    """Test FilterTextNormalizer class."""

    def test_creation(self) -> None:
        """Should create normalizer."""
        normalizer = FilterTextNormalizer(case_sensitive=False)
        assert normalizer is not None

    def test_normalize_string(self) -> None:
        """Should normalize string input."""
        normalizer = FilterTextNormalizer(case_sensitive=False)
        result = normalizer("Hello World")
        assert result is not None
        assert isinstance(result, str)

    def test_case_sensitive(self) -> None:
        """Case sensitive option should work."""
        normalizer = FilterTextNormalizer(case_sensitive=True)
        result = normalizer("HELLO")
        assert result is not None


class TestTextApiExports:
    """Test that text API exports work."""

    def test_memory_text_normalizer(self) -> None:
        """MemoryTextNormalizer should be importable."""
        normalizer = MemoryTextNormalizer()
        result = normalizer.normalize_text("hello")
        assert result is not None

    def test_sql_text_normalizer(self) -> None:
        """SqlTextNormalizer should be importable."""
        normalizer = SqlTextNormalizer()
        result = normalizer.normalize_text("hello")
        assert result is not None

    def test_utf8_normalizer(self) -> None:
        """Utf8Normalizer should be importable."""
        normalizer = Utf8Normalizer(lowercase=True)
        result = normalizer.normalise("HELLO")
        assert result == "hello"

    def test_normalize_utf8_function(self) -> None:
        """normalize_utf8 should work."""
        result = normalize_utf8("Hello", lowercase=True, casefold_output=False, form="NFC")
        assert result == "hello"

    def test_create_search_normalizer_function(self) -> None:
        """create_search_normalizer should work."""
        normalizer = create_search_normalizer()
        assert normalizer is not None
        result = normalizer.normalise("HELLO")
        assert result == "hello"
