"""Tests for the exception hierarchy."""

from __future__ import annotations

import pytest

from pypaginate.domain.exceptions import (
    ConfigurationError,
    FilterError,
    FilterValidationError,
    PaginationError,
    SearchError,
    SearchQueryError,
    SortError,
    ValidationError,
)


class TestPaginationErrorIsBase:
    def test_is_base_exception(self) -> None:
        assert issubclass(PaginationError, Exception)


_DIRECT_SUBCLASSES = [
    ConfigurationError,
    FilterError,
    SearchError,
    SortError,
    ValidationError,
]


class TestDirectSubclasses:
    @pytest.mark.parametrize("exc_cls", _DIRECT_SUBCLASSES)
    def test_inherits_from_pagination_error(self, exc_cls: type) -> None:
        assert issubclass(exc_cls, PaginationError)


class TestConfigurationErrorAttributes:
    def test_message_stored(self) -> None:
        err = ConfigurationError("bad config", details={"key": "val"})

        assert str(err) == "bad config"
        assert err.details == {"key": "val"}

    def test_details_default_empty(self) -> None:
        err = ConfigurationError("msg")

        assert err.details == {}


class TestFilterErrorAttributes:
    def test_field_and_details(self) -> None:
        err = FilterError("fail", field="age", details={"op": "gt"})

        assert err.field == "age"
        assert err.details == {"op": "gt"}

    def test_field_default_none(self) -> None:
        err = FilterError("fail")

        assert err.field is None


class TestFilterValidationChain:
    def test_inherits_filter_and_pagination(self) -> None:
        assert issubclass(FilterValidationError, FilterError)
        assert issubclass(FilterValidationError, PaginationError)

    def test_instance_check(self) -> None:
        err = FilterValidationError("bad filter", field="x")

        assert isinstance(err, FilterError)
        assert isinstance(err, PaginationError)


class TestSearchQueryChain:
    def test_inherits_search_and_pagination(self) -> None:
        assert issubclass(SearchQueryError, SearchError)
        assert issubclass(SearchQueryError, PaginationError)


class TestValidationErrorAttributes:
    def test_field_and_details(self) -> None:
        err = ValidationError("invalid", field="name", details={"v": 1})

        assert err.field == "name"
        assert err.details == {"v": 1}

    def test_defaults(self) -> None:
        err = ValidationError("invalid")

        assert err.field is None
        assert err.details == {}


class TestSearchErrorAttributes:
    def test_details_stored(self) -> None:
        err = SearchError("search fail", details={"query": "abc"})

        assert str(err) == "search fail"
        assert err.details == {"query": "abc"}

    def test_details_default_empty(self) -> None:
        err = SearchError("fail")

        assert err.details == {}


class TestSortErrorAttributes:
    def test_details_stored(self) -> None:
        err = SortError("sort fail", details={"field": "age"})

        assert err.details == {"field": "age"}
