"""Unit tests for the exception hierarchy, the alias, and structured payloads."""

from __future__ import annotations

import pytest

from pypaginate import (
    ConfigurationError,
    FilterError,
    FilterValidationError,
    PaginateError,
    PaginationError,
    SearchError,
    SearchQueryError,
    SortError,
    ValidationError,
)


pytestmark = pytest.mark.unit


class TestHierarchy:
    @pytest.mark.parametrize(
        "error_type",
        [
            ConfigurationError,
            FilterError,
            SearchError,
            SortError,
            ValidationError,
        ],
    )
    def test_direct_subclasses_of_base(self, error_type: type[PaginateError]) -> None:
        assert issubclass(error_type, PaginateError)

    def test_filter_validation_error_subclasses_filter_error(self) -> None:
        assert issubclass(FilterValidationError, FilterError)

    def test_search_query_error_subclasses_search_error(self) -> None:
        assert issubclass(SearchQueryError, SearchError)

    def test_base_is_an_exception(self) -> None:
        assert issubclass(PaginateError, Exception)


class TestPaginationAlias:
    def test_alias_is_the_base_class(self) -> None:
        assert PaginationError is PaginateError

    def test_subclasses_catchable_via_alias(self) -> None:
        with pytest.raises(PaginationError):
            raise FilterError("boom")


class TestStructuredPayloads:
    def test_base_details_default_to_empty_mapping(self) -> None:
        error = PaginateError("oops")

        assert error.details == {}
        assert str(error) == "oops"

    def test_details_are_preserved(self) -> None:
        error = PaginateError("oops", details={"reason": "x"})

        assert error.details == {"reason": "x"}

    def test_filter_error_carries_field(self) -> None:
        error = FilterError("bad", field="age", details={"op": "eq"})

        assert error.field == "age"
        assert error.details == {"op": "eq"}

    def test_validation_error_carries_field(self) -> None:
        error = ValidationError("bad", field="page")

        assert error.field == "page"
        assert error.details == {}

    def test_field_defaults_to_none(self) -> None:
        assert FilterError("bad").field is None
        assert ValidationError("bad").field is None
