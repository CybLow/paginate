"""Factory functions for search services."""

from __future__ import annotations

import re

from ...text.api import MemoryTextNormalizer, SqlTextNormalizer
from .conditions import SqlConditionBuilder
from .memory_search import MemorySearchEngine, MemorySearchService
from .parser import TokenParser
from .sql_search import SqlSearchService


def create_sql_search_service(
    *, id_pattern: re.Pattern[str] | None = None
) -> SqlSearchService:
    """Create a SQL-backed search service.

    Args:
        id_pattern: Optional regex used to detect identifier tokens.

    Returns:
        A configured :class:`SqlSearchService` instance.
    """
    parser = TokenParser()
    normalizer = SqlTextNormalizer()
    builder = SqlConditionBuilder(normalizer)
    return SqlSearchService(parser, normalizer, builder, id_pattern=id_pattern)


def create_memory_search_service() -> MemorySearchService:
    """Create an in-memory search service.

    Returns:
        A configured :class:`MemorySearchService` instance.
    """
    parser = TokenParser()
    engine = MemorySearchEngine(MemoryTextNormalizer())
    return MemorySearchService(parser, engine)


def create_search_services(
    *, id_pattern: re.Pattern[str] | None = None
) -> tuple[SqlSearchService, MemorySearchService]:
    """Create both SQL and in-memory search services.

    Args:
        id_pattern: Optional regex used to detect identifier tokens
            for the SQL service.

    Returns:
        A tuple ``(sql_service, memory_service)``.
    """
    return (
        create_sql_search_service(id_pattern=id_pattern),
        create_memory_search_service(),
    )


__all__ = [
    "create_sql_search_service",
    "create_memory_search_service",
    "create_search_services",
]
