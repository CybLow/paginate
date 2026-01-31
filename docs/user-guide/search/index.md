# Search

pypaginate provides powerful text search capabilities with fuzzy matching.

## Overview

| Feature | Description |
|---------|-------------|
| [Text Search](text-search.md) | Full-text search basics |
| [Fuzzy Matching](fuzzy.md) | Approximate string matching |

## Quick Example

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

# Configure search
service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email", "bio"],
        fuzzy_threshold=0.8,
    )
)

users = [
    {"name": "Alice Smith", "email": "alice@example.com", "bio": "Python developer"},
    {"name": "Bob Johnson", "email": "bob@example.com", "bio": "JavaScript expert"},
    {"name": "Alicia Keys", "email": "alicia@example.com", "bio": "Full-stack dev"},
]

# Search
results = service.search(users, "alice")
# Finds: Alice Smith, Alicia Keys (fuzzy match)
```

## Search Engines

### MemorySearchService

For in-memory data:

```python
from pypaginate.filters.search import MemorySearchService

service = MemorySearchService(options=SearchOptions(fields=["name"]))
results = service.search(items, "query")
```

### SqlSearchService

For database queries:

```python
from pypaginate.filters.search import SqlSearchService

service = SqlSearchService(
    model=User,
    search_fields=["name", "email"],
    options=SearchOptions(fuzzy=True)
)

stmt = service.apply_search(select(User), "query")
```

## Search Options

```python
from pypaginate.filters.search.options import SearchOptions

options = SearchOptions(
    fields=["name", "description"],   # Fields to search
    fuzzy_threshold=0.8,               # Similarity threshold (0-1)
    case_sensitive=False,              # Case-insensitive by default
    accent_sensitive=False,            # Ignore accents
)
```

## Next Steps

- [Text Search](text-search.md) - Full guide
- [Fuzzy Matching](fuzzy.md) - RapidFuzz integration
