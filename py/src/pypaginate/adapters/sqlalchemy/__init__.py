"""SQLAlchemy adapter — Pydantic-free pagination for SQLAlchemy 2.0.

Translates the package's flat specs into SQLAlchemy expressions and paginates a
``select()`` against a sync or async session:

- :func:`build_filter` / :func:`build_filter_group` -> WHERE expressions
- :func:`build_order_by` -> ORDER BY clauses
- :class:`SQLAlchemyBackend` / :class:`SyncSQLAlchemyBackend` -> offset pages
- :class:`SQLAlchemyCursorBackend` / :class:`SyncSQLAlchemyCursorBackend` -> keyset pages
"""

from __future__ import annotations

from pypaginate.adapters.sqlalchemy.backend import (
    SQLAlchemyBackend,
    SyncSQLAlchemyBackend,
)
from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.adapters.sqlalchemy.cursor import (
    SQLAlchemyCursorBackend,
    SyncSQLAlchemyCursorBackend,
)
from pypaginate.adapters.sqlalchemy.filters import build_filter, build_filter_group
from pypaginate.adapters.sqlalchemy.keyset import (
    OrderColumn,
    build_keyset_condition,
    extract_order_columns,
)
from pypaginate.adapters.sqlalchemy.sorting import build_order_by


__all__ = [
    "OrderColumn",
    "SQLAlchemyBackend",
    "SQLAlchemyCursorBackend",
    "SyncSQLAlchemyBackend",
    "SyncSQLAlchemyCursorBackend",
    "build_filter",
    "build_filter_group",
    "build_keyset_condition",
    "build_order_by",
    "extract_order_columns",
    "resolve_column",
]
