"""Safe regex compilation with optional google-re2.

Uses google-re2 (linear-time, ReDoS-safe) if installed,
falls back to stdlib ``re``. Same API surface.
"""

from __future__ import annotations

import re as _stdlib_re
from typing import Any


from pypaginate.domain.exceptions import FilterError

try:
    import re2 as _re_mod  # type: ignore[import-untyped,import-not-found]

    _HAS_RE2 = True
except ImportError:
    _re_mod = _stdlib_re  # type: ignore[assignment]
    _HAS_RE2 = False

MAX_REGEX_LENGTH = 200


def compile_pattern(pattern: str) -> Any:
    """Compile a regex pattern using re2 if available.

    Args:
        pattern: Regular expression pattern string.

    Returns:
        A compiled pattern object with a ``.search()`` method.

    Raises:
        FilterError: If the pattern is too long or invalid.
    """
    if len(pattern) > MAX_REGEX_LENGTH:
        msg = f"Invalid regex: exceeds {MAX_REGEX_LENGTH} characters"
        raise FilterError(msg)
    return _re_mod.compile(pattern)


__all__ = ["compile_pattern"]
