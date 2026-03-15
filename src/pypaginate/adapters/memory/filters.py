"""In-memory filter backend delegating to the filtering engine.

Implements FilterBackend protocol for Python sequences.
Uses the operator registry and field accessor to evaluate predicates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypaginate.filtering.accessor import get_value
from pypaginate.filtering.registry import OperatorRegistry, create_default_registry


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec


class MemoryFilterBackend:
    """Filter backend for in-memory sequences.

    Satisfies ``FilterBackend`` protocol by evaluating filter specs
    against items using the operator registry.
    """

    def __init__(self, registry: OperatorRegistry | None = None) -> None:
        """Initialize with an optional operator registry.

        Args:
            registry: Custom registry. Uses default if None.
        """
        self._registry = registry or create_default_registry()

    def apply_filters(
        self,
        query: object,
        filters: Sequence[FilterSpec],
    ) -> object:
        """Apply filter specs to a sequence.

        Args:
            query: A Python sequence of items.
            filters: Filter specifications to apply.

        Returns:
            Filtered list of items matching all specs.
        """
        items: Sequence[object] = query  # type: ignore[assignment]
        return [item for item in items if self._matches(item, filters)]

    def _matches(self, item: object, filters: Sequence[FilterSpec]) -> bool:
        """Check if an item matches all filter specs."""
        return all(self._evaluate(item, f) for f in filters)

    def _evaluate(self, item: object, spec: FilterSpec) -> bool:
        """Evaluate a single filter spec against an item."""
        value = get_value(item, spec.field)
        operator = self._registry.get(spec.operator)
        return operator.evaluate(value, spec.value)


__all__ = ["MemoryFilterBackend"]
