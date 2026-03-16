# pypaginate

**Universal pagination toolkit for Python -- one function, any backend, auto-detects sync/async.**

[![CI](https://github.com/CybLow/pypaginate/actions/workflows/ci.yml/badge.svg)](https://github.com/CybLow/pypaginate/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pypaginate.svg)](https://pypi.org/project/pypaginate/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypaginate.svg)](https://pypi.org/project/pypaginate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/CybLow/pypaginate/branch/main/graph/badge.svg)](https://codecov.io/gh/CybLow/pypaginate)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

pypaginate provides a single `paginate()` function that works with lists, SQLAlchemy queries (async and sync), and cursor-based pagination. The return type is automatically inferred from the params you pass in.

## Features

- **One function** -- `paginate()` handles lists, SQLAlchemy queries, sync and async
- **Type-safe inference** -- `OffsetParams` returns `OffsetPage`, `CursorParams` returns `CursorPage`
- **Filtering** -- 20+ operators (eq, gte, contains, between, regex, etc.)
- **Sorting** -- multi-column with direction and null placement control
- **Search** -- full-text with optional fuzzy matching (RapidFuzz)
- **FastAPI** -- `Annotated` dependencies for pagination, filtering, sorting, and search
- **Cursor pagination** -- keyset/cursor-based pagination via sqlakeyset
- **Pipeline** -- compose filter + sort + search + paginate in one call
- **100% typed** -- mypy strict mode, Pydantic v2 models

## Installation

```bash
# Core (in-memory pagination only)
pip install pypaginate

# With SQLAlchemy support
pip install pypaginate[sqlalchemy]

# With FastAPI integration
pip install pypaginate[fastapi]

# With fuzzy search (RapidFuzz)
pip install pypaginate[search]

# Everything
pip install pypaginate[all]
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pypaginate
uv add pypaginate[all]
```

## Quick Start

Paginate a list in 3 lines:

```python
from pypaginate import paginate, OffsetParams

page = paginate([1, 2, 3, 4, 5], OffsetParams(page=1, limit=2))

page.items       # [1, 2]
page.total       # 5
page.pages       # 3
page.has_next    # True
```

## SQLAlchemy (Async)

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

async def list_users(session: AsyncSession):
    stmt = select(User).order_by(User.created_at.desc())
    backend = SQLAlchemyBackend(session)

    page = await paginate(stmt, OffsetParams(page=1, limit=20), backend=backend)

    page.items       # list[User]
    page.total       # int
    page.has_next    # bool
```

For sync sessions, use `SyncSQLAlchemyBackend`:

```python
from sqlalchemy.orm import Session
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyBackend

def list_users(session: Session):
    backend = SyncSQLAlchemyBackend(session)
    page = paginate(select(User), OffsetParams(page=1, limit=20), backend=backend)
```

## Cursor Pagination

For large datasets where offset-based pagination is inefficient:

```python
from pypaginate import paginate, CursorParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

async def scroll_users(session: AsyncSession, cursor: str | None = None):
    stmt = select(User).order_by(User.id)
    backend = SQLAlchemyCursorBackend(session)

    page = await paginate(stmt, CursorParams(limit=20, after=cursor), backend=backend)

    page.items            # list[User]
    page.next_cursor      # str | None -- pass to next request
    page.previous_cursor  # str | None
    page.has_next         # bool
```

## FastAPI Integration

pypaginate provides `Annotated` dependency types for clean FastAPI integration:

```python
from fastapi import FastAPI
from pypaginate import paginate, OffsetPage
from pypaginate.adapters.fastapi import OffsetDep

app = FastAPI()

@app.get("/users")
async def list_users(params: OffsetDep) -> OffsetPage[dict]:
    users = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]
    return paginate(users, params)
```

Available dependencies:

| Dependency | Query Params | Produces |
|---|---|---|
| `OffsetDep` | `?page=1&limit=20` | `OffsetParams` |
| `CursorDep` | `?limit=20&after=abc` | `CursorParams` |
| `FilterDep` | (user-defined fields) | `list[FilterSpec]` |
| `SortDep` | `?sort=name,-age` | `list[SortSpec]` |
| `SearchDep` | `?q=alice&search_fields=name,email` | `SearchSpec` |

### Declarative Filters

```python
from typing import Annotated
from fastapi import Query
from pypaginate.adapters.fastapi import FilterDep, FilterField

class UserFilters(FilterDep):
    name: str | None = FilterField(None, operator="contains")
    age_min: int | None = FilterField(None, field="age", operator="gte")
    status: str | None = FilterField(None, operator="eq")

@app.get("/users")
async def list_users(
    params: OffsetDep,
    filters: Annotated[UserFilters, Query()],
):
    # filters.to_specs() returns list[FilterSpec] for non-None fields
    ...
```

### Sorting and Search

```python
from pypaginate.adapters.fastapi import OffsetDep, SortDep, SearchDep

@app.get("/users")
async def list_users(params: OffsetDep, sort: SortDep, search: SearchDep):
    # sort: ?sort=name,-created_at  (- prefix = descending)
    # search: ?q=alice&search_fields=name,email
    ...
```

## Filtering

Use `FilterSpec` to define filter conditions:

```python
from pypaginate import FilterSpec
from pypaginate.filtering import FilterEngine, create_default_registry

engine = FilterEngine(create_default_registry())

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Simple equality
active = engine.apply(users, [FilterSpec(field="status", value="active")])
# [Alice, Charlie]

# Multiple filters (AND by default)
result = engine.apply(users, [
    FilterSpec(field="age", operator="gte", value=30),
    FilterSpec(field="status", value="active"),
])
# [Alice, Charlie]
```

### Nested Filter Groups

```python
from pypaginate import And, Or, FilterSpec

# (status = active) AND (age >= 30 OR name contains "bob")
group = And(
    FilterSpec(field="status", value="active"),
    Or(
        FilterSpec(field="age", operator="gte", value=30),
        FilterSpec(field="name", operator="contains", value="bob"),
    ),
)

result = engine.apply(users, group)
```

### Available Filter Operators

| Operator | Description | Example |
|---|---|---|
| `eq`, `ne` | Equality / inequality | `FilterSpec(field="status", value="active")` |
| `gt`, `gte`, `lt`, `lte` | Comparisons | `FilterSpec(field="age", operator="gte", value=18)` |
| `in`, `not_in` | Membership | `FilterSpec(field="role", operator="in", value=["admin", "user"])` |
| `contains`, `starts_with`, `ends_with` | Text matching | `FilterSpec(field="name", operator="contains", value="ali")` |
| `like`, `ilike` | SQL-style patterns | `FilterSpec(field="email", operator="like", value="%@gmail.com")` |
| `between` | Range | `FilterSpec(field="price", operator="between", value=[10, 100])` |
| `is_null`, `is_not_null` | Null checks | `FilterSpec(field="notes", operator="is_null")` |
| `empty`, `not_empty` | Empty checks | `FilterSpec(field="tags", operator="not_empty")` |
| `regex` | Regex matching | `FilterSpec(field="code", operator="regex", value="^A\\d+")` |

## Sorting

```python
from pypaginate import SortSpec, SortDirection

from pypaginate.sorting import SortEngine

engine = SortEngine()

users = [
    {"name": "Charlie", "age": 35},
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]

sorted_users = engine.apply(users, [
    SortSpec(field="age", direction=SortDirection.DESC),
])
# [Charlie (35), Alice (30), Bob (25)]
```

## Search

```python
from pypaginate import SearchSpec

from pypaginate.search import SearchEngine

engine = SearchEngine()

users = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
]

results = engine.apply(users, SearchSpec(
    query="alice",
    fields=("name", "email"),
))
# [Alice Smith]
```

Fuzzy search (requires `pypaginate[search]`):

```python
from pypaginate import SearchSpec, FuzzyMode

results = engine.apply(users, SearchSpec(
    query="alce",
    fields=("name",),
    fuzzy=FuzzyMode.FUZZY,
    threshold=75,
))
```

## Pipeline (Filter + Sort + Search + Paginate)

Compose all operations in a single call:

```python
from pypaginate import OffsetParams, FilterSpec, SortSpec, SortDirection
from pypaginate.engine.pipeline import SyncPipeline
from pypaginate.engine.paginator import Paginator
from pypaginate.adapters.memory import (
    MemoryBackend,
    MemoryFilterBackend,
    MemorySortBackend,
)

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
    sort_backend=MemorySortBackend(),
)

page = pipeline.execute(
    users,
    OffsetParams(page=1, limit=10),
    filters=[FilterSpec(field="status", value="active")],
    sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
)
```

For async (e.g., SQLAlchemy), use `AsyncPipeline` with `AsyncPaginator`.

## Architecture

```
pypaginate/
├── domain/        # Models, specs, enums, protocols (no deps)
├── engine/        # Paginator, cursor paginator, pipeline
├── filtering/     # In-memory filter engine + operators
├── sorting/       # In-memory sort engine
├── search/        # In-memory search engine
└── adapters/
    ├── memory/        # In-memory backends (filter, sort, search)
    ├── sqlalchemy/    # SA backends (offset, cursor, filter, sort, search)
    └── fastapi/       # Annotated dependencies (OffsetDep, FilterDep, etc.)
```

## Development

```bash
git clone https://github.com/CybLow/pypaginate.git
cd pypaginate
uv sync

# Run all checks
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest

# Individual commands
uv run pytest                  # Tests
uv run pytest --cov            # Coverage
uv run ruff format .           # Format
uv run ruff check --fix .      # Lint
uv run mypy src/               # Type check
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and quality checks (`uv run pytest && uv run ruff check .`)
4. Commit with conventional commits (`git commit -m 'feat: add amazing feature'`)
5. Open a Pull Request

## License

MIT -- see [LICENSE](LICENSE) for details.
