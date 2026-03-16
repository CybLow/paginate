"""Tests for LIKE/ILIKE branch coverage in FilterEngine.

Covers all four dispatch branches (contains, startswith, endswith,
complex glob fallback) for both case-sensitive and case-insensitive
LIKE operators via the FilterEngine.apply() path.
"""

from __future__ import annotations

from pypaginate.domain.specs import FilterSpec
from pypaginate.filtering.engine import FilterEngine


_ITEMS = [
    {"name": "Alice Johnson"},
    {"name": "Bob Smith"},
    {"name": "Charlie Brown"},
    {"name": "Diana Prince"},
]


class TestLikeContains:
    """LIKE %value% -- contains branch."""

    def test_contains_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="%John%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"

    def test_contains_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="%xyz%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestLikeStartsWith:
    """LIKE value% -- startswith branch."""

    def test_startswith_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="Alice%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"

    def test_startswith_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="Zebra%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestLikeEndsWith:
    """LIKE %value -- endswith branch."""

    def test_endswith_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="%Prince")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Diana Prince"

    def test_endswith_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="%Zebra")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestLikeComplexGlob:
    """LIKE with _ wildcards or inner % -- glob fallback branch."""

    def test_underscore_wildcard(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="B_b Smith")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Bob Smith"

    def test_underscore_with_percent(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="%B_b%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Bob Smith"

    def test_inner_percent(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="Alice%Johnson")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"

    def test_complex_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="like", value="Z_bra%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestIlikeContains:
    """ILIKE %value% -- case-insensitive contains branch."""

    def test_ilike_contains_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="%JOHN%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"

    def test_ilike_contains_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="%XYZ%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestIlikeStartsWith:
    """ILIKE value% -- case-insensitive startswith branch."""

    def test_ilike_startswith_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="ALICE%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Alice Johnson"

    def test_ilike_startswith_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="ZEBRA%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestIlikeEndsWith:
    """ILIKE %value -- case-insensitive endswith branch."""

    def test_ilike_endswith_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="%PRINCE")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Diana Prince"

    def test_ilike_endswith_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="%ZEBRA")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []


class TestIlikeComplexGlob:
    """ILIKE with _ wildcards -- case-insensitive glob fallback."""

    def test_ilike_underscore_wildcard(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="B_B SMITH")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Bob Smith"

    def test_ilike_underscore_with_percent(
        self, filter_engine: FilterEngine,
    ) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="%B_B%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert len(result) == 1
        assert result[0]["name"] == "Bob Smith"

    def test_ilike_complex_no_match(self, filter_engine: FilterEngine) -> None:
        spec = FilterSpec(field="name", operator="ilike", value="Z_BRA%")
        result = filter_engine.apply(_ITEMS, [spec])

        assert result == []
