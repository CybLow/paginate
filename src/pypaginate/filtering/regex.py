"""Safe regex compilation with optional google-re2.

Uses google-re2 (linear-time, ReDoS-safe) if installed,
falls back to stdlib ``re``. Same API surface.
"""

from __future__ import annotations

import re as _stdlib_re
from typing import Any


try:
    import re2 as _re_mod  # type: ignore[import-untyped,import-not-found]

    _HAS_RE2 = True
except ImportError:
    _re_mod = _stdlib_re  # type: ignore[assignment]
    _HAS_RE2 = False


def compile_pattern(pattern: str) -> Any:
    """Compile a regex pattern using re2 if available.

    Args:
        pattern: Regular expression pattern string.

    Returns:
        A compiled pattern object with a ``.search()`` method.

    Raises:
        re.error: If the pattern is invalid.
    """
    return _re_mod.compile(pattern)


__all__ = ["compile_pattern"]
