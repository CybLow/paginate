"""Tests for domain enums — member names and value uniqueness."""

from __future__ import annotations

from enum import Enum

import pytest

from pypaginate.domain.enums import (
    FilterLogic,
    FuzzyMode,
    NullsPosition,
    OverflowStrategy,
    SearchFieldMode,
    SortDirection,
)


_ENUM_MEMBERS = [
    (OverflowStrategy, {"CLAMP", "EMPTY"}),
    (SortDirection, {"ASC", "DESC"}),
    (NullsPosition, {"FIRST", "LAST"}),
    (FilterLogic, {"AND", "OR"}),
    (SearchFieldMode, {"PREFIX", "CONTAINS", "EXACT"}),
    (FuzzyMode, {"EXACT", "FUZZY", "TOKEN_SORT"}),
]


class TestEnumMembers:
    @pytest.mark.parametrize(
        ("enum_cls", "expected_names"),
        _ENUM_MEMBERS,
        ids=lambda v: v.__name__ if isinstance(v, type) else "",
    )
    def test_has_expected_members(
        self,
        enum_cls: type[Enum],
        expected_names: set[str],
    ) -> None:
        actual = {m.name for m in enum_cls}

        assert actual == expected_names


class TestEnumValuesDistinct:
    @pytest.mark.parametrize(
        ("enum_cls", "expected_names"),
        _ENUM_MEMBERS,
        ids=lambda v: v.__name__ if isinstance(v, type) else "",
    )
    def test_values_are_unique(
        self,
        enum_cls: type[Enum],
        expected_names: set[str],
    ) -> None:
        assert set(enum_cls.__members__.keys()) == expected_names
        values = [m.value for m in enum_cls]

        assert len(values) == len(set(values))
