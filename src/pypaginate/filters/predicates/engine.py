"""Compile filtering specifications into executable predicates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from .builder import JsonLogicPredicateBuilder
from .field_accessor import FieldAccessor
from .registry import OperatorRegistry


if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .registry import FilterPredicate


ItemT = TypeVar("ItemT")


@dataclass(frozen=True)
class CompiledFilter(Generic[ItemT]):
    """Pair a field accessor with its predicate.

    Attributes:
        accessor: Accessor resolving field values on items.
        predicate: Callable evaluating the resolved value.
    """

    accessor: FieldAccessor
    predicate: FilterPredicate[object]

    def matches(self, item: ItemT) -> bool:
        """Return True when item matches the predicate.

        Args:
            item: Item to evaluate against the filter.

        Returns:
            True if the item passes the filter predicate.
        """
        return self.predicate(self.accessor.resolve(item))


class FilterEngine(Generic[ItemT]):
    """Compile declarative filter specifications into callables."""

    def __init__(self, registry: OperatorRegistry[object] | None = None) -> None:
        """Initialize the engine with an optional operator registry.

        Args:
            registry: Custom operator registry. Uses default if None.
        """
        self._registry = registry or OperatorRegistry.default()
        self._builder = JsonLogicPredicateBuilder(self._registry)

    def apply(self, items: Sequence[ItemT], filters: Mapping[str, object]) -> list[ItemT]:
        """Filter items using a mapping of path -> filter spec.

        Args:
            items: Sequence of items to filter.
            filters: Mapping of field paths to filter specifications.

        Returns:
            List of items matching all filter criteria.
        """
        compiled = [self._compile(path, spec) for path, spec in filters.items() if spec is not None]
        return [item for item in items if self._matches(item, compiled)]

    def _compile(self, path: str, spec: object) -> CompiledFilter[ItemT]:
        """Compile a single filter spec for the provided path.

        Args:
            path: Dotted path to the field to filter on.
            spec: Filter specification for this field.

        Returns:
            A CompiledFilter ready for evaluation.
        """
        accessor = FieldAccessor.from_string(path)
        predicate = self._build_predicate(spec)
        return CompiledFilter(accessor, predicate)

    def _build_predicate(self, spec: object) -> FilterPredicate[object]:
        """Build the predicate callable for spec.

        Args:
            spec: Filter specification to compile.

        Returns:
            A predicate function for evaluation.
        """
        return self._builder.build(spec)

    @staticmethod
    def _matches(item: ItemT, compiled: Sequence[CompiledFilter[ItemT]]) -> bool:
        """Return True when item matches all compiled filters.

        Args:
            item: Item to evaluate.
            compiled: Sequence of compiled filters to apply.

        Returns:
            True if item passes all filters.
        """
        return all(f.matches(item) for f in compiled)


def filter_items(
    items: Sequence[ItemT],
    filters: Mapping[str, object],
    *,
    registry: OperatorRegistry[object] | None = None,
) -> list[ItemT]:
    """Apply declarative filters to an in-memory sequence.

    Args:
        items: Sequence of candidate items to filter.
        filters: Mapping of ``path -> filter`` specifications.
        registry: Optional operator registry (default operators otherwise).

    Returns:
        Filtered list of items matching all compiled predicates.
    """

    engine: FilterEngine[ItemT] = FilterEngine(registry=registry)
    return engine.apply(items, filters)


__all__ = ["CompiledFilter", "FilterEngine", "filter_items"]
