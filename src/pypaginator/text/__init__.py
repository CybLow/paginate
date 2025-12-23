"""Text processing utilities for pagination.

This module provides text normalization and processing for search:
- Text normalizers for SQL and in-memory contexts
- Pattern matching utilities
- Text processing pipelines
- UTF-8 utilities

Public API
----------
MemoryTextNormalizer
    Text normalizer for in-memory search operations.
SqlTextNormalizer
    Text normalizer for SQL search operations.
"""

from __future__ import annotations

from .api import MemoryTextNormalizer, SqlTextNormalizer


__all__ = [
    "MemoryTextNormalizer",
    "SqlTextNormalizer",
]
