"""Runtime helpers bridging json-logic with strict typing constraints.

This adapter évite les mutations globales et rétablit l'état après évaluation.
Compatible mypy strict: on ne manipule pas directement json_logic.__dict__ tel quel.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from functools import reduce
from typing import TYPE_CHECKING, Any, TypeGuard, cast

import json_logic


if TYPE_CHECKING:
    from types import ModuleType

JsonLogicData = Mapping[str, Any]


class _CompatDict(dict[str, Any]):
    """Dict avec keys() -> list[str] pour compat json-logic."""

    def keys(self) -> list[str]:  # type: ignore[override]
        return list(super().keys())


def _is_json_sequence(value: object) -> TypeGuard[Sequence[object]]:
    """Check if value is a JSON-compatible sequence.

    Args:
        value: Value to check.

    Returns:
        True if value is a sequence excluding strings/bytes.
    """
    return isinstance(value, Sequence) and not isinstance(
        value, str | bytes | bytearray | memoryview
    )


def _prepare_rule(rule: object) -> object:
    """Prepare a rule for json-logic evaluation.

    Args:
        rule: JSON-logic rule structure.

    Returns:
        Prepared rule with _CompatDict instances.
    """
    if isinstance(rule, Mapping):
        return _CompatDict({str(k): _prepare_rule(v) for k, v in rule.items()})
    if _is_json_sequence(rule):
        return [_prepare_rule(item) for item in rule]
    return rule


def _prepare_value(value: Any) -> Any:
    """Prepare a value for json-logic evaluation.

    Args:
        value: Value to prepare.

    Returns:
        Prepared value with _CompatDict instances.
    """
    if isinstance(value, Mapping):
        return _CompatDict({str(k): _prepare_value(v) for k, v in value.items()})
    return value


def _prepare_data(data: JsonLogicData) -> _CompatDict:
    """Prepare data mapping for json-logic evaluation.

    Args:
        data: Input data mapping.

    Returns:
        A _CompatDict with prepared values.
    """
    prepared: dict[str, Any] = {}
    for key, value in data.items():
        prepared[str(key)] = _prepare_value(value)
    return _CompatDict(prepared)


def _module_dict(mod: ModuleType | object) -> MutableMapping[str, object]:
    """Get module __dict__ bypassing typeshed annotations.

    Args:
        mod: Module object.

    Returns:
        The module's __dict__ as a mutable mapping.
    """
    # Bypass l'annotation typeshed: on récupère le vrai dict Python.
    d = cast("object", object.__getattribute__(mod, "__dict__"))
    return cast("MutableMapping[str, object]", d)


@contextmanager
def _patched_json_logic_env() -> Iterator[None]:
    """Context manager patching json_logic module temporarily.

    Yields:
        None. Patches are active within the context.
    """
    d = _module_dict(json_logic)
    prev_reduce = d.get("reduce")
    prev_dict = d.get("dict")
    try:
        d["reduce"] = reduce
        d["dict"] = _CompatDict
        yield
    finally:
        if prev_reduce is not None:
            d["reduce"] = prev_reduce
        else:
            d.pop("reduce", None)
        if prev_dict is not None:
            d["dict"] = prev_dict
        else:
            d.pop("dict", None)


@dataclass(frozen=True)
class JsonLogicAdapter:
    """Évalue une règle json-logic dans un environnement isolé."""

    @staticmethod
    def evaluate(rule: object, data: JsonLogicData) -> object:
        """Evaluate a JSON-logic rule against a data context.

        Args:
            rule: JSON-serializable structure representing the rule.
            data: Mapping providing variables consumed by the rule.

        Returns:
            The raw result produced by ``json_logic.jsonLogic``.
        """
        prepared_rule = _prepare_rule(rule)
        prepared_data = _prepare_data(data)
        with _patched_json_logic_env():
            return json_logic.jsonLogic(prepared_rule, prepared_data)


# Facade fonctionnelle
_adapter = JsonLogicAdapter()


def evaluate_json_logic_rule(rule: object, data: JsonLogicData) -> object:
    """Convenience wrapper around :class:`JsonLogicAdapter` evaluation.

    Args:
        rule: JSON-logic rule.
        data: Variable mapping for rule evaluation.

    Returns:
        Evaluation result.
    """
    return _adapter.evaluate(rule, data)


__all__ = ["JsonLogicAdapter", "evaluate_json_logic_rule"]
