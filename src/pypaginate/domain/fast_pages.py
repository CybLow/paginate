"""Fast page construction using msgspec (optional).

When msgspec is installed, provides near-zero-overhead page
construction via msgspec.Struct instead of Pydantic BaseModel.
Duck-types as OffsetPage/CursorPage with ``.model_dump()``
and ``.to_pydantic()`` for compatibility.
"""

from __future__ import annotations

from typing import Any

import msgspec
from msgspec.structs import asdict


class FastOffsetPage(msgspec.Struct, frozen=True, gc=False):
    """Lightweight offset page — near-zero construction cost."""

    items: list[Any]
    limit: int
    has_next: bool
    has_previous: bool
    total: int
    page: int
    pages: int

    def model_dump(self) -> dict[str, Any]:
        """Convert to dict (Pydantic-compatible API)."""
        return asdict(self)

    def model_dump_json(self) -> bytes:
        """Convert to JSON bytes (fast path via msgspec)."""
        return msgspec.json.encode(self)

    def to_pydantic(self) -> Any:
        """Convert to a real Pydantic OffsetPage."""
        from pypaginate.domain.pages import OffsetPage

        return OffsetPage(**asdict(self))

    def __iter__(self):  # noqa: ANN204
        """Iterate over items."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self.items)

    def __getitem__(self, index: int) -> Any:
        """Return item by index."""
        return self.items[index]


class FastCursorPage(msgspec.Struct, frozen=True, gc=False):
    """Lightweight cursor page — near-zero construction cost."""

    items: list[Any]
    limit: int
    has_next: bool
    has_previous: bool
    next_cursor: str | None
    previous_cursor: str | None

    def model_dump(self) -> dict[str, Any]:
        """Convert to dict (Pydantic-compatible API)."""
        return asdict(self)

    def model_dump_json(self) -> bytes:
        """Convert to JSON bytes (fast path via msgspec)."""
        return msgspec.json.encode(self)

    def to_pydantic(self) -> Any:
        """Convert to a real Pydantic CursorPage."""
        from pypaginate.domain.pages import CursorPage

        return CursorPage(**asdict(self))

    def __iter__(self):  # noqa: ANN204
        """Iterate over items."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self.items)

    def __getitem__(self, index: int) -> Any:
        """Return item by index."""
        return self.items[index]


__all__ = ["FastCursorPage", "FastOffsetPage"]
