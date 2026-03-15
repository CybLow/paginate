"""Operator registry mapping names to operator instances.

Provides a default registry pre-populated with all built-in operators.
Custom operators can be registered at runtime.
"""

from __future__ import annotations

from pypaginate.domain.exceptions import FilterError
from pypaginate.filtering.operators import (
    Between,
    Contains,
    EndsWith,
    Eq,
    Gt,
    Gte,
    ILike,
    In,
    IsNotNull,
    IsNull,
    Like,
    Lt,
    Lte,
    Ne,
    NotIn,
    Operator,
    Regex,
    StartsWith,
)


class OperatorRegistry:
    """Registry mapping operator names to Operator instances."""

    def __init__(self) -> None:
        self._operators: dict[str, Operator] = {}

    def register(self, name: str, operator: Operator) -> None:
        """Register an operator under the given name.

        Args:
            name: Operator name (e.g. ``"eq"``).
            operator: An object implementing the Operator protocol.
        """
        self._operators[name] = operator

    def get(self, name: str) -> Operator:
        """Look up an operator by name.

        Args:
            name: Operator name.

        Returns:
            The registered Operator instance.

        Raises:
            FilterError: If no operator is registered under *name*.
        """
        operator = self._operators.get(name)
        if operator is None:
            _raise_unknown(name, list(self._operators))
        return operator  # type: ignore[return-value]


def _raise_unknown(name: str, known: list[str]) -> None:
    """Raise FilterError for an unknown operator name."""
    msg = f"Unknown filter operator '{name}'"
    raise FilterError(msg, details={"known": known})


def create_default_registry() -> OperatorRegistry:
    """Create an OperatorRegistry with all built-in operators.

    Returns:
        A fully populated OperatorRegistry.
    """
    registry = OperatorRegistry()
    for name, operator in _BUILTINS.items():
        registry.register(name, operator)
    return registry


_BUILTINS: dict[str, Operator] = {
    "eq": Eq(),
    "ne": Ne(),
    "gt": Gt(),
    "gte": Gte(),
    "lt": Lt(),
    "lte": Lte(),
    "in": In(),
    "not_in": NotIn(),
    "contains": Contains(),
    "starts_with": StartsWith(),
    "ends_with": EndsWith(),
    "like": Like(),
    "ilike": ILike(),
    "between": Between(),
    "is_null": IsNull(),
    "is_not_null": IsNotNull(),
    "regex": Regex(),
}


__all__ = ["OperatorRegistry", "create_default_registry"]
