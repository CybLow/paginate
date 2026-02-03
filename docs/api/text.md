# Text Processing

The text module provides text normalization utilities for search operations. It includes normalizers for both in-memory and SQL-based search contexts.

## Overview

| Class | Context | Use Case |
|-------|---------|----------|
| `MemoryTextNormalizer` | In-memory | Python-side text processing for fuzzy search |
| `SqlTextNormalizer` | SQL | Database-side text processing with collations |

## MemoryTextNormalizer

::: pypaginate.text.MemoryTextNormalizer
    options:
      show_source: true

## SqlTextNormalizer

::: pypaginate.text.SqlTextNormalizer
    options:
      show_source: true

## Usage Examples

### In-Memory Text Normalization

```python
from pypaginate.text import MemoryTextNormalizer

# Create normalizer for search
normalizer = MemoryTextNormalizer()

# Normalize search query
query = "Café résumé"
normalized = normalizer.normalize(query)
print(normalized)  # "cafe resume" (accents removed, lowercased)

# Use with fuzzy search
def search_items(items: list[str], query: str) -> list[str]:
    normalized_query = normalizer.normalize(query)
    return [
        item for item in items
        if normalized_query in normalizer.normalize(item)
    ]
```

### SQL Text Normalization

```python
from pypaginate.text import SqlTextNormalizer

# Create normalizer for SQL queries
normalizer = SqlTextNormalizer()

# Normalize for LIKE queries
search_term = "Müller"
normalized = normalizer.normalize(search_term)

# Use in SQLAlchemy query
from sqlalchemy import select, func

query = select(User).where(
    func.lower(User.name).contains(normalized)
)
```

### Combined Search Pipeline

```python
from pypaginate.text import MemoryTextNormalizer, SqlTextNormalizer


class SearchService:
    """Search service with consistent normalization."""
    
    def __init__(self) -> None:
        self.memory_normalizer = MemoryTextNormalizer()
        self.sql_normalizer = SqlTextNormalizer()
    
    def normalize_for_memory(self, text: str) -> str:
        """Normalize text for in-memory operations."""
        return self.memory_normalizer.normalize(text)
    
    def normalize_for_sql(self, text: str) -> str:
        """Normalize text for SQL operations."""
        return self.sql_normalizer.normalize(text)
```

## Normalization Features

Both normalizers provide:

- **Case folding**: Converts to lowercase for case-insensitive matching
- **Accent removal**: Strips diacritical marks (é → e, ü → u)
- **Unicode normalization**: Applies NFC/NFKC normalization
- **Whitespace handling**: Normalizes whitespace characters

### Differences

| Feature | MemoryTextNormalizer | SqlTextNormalizer |
|---------|---------------------|-------------------|
| Context | Python runtime | Database queries |
| Performance | Fast, in-process | Depends on DB collation |
| Consistency | Always consistent | May vary by database |
