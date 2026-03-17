"""Token parser for search queries.

Splits search queries into tokens, respecting quoted phrases.
No external dependencies -- uses stdlib only.
"""

from __future__ import annotations

import shlex


class TokenParser:
    """Parse search queries into individual tokens.

    Handles quoted phrases as single tokens and splits
    unquoted text on whitespace.
    """

    __slots__ = ()

    def parse(self, query: str) -> list[str]:
        """Split a query string into search tokens.

        Quoted phrases are preserved as single tokens.
        Extra whitespace is stripped.

        Args:
            query: Raw search query (e.g. ``'"john doe" admin'``).

        Returns:
            List of token strings.

        Examples:
            >>> TokenParser().parse('"john doe" admin')
            ['john doe', 'admin']
            >>> TokenParser().parse("  hello   world  ")
            ['hello', 'world']
        """
        stripped = query.strip()
        if not stripped:
            return []
        return self._tokenize(stripped)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenize text using shlex for quote handling.

        Falls back to simple whitespace split if shlex
        encounters malformed quotes.

        Args:
            text: Non-empty, stripped query text.

        Returns:
            List of non-empty token strings.
        """
        try:
            tokens = shlex.split(text)
        except ValueError:
            tokens = text.split()
        return [t for t in tokens if t]


__all__ = ["TokenParser"]
