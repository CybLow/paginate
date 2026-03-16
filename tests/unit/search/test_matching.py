"""Tests for search matching utilities (pre-normalized inputs)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.search.matching import fuzzy_score, matches_field
from pypaginate.text.normalize import normalize_text


class TestMatchesFieldContains:
    def test_contains_returns_true_for_substring(self) -> None:
        result = matches_field("hello world", "world", SearchFieldMode.CONTAINS)

        assert result is True

    def test_contains_returns_false_for_no_match(self) -> None:
        result = matches_field("hello", "xyz", SearchFieldMode.CONTAINS)

        assert result is False


class TestMatchesFieldPrefix:
    def test_prefix_returns_true_when_starts_with(self) -> None:
        result = matches_field("hello world", "hello", SearchFieldMode.PREFIX)

        assert result is True

    def test_prefix_returns_false_for_mid_match(self) -> None:
        result = matches_field("say hello", "hello", SearchFieldMode.PREFIX)

        assert result is False


class TestMatchesFieldExact:
    def test_exact_returns_true_for_equal(self) -> None:
        result = matches_field("hello", "hello", SearchFieldMode.EXACT)

        assert result is True

    def test_exact_returns_false_for_partial(self) -> None:
        result = matches_field("hello world", "hello", SearchFieldMode.EXACT)

        assert result is False


class TestMatchesFieldNormalized:
    @pytest.mark.parametrize(
        ("value", "token"),
        [("HELLO", "hello"), ("Hello", "HELLO"), ("hElLo", "HeLlO")],
        ids=["upper-lower", "mixed-upper", "mixed-mixed"],
    )
    def test_case_insensitive_after_normalize(self, value: str, token: str) -> None:
        result = matches_field(
            normalize_text(value),
            normalize_text(token),
            SearchFieldMode.EXACT,
        )

        assert result is True


class TestFuzzyScore:
    def test_similar_strings_return_positive_score(self) -> None:
        score = fuzzy_score(
            normalize_text("hello"),
            normalize_text("helo"),
            threshold=50,
        )

        assert score > 0

    def test_dissimilar_strings_return_zero(self) -> None:
        score = fuzzy_score(
            normalize_text("hello"),
            normalize_text("zzzzz"),
            threshold=90,
        )

        assert score == 0

    def test_empty_value_returns_zero(self) -> None:
        score = fuzzy_score("", normalize_text("hello"), threshold=50)

        assert score == 0

    def test_empty_token_returns_zero(self) -> None:
        score = fuzzy_score(normalize_text("hello"), "", threshold=50)

        assert score == 0


class TestComputeScoreFallback:
    def test_fallback_returns_high_score_for_substring(self) -> None:
        with patch("pypaginate.search.matching._HAS_RAPIDFUZZ", False):
            score = fuzzy_score(
                normalize_text("hello world"),
                normalize_text("hello"),
                threshold=50,
            )

            assert score == 100

    def test_fallback_returns_zero_for_no_match(self) -> None:
        with patch("pypaginate.search.matching._HAS_RAPIDFUZZ", False):
            score = fuzzy_score(
                normalize_text("hello"),
                normalize_text("xyz"),
                threshold=50,
            )

            assert score == 0


class TestFuzzyScoreTokenSort:
    def test_token_sort_returns_positive_for_reordered(self) -> None:
        score = fuzzy_score(
            normalize_text("alice johnson"),
            normalize_text("johnson alice"),
            threshold=50,
            fuzzy_mode=FuzzyMode.TOKEN_SORT,
        )

        assert score > 0

    def test_token_sort_returns_zero_for_dissimilar(self) -> None:
        score = fuzzy_score(
            normalize_text("hello"),
            normalize_text("zzzzz"),
            threshold=90,
            fuzzy_mode=FuzzyMode.TOKEN_SORT,
        )

        assert score == 0
