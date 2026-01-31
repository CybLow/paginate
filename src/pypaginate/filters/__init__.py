"""Filtering and search capabilities for pagination.

This module provides two distinct filtering systems:

predicates/
    JSON Logic-based filtering with customizable operators.
    Use for complex predicate-based filtering on in-memory data.

search/
    Text-based search for SQL and in-memory data.
    Use for full-text search with token parsing and fuzzy matching.

Public API
----------
From predicates:
    FilterEngine, FieldAccessor, OperatorRegistry, filter_items

From search:
    SqlSearchService, MemorySearchService, TokenParser
"""

from __future__ import annotations

# Predicate filtering - API principale
from .predicates import (
    CompiledFilter,
    FieldAccessor,
    FilterEngine,
    FilterPredicate,
    JsonLogicPredicateBuilder,
    OperatorFactory,
    OperatorRegistry,
    filter_items,
)

# Search capabilities - API principale
from .search import (
    DEFAULT_SEARCH_MODE,
    MemorySearchEngine,
    MemorySearchService,
    QueryTokens,
    SearchMode,
    SqlSearchService,
    TokenParser,
    create_memory_search_service,
    create_sql_search_service,
)


__all__ = [
    "DEFAULT_SEARCH_MODE",
    "CompiledFilter",
    "FieldAccessor",
    # Predicates - Filtrage par prédicats JSON Logic
    "FilterEngine",
    "FilterPredicate",
    "JsonLogicPredicateBuilder",
    "MemorySearchEngine",
    "MemorySearchService",
    "OperatorFactory",
    "OperatorRegistry",
    "QueryTokens",
    "SearchMode",
    "SqlSearchService",
    # Search - Recherche textuelle
    "TokenParser",
    "create_memory_search_service",
    # Factories
    "create_sql_search_service",
    "filter_items",
]
