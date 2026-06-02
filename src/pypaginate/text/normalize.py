"""Text normalization for search and filtering.

Delegates the actual normalization (NFKD accent-strip + case-fold + whitespace
collapse) to the native ``pypaginate._core`` engine, so Python and Rust agree
byte-for-byte. A bounded dict cache avoids the FFI hop for repeated field
values (which are common across rows).
"""

from __future__ import annotations

from pypaginate._core import normalize_text as _core_normalize


_CACHE: dict[str, str] = {}
_CACHE_MAX = 8192


def normalize_text(value: str) -> str:
    """Normalize text for search and filtering (native), with a bounded cache.

    Args:
        value: Text to normalize.

    Returns:
        Normalized ASCII-safe text.
    """
    result = _CACHE.get(value)
    if result is not None:
        return result
    result = _core_normalize(value)
    if len(_CACHE) < _CACHE_MAX:
        _CACHE[value] = result
    return result


def clear_normalize_cache() -> None:
    """Clear the normalize_text cache.

    Call in long-lived processes or between test runs
    to free memory from cached normalization results.
    """
    _CACHE.clear()


__all__ = ["clear_normalize_cache", "normalize_text"]
