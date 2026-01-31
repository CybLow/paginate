# Text Search

Implement full-text search in your applications.

## MemorySearchService

For searching in-memory data collections:

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

# Configure the service
service = MemorySearchService(
    options=SearchOptions(
        fields=["title", "description", "tags"],
    )
)

# Your data
products = [
    {"id": 1, "title": "Python Book", "description": "Learn Python programming"},
    {"id": 2, "title": "JavaScript Guide", "description": "Master JS development"},
    {"id": 3, "title": "Go Handbook", "description": "Golang essentials"},
]

# Search
results = service.search(products, "python")
# Returns: [Product 1]
```

## SearchOptions

Configure search behavior:

```python
from pypaginate.filters.search.options import SearchOptions

options = SearchOptions(
    # Fields to search
    fields=["name", "email", "bio"],
    
    # Fuzzy matching threshold (0.0 to 1.0)
    # Higher = stricter matching
    fuzzy_threshold=0.8,
    
    # Case sensitivity
    case_sensitive=False,  # Default: False
    
    # Accent sensitivity (é vs e)
    accent_sensitive=False,  # Default: False
    
    # Minimum query length
    min_query_length=2,
    
    # Maximum results (0 = no limit)
    max_results=100,
)
```

## Multi-Field Search

Search across multiple fields simultaneously:

```python
service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email", "department", "title"],
    )
)

employees = [
    {"name": "Alice Smith", "email": "alice@corp.com", "department": "Engineering", "title": "Senior Developer"},
    {"name": "Bob Johnson", "email": "bob@corp.com", "department": "Sales", "title": "Account Manager"},
]

# Searches all configured fields
results = service.search(employees, "engineer")
# Matches Alice (department: Engineering)

results = service.search(employees, "alice")
# Matches Alice (name and email)
```

## Search with Weights

Weight fields differently:

```python
options = SearchOptions(
    fields={
        "title": 2.0,       # Title matches are twice as important
        "description": 1.0,
        "tags": 0.5,        # Tags are less important
    }
)
```

## Searching Nested Fields

Search in nested object properties:

```python
data = [
    {
        "id": 1,
        "user": {"name": "Alice", "profile": {"bio": "Developer"}}
    }
]

service = MemorySearchService(
    options=SearchOptions(
        fields=["user.name", "user.profile.bio"],
    )
)

results = service.search(data, "alice")
```

## SQL Search Service

For database queries, use SqlSearchService:

```python
from pypaginate.filters.search import SqlSearchService
from pypaginate.filters.search.options import SearchOptions

service = SqlSearchService(
    model=User,
    search_fields=["name", "email", "bio"],
    options=SearchOptions(
        case_sensitive=False,
    )
)

# Apply search to a query
stmt = select(User).order_by(User.name)
stmt = service.apply_search(stmt, "alice")

# Execute the query
result = await session.execute(stmt)
users = result.scalars().all()
```

### SQL Search Patterns

```python
# The SQL search generates LIKE patterns:
# "alice" -> WHERE name ILIKE '%alice%' OR email ILIKE '%alice%' OR ...
```

## Combining Search with Pagination

```python
from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator

# 1. Search
search_results = service.search(all_items, query)

# 2. Paginate results
paginator = MemoryPaginator()
params = PageParams(page=1, limit=20)
page = paginator.paginate(search_results, params).to_page()
```

## Combining Search with Filtering

```python
from pypaginate.filters.predicates import FilterEngine

filter_engine = FilterEngine()

# 1. Filter first (narrow down the dataset)
filtered = filter_engine.filter(items, {"status": {"eq": "active"}})

# 2. Then search within filtered results
results = service.search(filtered, "query")
```

## Error Handling

```python
from pypaginate import SearchException

try:
    results = service.search(items, "query")
except SearchException as e:
    print(f"Search error: {e}")
```

## Performance Tips

1. **Limit fields**: Only search relevant fields
2. **Filter first**: Narrow down data before searching
3. **Set max_results**: Limit result count for large datasets
4. **Use SQL search**: For large databases, search at DB level

```python
# Good: Filter, then search, then paginate
filtered = filter_engine.filter(items, {"status": {"eq": "active"}})
searched = service.search(filtered, query)
page = paginator.paginate(searched, params).to_page()
```

## Next Steps

- [Fuzzy Matching](fuzzy.md) - Approximate string matching
- [Filtering Guide](../filtering/index.md) - Combine with filters
