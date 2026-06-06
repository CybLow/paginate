"""Unit tests for the _native.normalize_text bounded process cache."""

from __future__ import annotations

import pytest

from pypaginate import _native


pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Start every test from a clean normalize cache (and clean up after)."""
    _native.clear_normalize_cache()


class TestNormalizeText:
    def test_lowercases_and_strips_accents(self) -> None:
        assert _native.normalize_text("Héllo WORLD") == "hello world"

    def test_is_idempotent(self) -> None:
        once = _native.normalize_text("Café")

        assert _native.normalize_text(once) == once


class TestCache:
    def test_first_call_populates_cache(self) -> None:
        _native.normalize_text("Stockholm")

        assert "Stockholm" in _native._NORM_CACHE

    def test_cached_value_is_returned(self) -> None:
        first = _native.normalize_text("Göteborg")
        second = _native.normalize_text("Göteborg")

        assert first == second
        assert _native._NORM_CACHE["Göteborg"] == first

    def test_clear_empties_the_cache(self) -> None:
        _native.normalize_text("Malmö")
        assert _native._NORM_CACHE

        _native.clear_normalize_cache()

        assert _native._NORM_CACHE == {}

    def test_cache_is_bounded(self) -> None:
        limit = _native._NORM_CACHE_MAX

        for index in range(limit + 50):
            _native.normalize_text(f"value-{index}")

        assert len(_native._NORM_CACHE) <= limit
