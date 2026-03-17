"""Tests for OperatorRegistry."""

from __future__ import annotations

import pytest

from pypaginate.domain.exceptions import FilterError
from pypaginate.filtering.operators import Eq, Operator
from pypaginate.filtering.registry import OperatorRegistry, create_default_registry


_BUILTIN_NAMES = [
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "not_in",
    "contains",
    "starts_with",
    "ends_with",
    "like",
    "ilike",
    "regex",
    "between",
    "is_null",
    "is_not_null",
]


class TestGet:
    def test_returns_registered_operator(self) -> None:
        registry = OperatorRegistry()
        op = Eq()
        registry.register("eq", op)

        result = registry.get("eq")

        assert result is op

    def test_unknown_name_raises_filter_error(self) -> None:
        registry = OperatorRegistry()

        with pytest.raises(FilterError, match="Unknown filter operator"):
            registry.get("nonexistent")


class TestRegister:
    def test_adds_custom_operator(self) -> None:
        registry = OperatorRegistry()
        custom = Eq()
        registry.register("custom_eq", custom)

        result = registry.get("custom_eq")

        assert result is custom

    def test_override_existing_operator(self) -> None:
        registry = OperatorRegistry()
        original = Eq()
        override = Eq()
        registry.register("eq", original)

        registry.register("eq", override)

        assert registry.get("eq") is override

    def test_get_returns_overridden_operator(self) -> None:
        registry = create_default_registry()
        custom = Eq()

        registry.register("eq", custom)

        assert registry.get("eq") is custom


class TestDefaultRegistry:
    def test_has_all_17_builtins(self) -> None:
        registry = create_default_registry()

        for name in _BUILTIN_NAMES:
            op = registry.get(name)
            assert isinstance(op, Operator)

    @pytest.mark.parametrize("name", _BUILTIN_NAMES)
    def test_builtin_operator_exists(self, name: str) -> None:
        registry = create_default_registry()

        op = registry.get(name)

        assert op is not None
