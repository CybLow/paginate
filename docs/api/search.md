# Search Module

The search module provides text search capabilities including fuzzy matching and SQL search services.

## Overview

The search module provides:

- **SqlSearchService** - SQL-based search for database queries
- **MemorySearchService** - In-memory search for Python collections
- **SearchOptions** - Configuration for search behavior
- **Fuzzy matching** - Typo-tolerant searching

## SqlSearchService

::: pypaginate.filters.search.sql_search.SqlSearchService
    options:
      show_source: true
      members:
        - __init__
        - apply_search

## MemorySearchService

::: pypaginate.filters.search.memory_search.MemorySearchService
    options:
      show_source: true
      members:
        - __init__
        - search

## SearchOptions

::: pypaginate.filters.search.options.SearchOptions
    options:
      show_source: true

## Usage Examples

### Basic SQL Search

```python
from pypaginate.filters.search import SqlSearchService, SearchOptions

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
from pypaginate.filters.search import SqlSearchService, SearchOptions

search_service = SqlSearchService(
    model=Product,
    search_fields=["name", "description"],
    options=SearchOptions(
        fuzzy=True,
        min_similarity=0.6,
    ),
)

# Finds "iPhone" when searching "iphon"
stmt = search_service.apply_search(stmt, "iphon")
```

### Case-Insensitive Search

```python
search_service = SqlSearchService(
    model=User,
    search_fields=["name", "email"],
    options=SearchOptions(
        case_sensitive=False,
    ),
)

# Matches "John", "john", "JOHN"
stmt = search_service.apply_search(stmt, "john")
```

### Accent-Insensitive Search

```python
search_service = SqlSearchService(
    model=User,
    search_fields=["name"],
    options=SearchOptions(
        accent_sensitive=False,
    ),
)

# Matches "José" when searching "jose"
stmt = search_service.apply_search(stmt, "jose")
```

### In-Memory Search

```python
from pypaginate.filters.search import MemorySearchService, SearchOptions

search_service = MemorySearchService(
    search_fields=["name", "description"],
    options=SearchOptions(fuzzy=True),
)

# Search in-memory collection
results = search_service.search(products, "laptop")
```

### Multi-Field Search

```python
search_service = SqlSearchService(
    model=Article,
    search_fields=["title", "content", "author_name", "tags"],
    options=SearchOptions(
        fuzzy=True,
        min_similarity=0.7,
    ),
)

# Searches across all specified fields
stmt = search_service.apply_search(stmt, "python tutorial")
```

### Search with Ranking

```python
search_service = SqlSearchService(
    model=Product,
    search_fields=["name", "description"],
    options=SearchOptions(
        fuzzy=True,
        rank_results=True,  # Order by relevance
    ),
)

stmt = search_service.apply_search(stmt, "wireless mouse")
# Results ordered by search relevance
```

## SearchOptions Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fuzzy` | bool | False | Enable fuzzy matching |
| `min_similarity` | float | 0.6 | Minimum similarity for fuzzy matches (0-1) |
| `case_sensitive` | bool | False | Case-sensitive matching |
| `accent_sensitive` | bool | True | Accent-sensitive matching |
| `rank_results` | bool | False | Order results by relevance |
| `max_results` | int | None | Limit number of search results |
