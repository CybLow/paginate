"""Sorting utilities.

This module provides sorting services with:
- Natural ordering with deterministic tie-breaking
- Null value positioning (first/last)
- Reverse sorting

Public API
----------
SortEngine
    Generic sorting service for collections.
sort_items
    One-shot function to sort items.
create_sort_service
    Factory function to create SortEngine instances.
SqlSortAdapter
    SQL-specific sort adapter for building SQLAlchemy ORDER BY clauses.
"""

from __future__ import annotations

from .engine import Nulls, SortEngine, create_sort_service, sort_items
from .sql_adapter import SqlSortAdapter


__all__ = [
    "Nulls",
    "SortEngine",
    "SqlSortAdapter",
    "create_sort_service",
    "sort_items",
]
