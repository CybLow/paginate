"""Cursor value encoding/decoding for keyset pagination.

Thin wrapper over the native ``pypaginate._core`` codec — the single source of
truth for the URL-safe base64 + compact-JSON wire format (byte-identical across
the Rust, Python, and JS implementations). The native extension is mandatory, so
there is no pure-Python fallback; a malformed cursor surfaces as the domain
``ValidationError``.
"""

from __future__ import annotations

from typing import Any

from pypaginate._core import decode_cursor as _decode, encode_cursor as _encode
from pypaginate.domain.exceptions import ValidationError


def encode_cursor(values: tuple[Any, ...]) -> str:
    """Encode ORDER BY column values into a URL-safe cursor string."""
    return str(_encode(values))


def decode_cursor(cursor: str) -> tuple[Any, ...]:
    """Decode a cursor string back into its values tuple.

    Raises:
        ValidationError: If the cursor is malformed or tampered with.
    """
    try:
        return tuple(_decode(cursor))
    except ValueError as exc:
        raise ValidationError("Invalid cursor") from exc


__all__ = ["decode_cursor", "encode_cursor"]
