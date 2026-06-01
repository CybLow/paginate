"""Cursor value encoding/decoding for keyset pagination.

Encodes ORDER BY column values into URL-safe base64 strings.
No external dependencies — uses stdlib json + base64.
"""

from __future__ import annotations

import base64
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from pypaginate.domain.exceptions import ValidationError


_TYPE_KEY = "__type__"


def _encode_cursor_python(values: tuple[Any, ...]) -> str:
    """Encode cursor values to a URL-safe string.

    Args:
        values: Tuple of column values from the ORDER BY row.

    Returns:
        URL-safe base64-encoded string.
    """
    serialized = [_serialize_value(v) for v in values]
    payload = json.dumps(serialized, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")


def _decode_cursor_python(cursor: str) -> tuple[Any, ...]:
    """Decode a cursor string back to a values tuple.

    Args:
        cursor: URL-safe base64-encoded cursor string.

    Returns:
        Tuple of deserialized column values.

    Raises:
        ValidationError: If the cursor is malformed or tampered with.
    """
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        payload = base64.urlsafe_b64decode(padded.encode()).decode()
        raw = json.loads(payload)
    except Exception as exc:
        raise ValidationError("Invalid cursor") from exc
    if not isinstance(raw, list):
        raise ValidationError("Invalid cursor")
    return tuple(_deserialize_value(v) for v in raw)


# -- Serialization -----------------------------------------------------------


def _serialize_value(value: Any) -> Any:
    """Convert a Python value to a JSON-safe representation."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return {_TYPE_KEY: "datetime", "v": value.isoformat()}
    if isinstance(value, date):
        return {_TYPE_KEY: "date", "v": value.isoformat()}
    if isinstance(value, Decimal):
        return {_TYPE_KEY: "decimal", "v": str(value)}
    if isinstance(value, UUID):
        return {_TYPE_KEY: "uuid", "v": str(value)}
    return str(value)


# -- Deserialization ---------------------------------------------------------


_DESERIALIZERS: dict[str, Any] = {
    "datetime": lambda v: datetime.fromisoformat(v),
    "date": lambda v: date.fromisoformat(v),
    "decimal": lambda v: Decimal(v),
    "uuid": lambda v: UUID(v),
}


def _deserialize_value(value: Any) -> Any:
    """Convert a JSON value back to its Python type."""
    if not isinstance(value, dict) or _TYPE_KEY not in value:
        return value
    tag = value[_TYPE_KEY]
    raw = value.get("v")
    deserializer = _DESERIALIZERS.get(tag)
    if deserializer is None:
        raise ValidationError(
            "Invalid cursor",
            details={"reason": f"unknown type tag: {tag}"},
        )
    try:
        return deserializer(raw)
    except (ValueError, TypeError, InvalidOperation) as exc:
        raise ValidationError("Invalid cursor") from exc


# -- Optional native acceleration (pypaginate-core, Rust) --------------------
# When the compiled ``pypaginate_core`` extension is installed, delegate to its
# byte-compatible Rust implementation; otherwise use the pure-Python codec
# above. Same graceful-degradation pattern as msgspec / rapidfuzz / google-re2.
try:
    from paginate_core import (
        decode_cursor as _native_decode,
        encode_cursor as _native_encode,
    )

    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False


def encode_cursor(values: tuple[Any, ...]) -> str:
    """Encode cursor values to a URL-safe string.

    Uses the native ``pypaginate-core`` extension when available, falling back
    to the pure-Python codec. The wire format is identical either way.
    """
    if _HAS_NATIVE:
        return str(_native_encode(values))
    return _encode_cursor_python(values)


def decode_cursor(cursor: str) -> tuple[Any, ...]:
    """Decode a cursor string back to a values tuple.

    Raises:
        ValidationError: If the cursor is malformed or tampered with.
    """
    if not _HAS_NATIVE:
        return _decode_cursor_python(cursor)
    try:
        return tuple(_native_decode(cursor))
    except ValueError as exc:
        raise ValidationError("Invalid cursor") from exc


__all__ = ["decode_cursor", "encode_cursor"]
