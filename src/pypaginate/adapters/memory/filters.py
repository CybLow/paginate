"""In-memory filter backend with inline operator dispatch.

Implements FilterBackend protocol for Python sequences.
Compiles filter specs into inlined predicate closures that
bypass operator.evaluate() method dispatch for common ops.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pypaginate.filtering.accessor import compile_accessor
from pypaginate.filtering.registry import OperatorRegistry, create_default_registry


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec

Predicate = Callable[[object], bool]


# Strategy map: operator name → inline predicate factory.
# Eliminates operator.evaluate() method dispatch overhead.
_INLINE: dict[str, Callable[..., Predicate]] = {
    "eq": lambda a, v: (lambda item: a(item) == v),
    "ne": lambda a, v: (lambda item: a(item) != v),
    "gt": lambda a, v: (lambda item: a(item) > v),
    "gte": lambda a, v: (lambda item: a(item) >= v),
    "lt": lambda a, v: (lambda item: a(item) < v),
    "lte": lambda a, v: (lambda item: a(item) <= v),
    "in": lambda a, v: (lambda item: a(item) in v),
    "not_in": lambda a, v: (lambda item: a(item) not in v),
    "is_null": lambda a, _v: (lambda item: a(item) is None),
    "is_not_null": lambda a, _v: (lambda item: a(item) is not None),
    "contains": lambda a, v: (lambda item: str(v) in str(a(item))),
    "starts_with": lambda a, v: (lambda item: str(a(item)).startswith(str(v))),
    "ends_with": lambda a, v: (lambda item: str(a(item)).endswith(str(v))),
    "empty": lambda a, _v: (lambda item: a(item) is None or a(item) == "" or a(item) == []),
    "not_empty": lambda a, _v: (
        lambda item: a(item) is not None and a(item) != "" and a(item) != []
    ),
    "exists": lambda _a, _v: (lambda _item: True),
}


class MemoryFilterBackend:
    """Filter backend for in-memory sequences."""

    __slots__ = ("_registry",)

    def __init__(self, registry: OperatorRegistry | None = None) -> None:
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
        if not filters:
            return list(items)
        compiled = _compile_filters(filters, self._registry)
        if len(compiled) == 1:
            pred = compiled[0]
            return [item for item in items if pred(item)]
        return [item for item in items if _matches_all(item, compiled)]


def _compile_filters(
    filters: Sequence[FilterSpec],
    registry: OperatorRegistry,
) -> list[Predicate]:
    """Compile filter specs into inlined predicate closures."""
    predicates: list[Predicate] = []
    for spec in filters:
        accessor = compile_accessor(spec.field)
        predicates.append(_compile_pred(accessor, spec, registry))
    return predicates


def _compile_pred(
    accessor: Callable[[object], object],
    spec: Any,
    registry: OperatorRegistry,
) -> Predicate:
    """Compile a single spec: inline if possible, else delegate."""
    factory = _INLINE.get(spec.operator)
    if factory is not None:
        return factory(accessor, spec.value)
    operator = registry.get(spec.operator)

    def _fallback(item: object) -> bool:
        return operator.evaluate(accessor(item), spec.value)  # type: ignore[no-any-return]

    return _fallback


def _matches_all(item: object, preds: list[Predicate]) -> bool:
    """Check if item satisfies all predicates (no genexpr)."""
    for p in preds:  # noqa: SIM110
        if not p(item):
            return False
    return True


__all__ = ["MemoryFilterBackend"]
