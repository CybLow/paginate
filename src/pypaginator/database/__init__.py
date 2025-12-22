"""Database utilities for pagination.

This module provides database-specific utilities:
- collations: Database collation management
- types: SQL-specific type definitions

These utilities are isolated from the core pagination logic.
"""

from __future__ import annotations

from .collations import (
    CollationPlan,
    ensure_database_collations,
    recommend_collation_plan,
)
from .types import CountStatement, SelectStatement

__all__ = [
    "CollationPlan",
    "ensure_database_collations",
    "recommend_collation_plan",
    "CountStatement",
    "SelectStatement",
]
