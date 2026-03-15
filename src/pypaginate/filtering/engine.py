"""Filter engine applying filter specs to in-memory sequences.

Stateless engine that receives an OperatorRegistry via constructor
and evaluates FilterSpec predicates against items.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.specs import FilterSpec
from pypaginate.filtering import accessor
from pypaginate.filtering.registry import OperatorRegistry


T = TypeVar("T")


class FilterEngine:
    """Apply filter specifications to in-memory sequences.

    Args:
        registry: Operator registry for looking up operators.
    """

    def __init__(self, registry: OperatorRegistry) -> None:
        self._registry = registry

    def apply(
        self,
        items: Sequence[T],
        filters: Sequence[FilterSpec],
    ) -> list[T]:
        """Apply all filters to items.

        Args:
            items: Source sequence to filter.
            filters: Filter specifications to apply.

        Returns:
            Filtered list of items matching all specs.
        """
        if not filters:
            return list(items)
        and_specs, or_specs = _partition_specs(filters)
        return [item for item in items if _item_matches(item, and_specs, or_specs, self._registry)]


def _partition_specs(
    filters: Sequence[FilterSpec],
) -> tuple[list[FilterSpec], list[FilterSpec]]:
    """Split filters into AND and OR groups."""
    and_specs = [f for f in filters if f.logic == FilterLogic.AND]
    or_specs = [f for f in filters if f.logic == FilterLogic.OR]
    return and_specs, or_specs


def _item_matches(
    item: object,
    and_specs: list[FilterSpec],
    or_specs: list[FilterSpec],
    registry: OperatorRegistry,
) -> bool:
    """Check whether a single item satisfies all filter groups."""
    and_pass = all(_evaluate_spec(item, s, registry) for s in and_specs)
    if not and_pass:
        return False
    if not or_specs:
        return True
    return any(_evaluate_spec(item, s, registry) for s in or_specs)


def _evaluate_spec(
    item: object,
    spec: FilterSpec,
    registry: OperatorRegistry,
) -> bool:
    """Evaluate a single FilterSpec against an item."""
    field_value = accessor.get_value(item, spec.field)
    operator = registry.get(spec.operator)
    return operator.evaluate(field_value, spec.value)


__all__ = ["FilterEngine"]
