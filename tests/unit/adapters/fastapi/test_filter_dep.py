"""Tests for FilterDep and FilterField."""

from __future__ import annotations

from pypaginate.adapters.fastapi.filters import FilterDep, FilterField
from pypaginate.domain.specs import FilterSpec


class _UserFilters(FilterDep):
    name: str | None = FilterField(None, operator="contains")
    age_min: int | None = FilterField(None, field="age", operator="gte")
    status: str | None = FilterField(None)


class TestFilterField:
    def test_default_operator_is_eq(self) -> None:
        dep = _UserFilters(status="active")
        specs = dep.to_specs()

        assert len(specs) == 1
        assert specs[0].operator == "eq"

    def test_custom_operator(self) -> None:
        dep = _UserFilters(name="alice")
        specs = dep.to_specs()

        assert specs[0].operator == "contains"

    def test_custom_field_name(self) -> None:
        dep = _UserFilters(age_min=18)
        specs = dep.to_specs()

        assert specs[0].field == "age"
        assert specs[0].operator == "gte"
        assert specs[0].value == 18


class TestFilterDep:
    def test_to_specs_skips_none_values(self) -> None:
        dep = _UserFilters()

        assert dep.to_specs() == []

    def test_to_specs_includes_set_values(self) -> None:
        dep = _UserFilters(name="alice", status="active")
        specs = dep.to_specs()

        assert len(specs) == 2
        fields = {s.field for s in specs}
        assert fields == {"name", "status"}

    def test_to_specs_with_custom_field_mapping(self) -> None:
        dep = _UserFilters(age_min=21)
        specs = dep.to_specs()

        assert specs[0] == FilterSpec(
            field="age",
            operator="gte",
            value=21,
        )

    def test_to_specs_empty_returns_empty_list(self) -> None:
        dep = _UserFilters(name=None, age_min=None, status=None)

        assert dep.to_specs() == []

    def test_multiple_fields(self) -> None:
        dep = _UserFilters(name="bob", age_min=25, status="active")
        specs = dep.to_specs()

        assert len(specs) == 3
