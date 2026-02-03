# API Reference

Complete API documentation for pypaginate, auto-generated from source code docstrings.

```{toctree}
:maxdepth: 2

core
engines
query
filters
search
sorting
integrations
database
text
exceptions
```

## Modules

| Module | Description |
|--------|-------------|
| [Core](core.md) | Core types: `Page`, `PageParams`, pagination context |
| [Engines](engines.md) | Pagination engines: `SqlPaginator`, `MemoryPaginator` |
| [Query](query.md) | High-level query functions: `paginate_entities`, etc. |
| [Filters](filters.md) | Filtering: predicates, JSON Logic, field accessors |
| [Search](search.md) | Text search: fuzzy matching, SQL search |
| [Sorting](sorting.md) | Sorting: `SortEngine`, `SqlSortAdapter` |
| [Integrations](integrations.md) | Framework integrations: FastAPI |
| [Database](database.md) | Database utilities: collations, type aliases |
| [Text](text.md) | Text normalization for search |
| [Exceptions](exceptions.md) | Exception classes for error handling |

## Quick Start

### Pagination

```python
from pypaginate.core import Page, PageParams
from pypaginate.query import paginate_entities_to_page

# Create pagination parameters
params = PageParams(page=1, limit=20)

# Paginate a SQLAlchemy query
page = await paginate_entities_to_page(session, stmt, params)
```

### Filtering

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()
filters = {"age": {"gte": 18}, "status": {"eq": "active"}}
conditions = engine.build_conditions(User, filters)
```

### Search

```python
from pypaginate.filters.search import SqlSearchService, SearchMode

search = SqlSearchService(
    model=User,
    search_fields=["name", "email"],
    mode=SearchMode.FUZZY,
)
stmt = search.apply_search(stmt, "john")
```

### Sorting

```python
from pypaginate.sorting import SortEngine, SqlSortAdapter

# In-memory sorting
sorted_items = SortEngine.sort(items, "name", reverse=False, ...)

# SQL sorting
order_expr = SqlSortAdapter.build_order_expression(User.name, descending=True)
```

### FastAPI Integration

```python
from fastapi import Depends, FastAPI
from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse
from pypaginate.core import PageParams

app = FastAPI()

@app.get("/users", response_model=PagedResponse[UserSchema])
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
):
    stmt = select(User).order_by(User.id)
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)
```

## Import Patterns

### Recommended Imports

```python
# Core types
from pypaginate.core import Page, PageParams, KeysetPageParams

# Query API (most common)
from pypaginate.query import (
    paginate_entities,
    paginate_entities_to_page,
    paginate_rows,
    paginate_rows_to_page,
)

# FastAPI integration
from pypaginate.integrations.fastapi import (
    get_pagination_params,
    PagedResponse,
)

# Sorting
from pypaginate.sorting import SortEngine, SqlSortAdapter, sort_items

# Filtering
from pypaginate.filters.predicates import FilterEngine
from pypaginate.filters.search import SqlSearchService, SearchMode

# Exceptions
from pypaginate.exceptions import (
    PaginatorException,
    PaginationConfigurationError,
    FilterException,
    ValidationException,
)
```

### Full Module Access

```python
# Access all public APIs
import pypaginate

# Or specific submodules
from pypaginate import core, query, sorting, filters
```

## Type Annotations

pypaginate is fully typed and compatible with `mypy --strict`. Key type exports:

```python
from pypaginate.types import (
    # Type variables
    T,
    ItemT,
    ParamsT,
)

from pypaginate.core import (
    Page,       # Generic[T]
    PageParams, # Dataclass
)
```
