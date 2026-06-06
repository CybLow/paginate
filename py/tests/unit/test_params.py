"""Unit tests for OffsetParams / CursorParams (validation + derived offset)."""

from __future__ import annotations

import dataclasses

import pytest

from pypaginate import MAX_LIMIT, CursorParams, OffsetParams
from pypaginate.errors import PaginateError, ValidationError


pytestmark = pytest.mark.unit


class TestOffsetParams:
    def test_defaults_are_page_one_limit_twenty(self) -> None:
        params = OffsetParams()

        assert params.page == 1
        assert params.limit == 20

    def test_offset_is_zero_based_row_index(self) -> None:
        assert OffsetParams(page=1, limit=20).offset == 0
        assert OffsetParams(page=3, limit=10).offset == 20
        assert OffsetParams(page=5, limit=25).offset == 100

    def test_is_frozen(self) -> None:
        params = OffsetParams(page=2, limit=5)

        with pytest.raises(dataclasses.FrozenInstanceError):
            params.page = 9  # type: ignore[misc]

    @pytest.mark.parametrize("page", [0, -1, -100])
    def test_page_below_one_raises_validation_error(self, page: int) -> None:
        with pytest.raises(ValidationError, match="page must be >= 1"):
            OffsetParams(page=page, limit=20)

    def test_limit_below_one_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="limit must be >= 1"):
            OffsetParams(page=1, limit=0)

    def test_limit_above_max_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="must not exceed"):
            OffsetParams(page=1, limit=MAX_LIMIT + 1)

    def test_limit_at_max_is_accepted(self) -> None:
        params = OffsetParams(page=1, limit=MAX_LIMIT)

        assert params.limit == MAX_LIMIT

    def test_validation_error_is_a_paginate_error(self) -> None:
        with pytest.raises(PaginateError):
            OffsetParams(page=0)


class TestCursorParams:
    def test_defaults(self) -> None:
        params = CursorParams()

        assert params.limit == 20
        assert params.after is None
        assert params.before is None

    def test_after_only_is_accepted(self) -> None:
        assert CursorParams(limit=10, after="cursor").after == "cursor"

    def test_before_only_is_accepted(self) -> None:
        assert CursorParams(limit=10, before="cursor").before == "cursor"

    def test_after_and_before_are_mutually_exclusive(self) -> None:
        with pytest.raises(ValidationError, match="mutually exclusive"):
            CursorParams(limit=10, after="a", before="b")

    @pytest.mark.parametrize("limit", [0, MAX_LIMIT + 1])
    def test_limit_out_of_range_raises(self, limit: int) -> None:
        with pytest.raises(ValidationError):
            CursorParams(limit=limit)
