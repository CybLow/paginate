"""Tests for LIKE pattern utilities — classification, glob conversion, matching."""

from __future__ import annotations

import pytest

from pypaginate.filtering.like import classify_like, like_to_glob, match_ilike, match_like


# -- classify_like -----------------------------------------------------------


class TestClassifyLikeContains:
    """Pattern %x% should classify as 'contains'."""

    def test_wrapped_percent_returns_contains(self) -> None:
        kind, inner = classify_like("%hello%")

        assert kind == "contains"
        assert inner == "hello"

    def test_single_char_inner(self) -> None:
        kind, inner = classify_like("%a%")

        assert kind == "contains"
        assert inner == "a"


class TestClassifyLikeStartswith:
    """Pattern x% should classify as 'startswith'."""

    def test_trailing_percent_returns_startswith(self) -> None:
        kind, inner = classify_like("hello%")

        assert kind == "startswith"
        assert inner == "hello"


class TestClassifyLikeEndswith:
    """Pattern %x should classify as 'endswith'."""

    def test_leading_percent_returns_endswith(self) -> None:
        kind, inner = classify_like("%hello")

        assert kind == "endswith"
        assert inner == "hello"


class TestClassifyLikeComplex:
    """Patterns with _ wildcards or inner % are 'complex'."""

    def test_underscore_returns_complex(self) -> None:
        kind, _inner = classify_like("h_llo")

        assert kind == "complex"

    def test_underscore_with_percent_returns_complex(self) -> None:
        kind, _inner = classify_like("%h_llo%")

        assert kind == "complex"

    def test_inner_percent_returns_complex(self) -> None:
        kind, _inner = classify_like("he%lo")

        assert kind == "complex"

    def test_no_wildcards_returns_complex(self) -> None:
        kind, inner = classify_like("hello")

        assert kind == "complex"
        assert inner == "hello"


# -- like_to_glob ------------------------------------------------------------


class TestLikeToGlob:
    @pytest.mark.parametrize(
        ("pattern", "expected"),
        [
            ("%hello%", "*hello*"),
            ("hello%", "hello*"),
            ("%hello", "*hello"),
            ("h_llo", "h?llo"),
            ("%h_llo%", "*h?llo*"),
            ("hello", "hello"),
        ],
        ids=[
            "contains",
            "startswith",
            "endswith",
            "single_char",
            "mixed",
            "exact",
        ],
    )
    def test_conversion(self, pattern: str, expected: str) -> None:
        result = like_to_glob(pattern)

        assert result == expected


# -- match_like --------------------------------------------------------------


class TestMatchLikeContains:
    def test_substring_match(self) -> None:
        assert match_like("hello world", "%world%") is True

    def test_substring_no_match(self) -> None:
        assert match_like("hello world", "%xyz%") is False


class TestMatchLikeStartswith:
    def test_prefix_match(self) -> None:
        assert match_like("hello world", "hello%") is True

    def test_prefix_no_match(self) -> None:
        assert match_like("hello world", "world%") is False


class TestMatchLikeEndswith:
    def test_suffix_match(self) -> None:
        assert match_like("hello world", "%world") is True

    def test_suffix_no_match(self) -> None:
        assert match_like("hello world", "%hello") is False


class TestMatchLikeComplex:
    def test_underscore_single_char(self) -> None:
        assert match_like("hat", "h_t") is True

    def test_underscore_no_match(self) -> None:
        assert match_like("hoot", "h_t") is False

    def test_no_wildcards_exact(self) -> None:
        assert match_like("hello", "hello") is True

    def test_no_wildcards_mismatch(self) -> None:
        assert match_like("hello", "world") is False


# -- match_ilike -------------------------------------------------------------


class TestMatchIlikeContains:
    def test_case_insensitive_contains(self) -> None:
        assert match_ilike("Hello World", "%WORLD%") is True

    def test_case_insensitive_contains_no_match(self) -> None:
        assert match_ilike("Hello World", "%XYZ%") is False


class TestMatchIlikeStartswith:
    def test_case_insensitive_startswith(self) -> None:
        assert match_ilike("Hello World", "HELLO%") is True

    def test_case_insensitive_startswith_no_match(self) -> None:
        assert match_ilike("Hello World", "WORLD%") is False


class TestMatchIlikeEndswith:
    def test_case_insensitive_endswith(self) -> None:
        assert match_ilike("Hello World", "%WORLD") is True

    def test_case_insensitive_endswith_no_match(self) -> None:
        assert match_ilike("Hello World", "%HELLO") is False


class TestMatchIlikeComplex:
    def test_case_insensitive_underscore(self) -> None:
        assert match_ilike("HAT", "h_t") is True

    def test_case_insensitive_underscore_no_match(self) -> None:
        assert match_ilike("HOOT", "h_t") is False

    def test_case_insensitive_exact(self) -> None:
        assert match_ilike("HELLO", "hello") is True
