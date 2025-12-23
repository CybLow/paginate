"""Predicate builders orchestrating the FilterEngine strategies."""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeGuard

from .jsonlogic_evaluator import evaluate_json_logic_rule


if TYPE_CHECKING:
    from .registry import FilterPredicate, OperatorRegistry


def _is_collection(value: object) -> TypeGuard[Collection[object]]:
    """Return True for non-string, non-bytes collection types.

    Args:
        value: Value to check.

    Returns:
        True if value is a collection (excluding strings/bytes).
    """
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return False
    return isinstance(value, Collection)


def _store_predicate(
    predicates: dict[str, FilterPredicate[object]],
    predicate: FilterPredicate[object],
) -> dict[str, str]:
    """Store predicate in a local map and return a JSON-logic pointer node.

    Args:
        predicates: Dictionary to store the predicate in.
        predicate: Predicate function to store.

    Returns:
        A JSON-logic variable reference node.
    """
    key = str(len(predicates))
    predicates[key] = predicate
    return {"var": f"predicates.{key}"}


def _rule_from_spec(
    spec: object,
    registry: OperatorRegistry[object],
    predicates: dict[str, FilterPredicate[object]],
) -> object:
    """Build a JSON-logic rule tree from a high-level filter spec.

    Args:
        spec: Filter specification (mapping, collection, or scalar).
        registry: Registry for building operator predicates.
        predicates: Dictionary to accumulate predicates.

    Returns:
        A JSON-logic compatible rule structure.
    """
    if isinstance(spec, Mapping):
        return _rule_from_mapping(spec, registry, predicates)
    if _is_collection(spec):
        return _rule_from_collection(spec, registry, predicates)
    return _store_predicate(predicates, registry.build("eq", spec))


def _rule_from_mapping(
    spec: Mapping[str, object],
    registry: OperatorRegistry[object],
    predicates: dict[str, FilterPredicate[object]],
) -> object:
    """Convert mapping specs into an implicit logical conjunction.

    Args:
        spec: Mapping of field -> filter specification.
        registry: Registry for building operator predicates.
        predicates: Dictionary to accumulate predicates.

    Returns:
        A JSON-logic AND node combining all field predicates.
    """
    nodes = [
        _store_predicate(predicates, registry.build(name, argument))
        for name, argument in spec.items()
    ]
    return _combine_nodes(nodes)


def _combine_nodes(nodes: Sequence[object]) -> object:
    """Combine rule nodes into a minimal JSON-logic expression.

    Args:
        nodes: Sequence of JSON-logic rule nodes.

    Returns:
        A single node (trivial case) or an AND combination.
    """
    if not nodes:
        return True
    if len(nodes) == 1:
        return nodes[0]
    return {"and": nodes}


def _rule_from_collection(
    spec: Collection[object],
    registry: OperatorRegistry[object],
    predicates: dict[str, FilterPredicate[object]],
) -> object:
    """Create a membership predicate from a collection spec.

    Args:
        spec: Collection of allowed values.
        registry: Registry for building operator predicates.
        predicates: Dictionary to accumulate predicates.

    Returns:
        A JSON-logic variable reference to the membership predicate.
    """
    predicate = registry.build("in", tuple(spec))
    return _store_predicate(predicates, predicate)


@dataclass(frozen=True)
class JsonLogicPredicateBuilder:
    """Compile filter specifications into predicates using JSON Logic semantics.

    Attributes:
        registry: Operator registry used to instantiate predicates.
    """

    registry: OperatorRegistry[object]

    def build(self, spec: object) -> FilterPredicate[object]:
        """Compile spec into a single predicate callable.

        Args:
            spec: Filter specification to compile.

        Returns:
            A predicate function that evaluates candidates.
        """
        rule, predicates = self._compile(spec)
        return _make_jsonlogic_predicate(rule, predicates)

    def _compile(
        self, spec: object
    ) -> tuple[object, dict[str, FilterPredicate[object]]]:
        """Return the JSON-logic rule and internal predicates mapping.

        Args:
            spec: Filter specification to compile.

        Returns:
            Tuple of (rule, predicates_dict).
        """
        predicates: dict[str, FilterPredicate[object]] = {}
        rule = _rule_from_spec(spec, self.registry, predicates)
        return rule, predicates


def _make_jsonlogic_predicate(
    rule: object, predicates: dict[str, FilterPredicate[object]]
) -> FilterPredicate[object]:
    """Create a predicate applying JSON-logic to stored predicate results.

    Args:
        rule: JSON-logic compatible structure.
        predicates: Mapping used to evaluate dynamic var nodes.

    Returns:
        A predicate function accepting a candidate value.
    """

    def _predicate(candidate: object) -> bool:
        values = {key: predicate(candidate) for key, predicate in predicates.items()}
        context = {"value": candidate, "predicates": values}
        return bool(evaluate_json_logic_rule(rule, context))

    return _predicate


__all__ = ["JsonLogicPredicateBuilder"]
