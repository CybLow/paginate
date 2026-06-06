"""Top-level offset pagination over in-memory items.

DB-backed pagination (offset or cursor) is provided by the adapters; this is the
in-memory entry point — the Rust core does the slicing and derives the metadata.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from pypaginate._native import build_offset_page
from pypaginate.pages import OffsetPage
from pypaginate.params import OffsetParams


ItemT = TypeVar("ItemT")


def paginate(items: Sequence[ItemT], params: OffsetParams) -> OffsetPage[ItemT]:
    """Offset-paginate an in-memory sequence into an :class:`OffsetPage`."""
    rows = list(items)
    start = params.offset
    page_items = rows[start : start + params.limit]
    return build_offset_page(page_items, len(rows), params)


__all__ = ["paginate"]
