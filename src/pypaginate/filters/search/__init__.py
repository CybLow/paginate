"""Search-based filtering for pagination."""

from __future__ import annotations

from .conditions import SearchMode, SqlConditionBuilder

# Factories
from .factories import (
    create_memory_search_service,
    create_search_services,
    create_sql_search_service,
)
from .memory_search import MemorySearchEngine, MemorySearchService
from .options import DEFAULT_SEARCH_MODE
from .parser import QueryTokens, TokenParser
from .sql_search import SqlSearchService


__all__ = [
    "DEFAULT_SEARCH_MODE",
    # Memory Search - API publique principale
    "MemorySearchEngine",
    "MemorySearchService",
    "QueryTokens",
    "SearchMode",
    "SqlConditionBuilder",
    # SQL Search - API publique principale
    "SqlSearchService",
    # Parser - API publique principale
    "TokenParser",
    "create_memory_search_service",
    "create_search_services",
    # Factories - helpers de création
    "create_sql_search_service",
]
