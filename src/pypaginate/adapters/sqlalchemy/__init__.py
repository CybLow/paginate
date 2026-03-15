"""SQLAlchemy backends for pagination, filtering, sorting, and search."""

from __future__ import annotations

from pypaginate.adapters.sqlalchemy.backend import (
    SQLAlchemyBackend,
    SyncSQLAlchemyBackend,
)
from pypaginate.adapters.sqlalchemy.cursor import (
    SQLAlchemyCursorBackend,
    SyncSQLAlchemyCursorBackend,
)
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.adapters.sqlalchemy.search import SQLAlchemySearchBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend


__all__ = [
    "SQLAlchemyBackend",
    "SQLAlchemyCursorBackend",
    "SQLAlchemyFilterBackend",
    "SQLAlchemySearchBackend",
    "SQLAlchemySortBackend",
    "SyncSQLAlchemyBackend",
    "SyncSQLAlchemyCursorBackend",
]
