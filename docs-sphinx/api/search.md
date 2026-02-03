# Search Module

The search module provides text search capabilities including fuzzy matching and SQL search services.

## Overview

| Class | Context | Use Case |
|-------|---------|----------|
| `SqlSearchService` | SQL | Database queries with LIKE/ILIKE/trigram |
| `MemorySearchService` | In-memory | Python collections with fuzzy matching |
| `SearchMode` | Configuration | Search behavior (exact, fuzzy, prefix) |

## SqlSearchService

SQL-based search for database queries. Supports multiple search modes and fields.

```{eval-rst}
.. autoclass:: pypaginate.filters.search.SqlSearchService
   :members:
   :show-inheritance:
```

## MemorySearchService

In-memory search for Python collections with fuzzy matching support.

```{eval-rst}
.. autoclass:: pypaginate.filters.search.MemorySearchService
   :members:
   :show-inheritance:
```

## MemorySearchEngine

Low-level search engine for in-memory operations.

```{eval-rst}
.. autoclass:: pypaginate.filters.search.MemorySearchEngine
   :members:
   :show-inheritance:
```

## SearchMode

Enumeration of available search modes.

```{eval-rst}
.. autoclass:: pypaginate.filters.search.SearchMode
   :members:
   :show-inheritance:
```

## Factory Functions

Convenience functions for creating search services.

```{eval-rst}
.. autofunction:: pypaginate.filters.search.create_sql_search_service
```

```{eval-rst}
.. autofunction:: pypaginate.filters.search.create_memory_search_service
```

```{eval-rst}
.. autofunction:: pypaginate.filters.search.create_search_services
```

## Query Parser

Parses search queries into tokens for advanced search operations.

```{eval-rst}
.. autoclass:: pypaginate.filters.search.TokenParser
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: pypaginate.filters.search.QueryTokens
   :members:
   :show-inheritance:
```

## SQL Condition Builder

Builds SQL conditions from search queries.

```{eval-rst}
.. autoclass:: pypaginate.filters.search.SqlConditionBuilder
   :members:
   :show-inheritance:
```

## Usage Examples

### Basic SQL Search

```python
from pypaginate.filters.search import SqlSearchService, SearchMode

# Create search service
search_service = SqlSearchService(
    model=User,
    search_fields=["name", "email", "bio"],
)

# Apply search to query
stmt = select(User)
stmt = search_service.apply_search(stmt, "john doe")
```

### Fuzzy Search

```python
from pypaginate.filters.search import SqlSearchService, SearchMode

search_service = SqlSearchService(
    model=Product,
    search_fields=["name", "description"],
    mode=SearchMode.FUZZY,
)

# Finds "iPhone" when searching "iphon"
stmt = search_service.apply_search(stmt, "iphon")
```

### Case-Insensitive Search

```python
search_service = SqlSearchService(
    model=User,
    search_fields=["name", "email"],
    mode=SearchMode.ILIKE,
)

# Matches "John", "john", "JOHN"
stmt = search_service.apply_search(stmt, "john")
```

### In-Memory Search

```python
from pypaginate.filters.search import MemorySearchService, SearchMode

search_service = MemorySearchService(
    search_fields=["name", "description"],
    mode=SearchMode.FUZZY,
)

# Search in-memory collection
results = search_service.search(products, "laptop")
```

### Multi-Field Search

```python
search_service = SqlSearchService(
    model=Article,
    search_fields=["title", "content", "author_name", "tags"],
    mode=SearchMode.FUZZY,
)

# Searches across all specified fields
stmt = search_service.apply_search(stmt, "python tutorial")
```

## SearchMode Reference

| Mode | Description |
|------|-------------|
| `EXACT` | Exact case-sensitive matching |
| `ILIKE` | Case-insensitive LIKE matching |
| `FUZZY` | Fuzzy/similarity-based matching |
| `PREFIX` | Prefix matching (starts with) |
