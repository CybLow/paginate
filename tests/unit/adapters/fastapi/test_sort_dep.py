"""Tests for SortDep."""

from __future__ import annotations

from pypaginate.adapters.fastapi.sorting import SortDep
from pypaginate.domain.enums import SortDirection


class TestSortDep:
    def test_asc_field(self) -> None:
        dep = SortDep(sort="name")
        specs = dep.to_specs()

        assert len(specs) == 1
        assert specs[0].field == "name"
        assert specs[0].direction is SortDirection.ASC

    def test_desc_with_minus_prefix(self) -> None:
        dep = SortDep(sort="-age")
        specs = dep.to_specs()

        assert specs[0].field == "age"
        assert specs[0].direction is SortDirection.DESC

    def test_multiple_fields_comma_separated(self) -> None:
        dep = SortDep(sort="name,-age")
        specs = dep.to_specs()

        assert len(specs) == 2
        assert specs[0].field == "name"
        assert specs[0].direction is SortDirection.ASC
        assert specs[1].field == "age"
        assert specs[1].direction is SortDirection.DESC

    def test_plus_prefix_is_asc(self) -> None:
        dep = SortDep(sort="+name")
        specs = dep.to_specs()

        assert specs[0].field == "name"
        assert specs[0].direction is SortDirection.ASC

    def test_none_sort_returns_empty(self) -> None:
        dep = SortDep(sort=None)

        assert dep.to_specs() == []

    def test_empty_string_returns_empty(self) -> None:
        dep = SortDep(sort="")

        assert dep.to_specs() == []
