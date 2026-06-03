# API Reference

This section provides API documentation for all pypaginate modules.
Documentation is automatically generated from source code docstrings using
[sphinx-autoapi](https://sphinx-autoapi.readthedocs.io/).

## Module Overview

| Module | Description |
|--------|-------------|
| [`pypaginate`](pypaginate/index.rst) | Public API: `paginate`, `OffsetParams`, `CursorParams`, page types, specs, enums |
| [`pypaginate.domain`](pypaginate/domain/index.rst) | Pure types: params, pages, specs, protocols, enums, exceptions |
| [`pypaginate.engine`](pypaginate/engine/index.rst) | Orchestration: `Paginator`, `AsyncPaginator`, `AsyncCursorPaginator`, pipelines |
| [`pypaginate.filtering`](pypaginate/filtering/index.rst) | In-memory filter engine, operators, registry, accessors |
| [`pypaginate.search`](pypaginate/search/index.rst) | In-memory search engine, matching, tokenization |
| [`pypaginate.sorting`](pypaginate/sorting/index.rst) | Sort key helpers |
| [`pypaginate.text`](pypaginate/text/index.rst) | Text normalization (Unicode, accent removal) |
| [`pypaginate.adapters.memory`](pypaginate/adapters/memory/index.rst) | Memory backends: pagination, filtering, sorting, search |
| [`pypaginate.adapters.sqlalchemy`](pypaginate/adapters/sqlalchemy/index.rst) | SQLAlchemy backends: pagination, cursor, filtering, sorting, search |
| [`pypaginate.adapters.fastapi`](pypaginate/adapters/fastapi/index.rst) | FastAPI dependencies: `OffsetDep`, `CursorDep`, `FilterDep`, `SortDep`, `SearchDep` |

```{seealso}
For the complete auto-generated API reference with all classes, functions, and type
annotations, see the [Full API Reference](pypaginate/index.rst).
```

## Quick Reference

### Pagination

```python
from pypaginate import paginate, OffsetParams, CursorParams

# In-memory offset pagination
page = paginate(users_list, OffsetParams(page=1, limit=20))
page.total   # int
page.items   # list[T]

# SQLAlchemy async offset pagination
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

backend = SQLAlchemyBackend(session)
page = await paginate(select(User), OffsetParams(page=1), backend=backend)

# SQLAlchemy cursor pagination
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

cursor_backend = SQLAlchemyCursorBackend(session)
page = await paginate(
    select(User).order_by(User.id),
    CursorParams(limit=20),
    backend=cursor_backend,
)
page.next_cursor  # str | None
```

### Filtering

```python
from pypaginate import FilterSpec, And, Or

# Single filter
FilterSpec(field="age", operator="gte", value=18)

# Nested groups
group = And(
    FilterSpec(field="status", value="active"),
    Or(
        FilterSpec(field="role", value="admin"),
        FilterSpec(field="age", operator="gte", value=21),
    ),
)

# In-memory filtering
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry

engine = FilterEngine(create_default_registry())
filtered = engine.apply(items, [FilterSpec(field="age", operator="gte", value=18)])

# SQLAlchemy filtering
from pypaginate.adapters.sqlalchemy import SQLAlchemyFilterBackend

fb = SQLAlchemyFilterBackend()
query = fb.apply_filters(select(User), [FilterSpec(field="age", operator="gte", value=18)])
```

### Search

```python
from pypaginate import SearchSpec
from pypaginate.domain.enums import FuzzyMode

# Basic search
SearchSpec(query="john doe", fields=("name", "email"))

# Fuzzy search with weights
SearchSpec(
    query="jhn",
    fields=("name", "email"),
    weights={"name": 2.0},
    fuzzy=FuzzyMode.FUZZY,
    threshold=75,
)

# In-memory search
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()
results = engine.apply(items, SearchSpec(query="john", fields=("name",)))
```

### Sorting

```python
from pypaginate import SortSpec
from pypaginate.domain.enums import SortDirection, NullsPosition

SortSpec(field="name")
SortSpec(field="created_at", direction=SortDirection.DESC, nulls=NullsPosition.LAST)

# SQLAlchemy sorting
from pypaginate.adapters.sqlalchemy import SQLAlchemySortBackend

sb = SQLAlchemySortBackend()
query = sb.apply_sorting(select(User), [SortSpec(field="name")])
```

### Pipeline (filter + sort + search + paginate)

```python
from pypaginate import OffsetParams, FilterSpec, SortSpec, SearchSpec
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend, SQLAlchemyFilterBackend,
    SQLAlchemySortBackend, SQLAlchemySearchBackend,
)

pipeline = AsyncPipeline(
    AsyncPaginator(SQLAlchemyBackend(session)),
    filter_backend=SQLAlchemyFilterBackend(),
    sort_backend=SQLAlchemySortBackend(),
    search_backend=SQLAlchemySearchBackend(),
)

result = await pipeline.execute(
    select(User),
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="status", value="active")],
    sorting=[SortSpec(field="name")],
    search=SearchSpec(query="john", fields=("name", "email")),
)
```

### FastAPI Integration

```python
from fastapi import Depends, FastAPI, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import OffsetParams, FilterSpec
from pypaginate.adapters.fastapi import OffsetDep, CursorDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend, SQLAlchemyFilterBackend
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.engine.paginator import AsyncPaginator

app = FastAPI()

@app.get("/users")
async def list_users(
    params: OffsetDep,
    session: AsyncSession = Depends(get_session),
    name: str | None = Query(None),
):
    filters = []
    if name:
        filters.append(FilterSpec(field="name", operator="contains", value=name))

    backend = SQLAlchemyBackend(session)
    pipeline = AsyncPipeline(
        AsyncPaginator(backend),
        filter_backend=SQLAlchemyFilterBackend(),
    )
    return await pipeline.execute(select(User), params, filters=filters)
```

## Import Patterns

### Top-Level (Recommended)

```python
from pypaginate import (
    # Entry point
    paginate,
    # Params
    OffsetParams, CursorParams,
    # Pages
    OffsetPage, CursorPage,
    # Specs
    FilterSpec, SortSpec, SearchSpec,
    # Filter groups
    FilterGroup, And, Or,
    # Enums
    SortDirection, NullsPosition, FilterLogic,
    FuzzyMode, SearchFieldMode, OverflowStrategy,
    # Exceptions
    PaginationError, ConfigurationError, ValidationError,
    FilterError, FilterValidationError,
    SearchError, SearchQueryError, SortError,
    # Version
    __version__,
)
```

### Adapters

```python
# SQLAlchemy
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend, SyncSQLAlchemyBackend,
    SQLAlchemyCursorBackend, SyncSQLAlchemyCursorBackend,
    SQLAlchemyFilterBackend,
    SQLAlchemySortBackend,
    SQLAlchemySearchBackend,
)

# FastAPI
from pypaginate.adapters.fastapi import (
    OffsetDep, CursorDep,
    FilterDep, FilterField,
    SortDep, SearchDep,
)

# Memory (usually used internally)
from pypaginate.adapters.memory.backend import MemoryBackend
```

### Engine

```python
from pypaginate.engine.paginator import Paginator, AsyncPaginator
from pypaginate.engine.cursor import AsyncCursorPaginator
from pypaginate.engine.pipeline import SyncPipeline, AsyncPipeline
```

### Domain (Advanced)

```python
from pypaginate.domain.protocols import (
    PaginationBackend, SyncPaginationBackend,
    CursorBackend, FilterBackend,
    SortBackend, SearchBackend,
)
```

## Type Annotations

pypaginate is fully typed and compatible with `mypy --strict`. The package includes
a `py.typed` marker (PEP 561).

## Versioning

This documentation is for pypaginate version **0.2.0**. See the
[Changelog](https://github.com/CybLow/paginate/blob/main/CHANGELOG.md)
for version history.
