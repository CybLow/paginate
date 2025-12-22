"""SQL query builders.

This module provides utilities for building SQL queries:
- count_builder: Build optimized COUNT queries
"""

from __future__ import annotations

from .count_builder import build_count_statement, fetch_count, strip_ordering

__all__ = [
    "build_count_statement",
    "fetch_count",
    "strip_ordering",
]
