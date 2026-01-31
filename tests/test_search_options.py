"""Tests for filters/search/options.py module.

This module tests the search options validation and resolution functionality.
"""

import re

import pytest

from pypaginate.exceptions import SearchQueryError
from pypaginate.filters.search.conditions import SearchMode
from pypaginate.filters.search.options import (
    DEFAULT_SEARCH_MODE,
    ResolvedOptions,
    SearchOptionSet,
    resolve_options,
)


# Default pattern for tests
DEFAULT_PATTERN = re.compile(r"^[A-Z]{2,3}-\d+$")


class TestSearchOptionSet:
    """Tests for SearchOptionSet dataclass."""

    def test_from_mapping_empty_options(self) -> None:
        """Empty options should use defaults."""
        result = SearchOptionSet.from_mapping({}, default_pattern=DEFAULT_PATTERN)

        assert result.mode == DEFAULT_SEARCH_MODE
        assert result.prefix is False
        assert result.id_fields == ()
        assert result.id_token_regex == DEFAULT_PATTERN

    def test_from_mapping_with_mode_enum(self) -> None:
        """Mode as SearchMode enum should be accepted."""
        result = SearchOptionSet.from_mapping(
            {"mode": SearchMode.OR}, default_pattern=DEFAULT_PATTERN
        )
        assert result.mode == SearchMode.OR

    def test_from_mapping_with_mode_string(self) -> None:
        """Mode as string should be converted to enum."""
        result = SearchOptionSet.from_mapping({"mode": "or"}, default_pattern=DEFAULT_PATTERN)
        assert result.mode == SearchMode.OR

    def test_from_mapping_with_prefix_true(self) -> None:
        """Prefix option should be accepted."""
        result = SearchOptionSet.from_mapping({"prefix": True}, default_pattern=DEFAULT_PATTERN)
        assert result.prefix is True

    def test_from_mapping_with_prefix_false(self) -> None:
        """Prefix false should be accepted."""
        result = SearchOptionSet.from_mapping({"prefix": False}, default_pattern=DEFAULT_PATTERN)
        assert result.prefix is False

    def test_from_mapping_with_id_fields_list(self) -> None:
        """id_fields as list should be converted to tuple."""
        result = SearchOptionSet.from_mapping(
            {"id_fields": ["id", "code"]}, default_pattern=DEFAULT_PATTERN
        )
        assert result.id_fields == ("id", "code")

    def test_from_mapping_with_id_fields_tuple(self) -> None:
        """id_fields as tuple should be preserved."""
        result = SearchOptionSet.from_mapping(
            {"id_fields": ("id", "code")}, default_pattern=DEFAULT_PATTERN
        )
        assert result.id_fields == ("id", "code")

    def test_from_mapping_with_custom_pattern(self) -> None:
        """Custom id_token_regex should override default."""
        custom_pattern = re.compile(r"^\d+$")
        result = SearchOptionSet.from_mapping(
            {"id_token_regex": custom_pattern}, default_pattern=DEFAULT_PATTERN
        )
        assert result.id_token_regex == custom_pattern

    def test_from_mapping_with_all_options(self) -> None:
        """All options together should work."""
        custom_pattern = re.compile(r"^\d{3}$")
        result = SearchOptionSet.from_mapping(
            {
                "mode": SearchMode.AND,
                "prefix": True,
                "id_fields": ["id"],
                "id_token_regex": custom_pattern,
            },
            default_pattern=DEFAULT_PATTERN,
        )
        assert result.mode == SearchMode.AND
        assert result.prefix is True
        assert result.id_fields == ("id",)
        assert result.id_token_regex == custom_pattern


class TestResolveOptions:
    """Tests for resolve_options function."""

    def test_resolve_empty_options(self) -> None:
        """Empty options should produce valid resolved options."""
        result = resolve_options({}, default_pattern=DEFAULT_PATTERN)

        assert isinstance(result, ResolvedOptions)
        assert result.mode == DEFAULT_SEARCH_MODE
        assert isinstance(result.context, dict)
        assert result.context["prefix"] is False
        assert result.context["id_fields"] == ()
        assert result.context["id_token_regex"] == DEFAULT_PATTERN

    def test_resolve_with_mode(self) -> None:
        """Mode should be resolved correctly."""
        result = resolve_options({"mode": "or"}, default_pattern=DEFAULT_PATTERN)
        assert result.mode == SearchMode.OR

    def test_resolved_context_has_all_keys(self) -> None:
        """Resolved context should have all required keys."""
        result = resolve_options(
            {"prefix": True, "id_fields": ["code"]}, default_pattern=DEFAULT_PATTERN
        )
        context = result.context

        assert "prefix" in context
        assert "id_fields" in context
        assert "id_token_regex" in context
        assert context["prefix"] is True
        assert context["id_fields"] == ("code",)


class TestModeCoercion:
    """Tests for mode option coercion and validation."""

    def test_invalid_mode_string_raises_error(self) -> None:
        """Invalid mode string should raise SearchQueryError."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping({"mode": "invalid"}, default_pattern=DEFAULT_PATTERN)

        assert "Unsupported search mode" in str(exc_info.value)

    def test_invalid_mode_type_raises_error(self) -> None:
        """Non-string, non-enum mode should raise SearchQueryError."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping({"mode": 123}, default_pattern=DEFAULT_PATTERN)

        assert "Unsupported search mode" in str(exc_info.value)


class TestPrefixCoercion:
    """Tests for prefix option coercion."""

    def test_invalid_prefix_type_raises_error(self) -> None:
        """Non-boolean prefix should raise SearchQueryError."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping({"prefix": "yes"}, default_pattern=DEFAULT_PATTERN)

        assert "prefix must be a boolean" in str(exc_info.value)

    def test_prefix_integer_raises_error(self) -> None:
        """Integer prefix should raise SearchQueryError."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping({"prefix": 1}, default_pattern=DEFAULT_PATTERN)

        assert "prefix must be a boolean" in str(exc_info.value)


class TestIdFieldsCoercion:
    """Tests for id_fields option coercion."""

    def test_id_fields_string_raises_error(self) -> None:
        """String id_fields should raise SearchQueryError (must be sequence)."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping({"id_fields": "id"}, default_pattern=DEFAULT_PATTERN)

        assert "id_fields must be a sequence" in str(exc_info.value)

    def test_id_fields_with_non_string_item_raises_error(self) -> None:
        """id_fields with non-string items should raise SearchQueryError."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping(
                {"id_fields": ["id", 123]}, default_pattern=DEFAULT_PATTERN
            )

        assert "id_fields must contain only strings" in str(exc_info.value)

    def test_id_fields_empty_list(self) -> None:
        """Empty list should result in empty tuple."""
        result = SearchOptionSet.from_mapping({"id_fields": []}, default_pattern=DEFAULT_PATTERN)
        assert result.id_fields == ()


class TestPatternCoercion:
    """Tests for id_token_regex option coercion."""

    def test_invalid_pattern_type_raises_error(self) -> None:
        """Non-pattern id_token_regex should raise SearchQueryError."""
        with pytest.raises(SearchQueryError) as exc_info:
            SearchOptionSet.from_mapping(
                {"id_token_regex": r"^\d+$"}, default_pattern=DEFAULT_PATTERN
            )

        assert "id_token_regex must be a compiled regular expression" in str(exc_info.value)


class TestDefaultSearchMode:
    """Tests for default search mode constant."""

    def test_default_search_mode_is_and(self) -> None:
        """Default search mode should be AND."""
        assert DEFAULT_SEARCH_MODE == SearchMode.AND
