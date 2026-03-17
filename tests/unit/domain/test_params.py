"""Tests for OffsetParams and CursorParams domain models."""

from __future__ import annotations

import pytest

from pypaginate.domain.exceptions import ValidationError
from pypaginate.domain.params import MAX_LIMIT, CursorParams, OffsetParams


DEFAULT_PAGE = 1
DEFAULT_LIMIT = 20


class TestOffsetParamsDefaults:
    def test_default_page_is_one(self) -> None:
        params = OffsetParams()

        assert params.page == DEFAULT_PAGE

    def test_default_limit_is_twenty(self) -> None:
        params = OffsetParams()

        assert params.limit == DEFAULT_LIMIT


class TestOffsetParamsOffset:
    @pytest.mark.parametrize(
        ("page", "limit", "expected_offset"),
        [
            (1, 10, 0),
            (2, 10, 10),
            (3, 25, 50),
            (1, 1, 0),
        ],
        ids=["first_page", "second_page", "third_page", "min_limit"],
    )
    def test_offset_computed_correctly(
        self,
        page: int,
        limit: int,
        expected_offset: int,
    ) -> None:
        params = OffsetParams(page=page, limit=limit)

        assert params.offset == expected_offset


class TestOffsetParamsValidation:
    @pytest.mark.parametrize(
        "page",
        [0, -1, -100],
        ids=["zero", "negative_one", "large_negative"],
    )
    def test_invalid_page_raises_validation_error(self, page: int) -> None:
        with pytest.raises(ValidationError, match="page must be >= 1"):
            OffsetParams(page=page)

    def test_limit_below_one_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="limit must be >= 1"):
            OffsetParams(limit=0)

    def test_limit_above_max_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="limit must not exceed"):
            OffsetParams(limit=MAX_LIMIT + 1)

    def test_limit_at_max_boundary_is_valid(self) -> None:
        params = OffsetParams(limit=MAX_LIMIT)

        assert params.limit == MAX_LIMIT


class TestOffsetParamsClamp:
    def test_clamp_beyond_total_returns_last_page(self) -> None:
        params = OffsetParams(page=10, limit=5)

        clamped = params.clamp(total=20)

        assert clamped.page == 4

    def test_clamp_within_range_returns_self(self) -> None:
        params = OffsetParams(page=2, limit=10)

        clamped = params.clamp(total=50)

        assert clamped is params

    def test_clamp_zero_total_returns_page_one(self) -> None:
        params = OffsetParams(page=5, limit=10)

        clamped = params.clamp(total=0)

        assert clamped.page == DEFAULT_PAGE

    def test_clamp_exact_boundary_returns_self(self) -> None:
        params = OffsetParams(page=2, limit=5)

        clamped = params.clamp(total=10)

        assert clamped is params


class TestOffsetParamsFrozen:
    def test_cannot_mutate_page(self) -> None:
        params = OffsetParams()

        with pytest.raises(Exception, match="frozen"):
            params.page = 2  # type: ignore[misc]


class TestCursorParamsDefaults:
    def test_default_after_is_none(self) -> None:
        params = CursorParams()

        assert params.after is None

    def test_default_before_is_none(self) -> None:
        params = CursorParams()

        assert params.before is None

    def test_default_limit_is_twenty(self) -> None:
        params = CursorParams()

        assert params.limit == DEFAULT_LIMIT


class TestCursorParamsValidation:
    def test_after_and_before_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError, match="mutually exclusive"):
            CursorParams(after="abc", before="xyz")

    def test_after_only_is_valid(self) -> None:
        params = CursorParams(after="abc123")

        assert params.after == "abc123"

    def test_before_only_is_valid(self) -> None:
        params = CursorParams(before="xyz789")

        assert params.before == "xyz789"

    def test_empty_cursor_string_is_valid(self) -> None:
        params = CursorParams(after="")

        assert params.after == ""
