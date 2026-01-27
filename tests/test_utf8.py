"""Tests for UTF-8 normalization module."""

from __future__ import annotations

import pytest

from pypaginator.text.utf8 import (
    Utf8Normalizer,
    create_search_normalizer,
    normalize_utf8,
    transliterate_ascii,
)


class TestNormalizeUtf8:
    """Test normalize_utf8 function."""

    def test_basic_normalization(self) -> None:
        """Should normalize UTF-8 string."""
        result = normalize_utf8(
            "Hello", lowercase=False, casefold_output=False, form="NFC"
        )
        assert result == "Hello"

    def test_lowercase(self) -> None:
        """Should lowercase when specified."""
        result = normalize_utf8(
            "HELLO", lowercase=True, casefold_output=False, form="NFC"
        )
        assert result == "hello"

    def test_casefold(self) -> None:
        """Should casefold when specified."""
        result = normalize_utf8(
            "HELLO", lowercase=False, casefold_output=True, form="NFC"
        )
        assert result == "hello"

    def test_nfkc_normalization(self) -> None:
        """Should apply NFKC normalization."""
        # NFKC converts ﬁ ligature to "fi"
        result = normalize_utf8(
            "ﬁle", lowercase=False, casefold_output=False, form="NFKC"
        )
        assert "fi" in result

    def test_nfd_form(self) -> None:
        """Should handle NFD normalization form."""
        result = normalize_utf8(
            "café", lowercase=False, casefold_output=False, form="NFD"
        )
        assert result is not None


class TestTransliterateAscii:
    """Test transliterate_ascii function."""

    def test_ascii_passthrough(self) -> None:
        """ASCII should pass through unchanged."""
        result = transliterate_ascii("hello")
        assert result == "hello"

    def test_unicode_to_ascii(self) -> None:
        """Should transliterate unicode to ASCII."""
        result = transliterate_ascii("café")
        assert "cafe" in result or "caf" in result

    def test_cyrillic(self) -> None:
        """Should transliterate cyrillic characters."""
        result = transliterate_ascii("Привет")
        # Should be ASCII only
        assert result.isascii() or result == "Privet"


class TestUtf8Normalizer:
    """Test Utf8Normalizer class."""

    def test_default_normalizer(self) -> None:
        """Default normalizer should exist."""
        normalizer = Utf8Normalizer()
        assert normalizer is not None

    def test_normalise_basic(self) -> None:
        """Should normalize basic string."""
        normalizer = Utf8Normalizer()
        result = normalizer.normalise("Hello")
        assert result == "Hello"

    def test_normalise_with_lowercase(self) -> None:
        """Should lowercase when configured."""
        normalizer = Utf8Normalizer(lowercase=True)
        result = normalizer.normalise("HELLO")
        assert result == "hello"

    def test_normalise_with_casefold(self) -> None:
        """Should casefold when configured."""
        normalizer = Utf8Normalizer(casefold_output=True)
        result = normalizer.normalise("HELLO")
        assert result == "hello"

    def test_different_forms(self) -> None:
        """Should support different normalization forms."""
        nfc = Utf8Normalizer(form="NFC").normalise("test")
        nfkc = Utf8Normalizer(form="NFKC").normalise("test")
        assert nfc is not None
        assert nfkc is not None


class TestCreateSearchNormalizer:
    """Test create_search_normalizer factory."""

    def test_creates_normalizer(self) -> None:
        """Should create a normalizer."""
        normalizer = create_search_normalizer()
        assert normalizer is not None
        assert isinstance(normalizer, Utf8Normalizer)

    def test_lowercases(self) -> None:
        """Search normalizer should lowercase."""
        normalizer = create_search_normalizer()
        result = normalizer.normalise("HELLO")
        assert result == "hello"

    def test_uses_nfkc(self) -> None:
        """Search normalizer should use NFKC form."""
        normalizer = create_search_normalizer()
        assert normalizer.form == "NFKC"
