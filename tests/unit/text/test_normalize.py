"""Tests for text normalization."""

from __future__ import annotations

import pytest

from pypaginate.text.normalize import clear_normalize_cache, normalize_text


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("cafe\u0301", "cafe"),
        ("\u00e9", "e"),
        ("\u00f1", "n"),
    ],
    ids=["combining_accent", "precomposed_e_acute", "precomposed_n_tilde"],
)
def test_accent_removal(input_text: str, expected: str) -> None:
    result = normalize_text(input_text)

    assert result == expected


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("HELLO", "hello"),
        ("HeLLo WoRLd", "hello world"),
    ],
    ids=["all_upper", "mixed_case"],
)
def test_case_folding(input_text: str, expected: str) -> None:
    result = normalize_text(input_text)

    assert result == expected


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("  hello  ", "hello"),
        ("  hello   world  ", "hello world"),
        ("\thello\n", "hello"),
    ],
    ids=["leading_trailing", "multiple_spaces", "tabs_newlines"],
)
def test_whitespace_collapse(input_text: str, expected: str) -> None:
    result = normalize_text(input_text)

    assert result == expected


class TestCombined:
    def test_accent_and_case_normalized(self) -> None:
        result = normalize_text("Caf\u00e9 R\u00e9sum\u00e9")

        assert result == "cafe resume"

    def test_empty_string_returns_empty(self) -> None:
        result = normalize_text("")

        assert result == ""


class TestCache:
    def test_clear_cache_is_callable(self) -> None:
        normalize_text("cached_value")

        clear_normalize_cache()

    def test_cached_result_matches_fresh(self) -> None:
        clear_normalize_cache()
        first = normalize_text("Hello World")
        second = normalize_text("Hello World")

        assert first == second == "hello world"

    def test_cache_eviction_after_max_entries(self) -> None:
        """Fill cache past 8192 entries; verify normalize still works."""
        clear_normalize_cache()

        for i in range(8200):
            normalize_text(f"entry_{i}")

        result = normalize_text("Post Eviction")

        assert result == "post eviction"
