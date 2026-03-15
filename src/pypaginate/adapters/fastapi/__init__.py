"""FastAPI integration — Annotated dependency types.

Usage::

    from pypaginate.adapters.fastapi import OffsetDep, CursorDep
"""

from __future__ import annotations

from pypaginate.adapters.fastapi.dependencies import CursorDep, OffsetDep


__all__ = ["CursorDep", "OffsetDep"]
