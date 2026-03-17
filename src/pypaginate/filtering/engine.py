"""Filter engine applying filter specs to in-memory sequences.

Compiles filter specs into fast predicate closures ONCE,
then applies them N times without per-item overhead.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from fnmatch import fnmatch
from typing import TypeVar

from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.specs import FilterGroup, FilterSpec
from pypaginate.filtering.accessor import compile_accessor
from pypaginate.filtering.like import classify_like, like_to_glob
from pypaginate.filtering.regex import compile_pattern
from pypaginate.filtering.registry import OperatorRegistry


T = TypeVar("T")

_STRING_OPS = frozenset({"contains", "starts_with", "ends_with"})


class FilterEngine:
    """Apply filter specifications to in-memory sequences.

    Args:
        registry: Operator registry for looking up operators.
    """

    __slots__ = ("_registry",)

    def __init__(self, registry: OperatorRegistry) -> None:
        self._registry = registry

    def apply(
        self,
        items: Sequence[T],
        filters: Sequence[FilterSpec] | FilterGroup,
    ) -> list[T]:
        """Apply filters to items. Accepts flat list or nested FilterGroup.

        Args:
            items: Source sequence to filter.
            filters: FilterSpec list or FilterGroup (via And/Or builders).

        Returns:
            Filtered list of items matching all specs.
        """
        if isinstance(filters, FilterGroup):
            pred = _compile_group(filters, self._registry)
            return [item for item in items if pred(item)]
        if not filters:
            return list(items)
        and_preds, or_preds = _compile_all(filters, self._registry)
        return [item for item in items if _matches(item, and_preds, or_preds)]


def _compile_all(
    filters: Sequence[FilterSpec],
    registry: OperatorRegistry,
) -> tuple[list[Callable[[object], bool]], list[Callable[[object], bool]]]:
    """Partition and compile all filter specs."""
    and_preds: list[Callable[[object], bool]] = []
    or_preds: list[Callable[[object], bool]] = []
    for spec in filters:
        pred = _compile_predicate(spec, registry)
        if spec.logic == FilterLogic.AND:
            and_preds.append(pred)
        else:
            or_preds.append(pred)
    return and_preds, or_preds


def _compile_predicate(
    spec: FilterSpec,
    registry: OperatorRegistry,
) -> Callable[[object], bool]:
    """Compile a FilterSpec into a fast predicate closure."""
    accessor = compile_accessor(spec.field)
    op_name = spec.operator
    value = spec.value

    if op_name == "regex":
        return _compile_regex(accessor, value)
    if op_name == "like":
        return _compile_like(accessor, value)
    if op_name == "ilike":
        return _compile_ilike(accessor, value)
    if op_name in _STRING_OPS:
        value = str(value)

    operator = registry.get(op_name)

    def _predicate(item: object) -> bool:
        return operator.evaluate(accessor(item), value)

    return _predicate


def _compile_regex(
    accessor: Callable[[object], object],
    value: object,
) -> Callable[[object], bool]:
    """Compile a regex predicate with pre-compiled pattern."""
    from pypaginate.domain.exceptions import FilterError

    pattern_str = str(value)
    try:
        compiled = compile_pattern(pattern_str)
    except Exception as exc:
        raise FilterError(
            f"Invalid regex pattern: '{pattern_str}'",
            details={"pattern": pattern_str, "error": str(exc)},
        ) from exc

    def _pred(item: object) -> bool:
        return bool(compiled.search(str(accessor(item))))

    return _pred


def _compile_like(
    accessor: Callable[[object], object],
    value: object,
) -> Callable[[object], bool]:
    """Compile LIKE using string methods when possible."""
    pattern = str(value)
    kind, inner = classify_like(pattern)
    if kind == "contains":
        return lambda item: inner in str(accessor(item))
    if kind == "startswith":
        return lambda item: str(accessor(item)).startswith(inner)
    if kind == "endswith":
        return lambda item: str(accessor(item)).endswith(inner)
    glob = like_to_glob(pattern)
    return lambda item: fnmatch(str(accessor(item)), glob)


def _compile_ilike(
    accessor: Callable[[object], object],
    value: object,
) -> Callable[[object], bool]:
    """Compile case-insensitive LIKE using string methods."""
    pattern = str(value)
    kind, inner = classify_like(pattern)
    lower_inner = inner.lower()
    if kind == "contains":
        return lambda item: lower_inner in str(accessor(item)).lower()
    if kind == "startswith":
        return lambda item: str(accessor(item)).lower().startswith(lower_inner)
    if kind == "endswith":
        return lambda item: str(accessor(item)).lower().endswith(lower_inner)
    glob = like_to_glob(pattern).lower()
    return lambda item: fnmatch(str(accessor(item)).lower(), glob)


def _matches(
    item: object,
    and_preds: list[Callable[[object], bool]],
    or_preds: list[Callable[[object], bool]],
) -> bool:
    """Check whether a single item satisfies all predicate groups."""
    for p in and_preds:
        if not p(item):
            return False
    if not or_preds:
        return True
    for p in or_preds:  # noqa: SIM110
        if p(item):
            return True
    return False


def _compile_group(
    group: FilterGroup,
    registry: OperatorRegistry,
) -> Callable[[object], bool]:
    """Compile a nested FilterGroup into a recursive predicate."""
    child_preds = []
    for condition in group.conditions:
        if isinstance(condition, FilterGroup):
            child_preds.append(_compile_group(condition, registry))
        else:
            child_preds.append(_compile_predicate(condition, registry))

    if group.logic is FilterLogic.AND:

        def _and(item: object) -> bool:
            for p in child_preds:  # noqa: SIM110
                if not p(item):
                    return False
            return True

        return _and

    def _or(item: object) -> bool:
        for p in child_preds:  # noqa: SIM110
            if p(item):
                return True
        return False

    return _or


__all__ = ["FilterEngine"]
