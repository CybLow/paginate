"""Resolve dotted paths using :mod:`jmespath` expressions."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, is_dataclass
from typing import TypeAlias

import jmespath
from jmespath.parser import ParsedResult


# Concrete alias for jmespath vendor type - exposed at runtime
CompiledExpression: TypeAlias = ParsedResult

_SCALAR_TYPES = (str, bytes, bytearray, memoryview, int, float, bool, type(None))


def _parse_tokens(raw_path: str) -> list[int | str]:
    """Split a dotted path into tokens, coercing numeric segments to ints.

    Args:
        raw_path: Dotted path (e.g. ``a.b.0.c``).

    Returns:
        A list of path tokens (``str`` or ``int``).
    """
    tokens: list[int | str] = []
    for segment in raw_path.split("."):
        if not segment:
            continue
        tokens.append(int(segment) if segment.lstrip("-").isdigit() else segment)
    return tokens


def _token_fragment(token: int | str, *, first: bool) -> str:
    """Render a token fragment suitable for jmespath syntax.

    Args:
        token: Token to render (int or string).
        first: Whether this is the first token in the path.

    Returns:
        A jmespath-compatible string fragment.
    """
    if isinstance(token, int):
        return f"[{token}]"
    if token.isidentifier():
        return ("" if first else ".") + token
    return f"[{json.dumps(token)}]"


def _format_tokens(tokens: Sequence[int | str]) -> str:
    """Convert tokens into a jmespath expression string.

    Args:
        tokens: Sequence of path tokens.

    Returns:
        A jmespath expression string.
    """
    fragments = [_token_fragment(token, first=index == 0) for index, token in enumerate(tokens)]
    expression = "".join(fragments)
    return expression or "@"


def _compile_expression(tokens: Sequence[int | str]) -> CompiledExpression:
    """Compile tokens into a jmespath expression.

    Args:
        tokens: Sequence of path tokens.

    Returns:
        A compiled jmespath expression.
    """
    return jmespath.compile(_format_tokens(tokens))


def _is_scalar(value: object) -> bool:
    """Return True for scalar-like values that are not containers.

    Args:
        value: Value to check.

    Returns:
        True if value is a scalar type.
    """
    return isinstance(value, _SCALAR_TYPES)


def _from_dataclass(value: object) -> dict[str, object] | None:
    """Convert a dataclass instance to a plain dict.

    Avoids importing dataclasses.fields/asdict for performance and to
    preserve strict typing constraints.

    Args:
        value: Object to convert.

    Returns:
        Dictionary representation or None if not a dataclass.
    """
    if not is_dataclass(value) or isinstance(value, type):
        return None
    fields_map = getattr(value, "__dataclass_fields__", None)
    if not isinstance(fields_map, dict):
        return None
    return {name: _to_data(getattr(value, name)) for name in fields_map}


def _from_mapping(value: object) -> dict[str, object] | None:
    """Convert a mapping to a JSON-compatible dict, or return None.

    Args:
        value: Object to convert.

    Returns:
        Dictionary representation or None if not a mapping.
    """
    if not isinstance(value, Mapping):
        return None
    return {str(key): _to_data(val) for key, val in value.items()}


def _from_sequence(value: object) -> list[object] | None:
    """Convert a sequence to a JSON-compatible list, or return None.

    Args:
        value: Object to convert.

    Returns:
        List representation or None if not a sequence.
    """
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray | memoryview):
        return [_to_data(item) for item in value]
    return None


def _from_object(value: object) -> object:
    """Fallback conversion using __dict__ when available.

    Args:
        value: Object to convert.

    Returns:
        Dictionary representation from __dict__ or original value.
    """
    if hasattr(value, "__dict__"):
        return {
            name: _to_data(item) for name, item in vars(value).items() if not name.startswith("_")
        }
    return value


def _to_data(value: object) -> object:
    """Convert heterogeneous Python values into JSON-compatible data.

    Args:
        value: Value to convert.

    Returns:
        JSON-compatible representation.
    """
    if _is_scalar(value):
        return value
    for converter in (_from_dataclass, _from_mapping, _from_sequence):
        converted = converter(value)
        if converted is not None:
            return converted
    return _from_object(value)


@dataclass(frozen=True)
class FieldAccessor:
    """Resolve dotted paths on heterogeneous containers."""

    expression: CompiledExpression
    """Compiled :mod:`jmespath` expression."""

    @classmethod
    def from_string(cls, raw_path: str) -> FieldAccessor:
        """Create an accessor from a dotted path string.

        Args:
            raw_path: Dotted path notation (e.g. "user.address.city").

        Returns:
            A configured FieldAccessor instance.
        """
        tokens = _parse_tokens(raw_path)
        return cls(_compile_expression(tokens))

    def resolve(self, obj: object) -> object:
        """Resolve the accessor against obj and return the extracted value.

        Args:
            obj: Object to extract value from.

        Returns:
            The resolved value at the accessor's path.
        """
        return self.expression.search(_to_data(obj))


__all__ = ["CompiledExpression", "FieldAccessor"]
