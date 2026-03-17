"""Type aliases for SQLAlchemy adapter.

Centralizes SQLAlchemy type imports behind TYPE_CHECKING
to keep the adapter importable without SQLAlchemy installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from sqlalchemy import Column
    from sqlalchemy.sql import Select

    # Re-export for type annotations
    SelectStatement = Select[Any]
    ColumnElement = Column[Any]


__all__ = ["ColumnElement", "SelectStatement"]
