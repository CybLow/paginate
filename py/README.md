# pypaginate

**Fast, typed pagination, filtering, sorting & search for Python — one Rust core, byte-for-byte parity with the TypeScript package.**

[![CI](https://github.com/CybLow/paginate/actions/workflows/ci.yml/badge.svg)](https://github.com/CybLow/paginate/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pypaginate)](https://pypi.org/project/pypaginate/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypaginate)](https://pypi.org/project/pypaginate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/CybLow/paginate/branch/main/graph/badge.svg)](https://codecov.io/gh/CybLow/paginate)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

`pypaginate` paginates, filters, sorts, and searches your data — in memory or
against a database — through a single `paginate()` entry point and a small set of
ergonomic helpers. The algorithms live **once** in a native Rust core
([`paginate-core`](https://crates.io/crates/paginate-core)) that ships inside the
wheel, so there is **no Rust toolchain to install** and the Python and
TypeScript ([`@cyblow/paginate`](https://www.npmjs.com/package/@cyblow/paginate))
packages return **identical results and byte-identical cursors**.

📖 **Full documentation: [cyblow.github.io/paginate](https://cyblow.github.io/paginate/)**

## Highlights

- **One `paginate()`** for in-memory lists; ORM-backed pages via the adapters.
- **Filtering** — 20 operators (`eq`, `gte`, `contains`, `between`, `in`, `regex`, …)
  with flat `AND`/`OR` lists and nested `And()` / `Or()` groups.
- **Sorting** — stable, multi-key, with per-key direction and null placement.
- **Search** — ranked full-text with optional trigram **fuzzy** matching and
  per-field weights — all in the native engine, no extra dependency.
- **Cursor (keyset) pagination** — opaque, URL-safe cursors that decode
  byte-for-byte across Python, TypeScript, and Rust.
- **Integrations** — SQLAlchemy 2.0 (sync + async), Django, and FastAPI.
- **Zero runtime dependencies** in the core; **Pydantic is optional** (only the
  FastAPI extra needs it).
- **Fully typed** (PEP 561) — the spec/param shapes are generated from the core's
  JSON Schema, so Python and TypeScript can't drift.

## Installation

```bash
pip install pypaginate                  # core: in-memory + native engine
pip install "pypaginate[sqlalchemy]"    # SQLAlchemy 2.0 offset + keyset adapter
pip install "pypaginate[fastapi]"       # FastAPI dependencies (+ Pydantic)
pip install "pypaginate[django]"        # Django Q-object builders
pip install "pypaginate[all]"           # everything
```

Or with [uv](https://docs.astral.sh/uv/): `uv add pypaginate` (Python 3.11+).
The native engine is bundled in the wheel; fuzzy/ranked search needs no extra.

## Quick start

Paginate an in-memory list in three lines:

```python
from pypaginate import paginate, OffsetParams

page = paginate([1, 2, 3, 4, 5], OffsetParams(page=1, limit=2))

page.items       # [1, 2]
page.total       # 5
page.pages       # 3
page.has_next    # True
list(page)       # [1, 2]  — OffsetPage is iterable, indexable, sized
```

### Filter, sort, and search

The one-shot helpers run a single operation over any list of dicts or objects:

```python
from pypaginate import filter, sort, search, FilterSpec, SortSpec, SearchSpec, And

users = [...]  # list of dicts or objects

adults = filter(users, FilterSpec(field="age", operator="gte", value=18))
grouped = filter(users, And(
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="role", operator="in", value=["admin", "owner"]),
))
newest = sort(users, SortSpec(field="created_at", direction="desc"))
hits   = search(users, SearchSpec(query="alice", fields=["name", "email"]))
```

Operators, directions, and search modes are plain strings (`"gte"`, `"desc"`,
`"contains"`) — defined once in the core, identical in every language.

### Query the same data repeatedly — `Dataset`

Each one-shot call marshals the whole collection into the engine. When you query
the **same** rows many times, build a `Dataset` once and reuse it — it runs the
full filter → search → sort → paginate pipeline in a single native call:

```python
from pypaginate import Dataset, OffsetParams, FilterSpec, SortSpec

ds = Dataset(users)                         # marshals once

page = ds.page(
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="age", operator="gte", value=18)],
    sorting=[SortSpec(field="created_at", direction="desc")],
)
page.total      # matches across all pages
list(page)      # the page's rows (your original objects, never copied)
```

## SQLAlchemy

`pip install "pypaginate[sqlalchemy]"` — Pydantic-free pagination for
SQLAlchemy 2.0, sync or async, offset or keyset.

```python
from sqlalchemy import select
from pypaginate import OffsetParams, FilterSpec, SortSpec
from pypaginate.adapters.sqlalchemy import (
    SyncSQLAlchemyBackend, build_filter, build_order_by,
)

stmt = select(User)
where = build_filter(User, [FilterSpec(field="status", operator="eq", value="active")])
if where is not None:
    stmt = stmt.where(where)
stmt = stmt.order_by(*build_order_by(User, [SortSpec(field="created_at", direction="desc")]))

page = SyncSQLAlchemyBackend(session).paginate(stmt, OffsetParams(page=1, limit=20))
page.items       # list[User]
page.total       # int
page.has_next    # bool
```

The async backend is identical with `await`:

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

page = await SQLAlchemyBackend(async_session).paginate(stmt, OffsetParams(page=1, limit=20))
```

### Cursor (keyset) pagination

For large or frequently-changing datasets where `OFFSET` is slow or unstable:

```python
from sqlalchemy import select
from pypaginate import CursorParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend

stmt = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
backend = SyncSQLAlchemyCursorBackend(session)

first = backend.fetch_page(stmt, CursorParams(limit=20))
nxt   = backend.fetch_page(stmt, CursorParams(limit=20, after=first.next_cursor))

first.items            # list[Post]
first.next_cursor      # str | None — feed back in as `after`
first.previous_cursor  # str | None
first.has_next         # bool
```

The cursor codec is shared with the TS and Django adapters, so a cursor minted by
any of them decodes byte-for-byte in the others.

## FastAPI

`pip install "pypaginate[fastapi]"` — `Annotated` dependencies that turn a
request's query string into pypaginate specs (invalid params become **HTTP 422**):

```python
from fastapi import FastAPI
from pypaginate import paginate, OffsetPage
from pypaginate.adapters.fastapi import OffsetDep, SortDep, SearchDep

app = FastAPI()

@app.get("/users")
def list_users(params: OffsetDep, sort: SortDep, search: SearchDep) -> OffsetPage[dict]:
    # params: OffsetParams from ?page=&limit=   (defaults page=1, limit=20)
    # sort:   list[SortSpec] from ?sort=name,-age   ('-' prefix = descending)
    # search: SearchSpec | None from ?q=&search_fields=name,email
    users = [{"name": "Alice"}, {"name": "Bob"}]
    return paginate(users, params)
```

| Dependency | Query params | Produces |
|---|---|---|
| `OffsetDep` | `?page=1&limit=20` | `OffsetParams` |
| `CursorDep` | `?limit=20&after=…` | `CursorParams` |
| `SortDep` | `?sort=name,-age` | `list[SortSpec]` |
| `SearchDep` | `?q=alice&search_fields=name,email` | `SearchSpec \| None` |
| `FilterDep` | (declarative, user-defined) | `list[FilterSpec]` |

Declarative filters map query params onto `FilterSpec` conditions:

```python
from typing import Annotated
from fastapi import Query
from pypaginate.adapters.fastapi import FilterDep, FilterField

class UserFilters(FilterDep):
    name: str | None = FilterField(None, operator="contains")
    min_age: int | None = FilterField(None, field="age", operator="gte")
    status: str | None = FilterField(None, operator="eq")

@app.get("/users")
def list_users(filters: Annotated[UserFilters, Query()]):
    specs = filters.to_specs()   # list[FilterSpec] for the non-None fields
    ...
```

## Django

`pip install "pypaginate[django]"` — translate specs into `Q` objects and
`order_by` arguments, then offset- or keyset-paginate a `QuerySet` (Django is
imported lazily, so importing the adapter doesn't require Django):

```python
from pypaginate import OffsetParams, FilterSpec, SortSpec
from pypaginate.adapters.django import apply_filters, apply_sorting, paginate_offset

qs = apply_filters(User.objects.all(), [FilterSpec(field="age", operator="gte", value=18)])
qs = apply_sorting(qs, [SortSpec(field="age", direction="desc")])

page = paginate_offset(qs, OffsetParams(page=1, limit=20))
page.total       # int
list(page)       # the page's model instances
```

`paginate_keyset(qs, CursorParams(...))` provides cursor pagination over an
explicitly ordered `QuerySet`.

## Filter operators

| Operator | Meaning | Operator | Meaning |
|---|---|---|---|
| `eq` / `ne` | Equal / not equal | `like` / `ilike` | SQL `LIKE` (case-(in)sensitive) |
| `gt` / `gte` | Greater (or equal) | `between` | Inclusive range `[lo, hi]` |
| `lt` / `lte` | Less (or equal) | `is_null` / `is_not_null` | Null / present |
| `in` / `not_in` | Membership in a list | `empty` / `not_empty` | Empty / non-empty |
| `contains` | Substring | `regex` | Regular-expression match |
| `starts_with` / `ends_with` | Prefix / suffix | `exists` | Field path resolves |

See the [filtering guide](https://cyblow.github.io/paginate/python/filtering) for
per-operator examples, and [boolean groups](https://cyblow.github.io/paginate/general/filtering)
for nested `And()` / `Or()` trees.

## Errors

All failures derive from `PaginateError` (aliased `PaginationError`):
`ValidationError` (bad page/limit) and its subclass `InvalidCursorError` (a
malformed cursor), `FilterError` / `FilterValidationError`, `SortError`,
`SearchError` / `SearchQueryError`, and `ConfigurationError` (unknown ORM field).
Each carries a structured `details` mapping, mirrored by the TypeScript package.

## Cross-language parity

Because the engine has a single implementation, `pypaginate` and
`@cyblow/paginate` produce the same filtered/sorted/ranked order and
**byte-identical cursors**. A frozen golden fixture is asserted by the Rust,
Python, and TypeScript test suites in CI. See
[cross-language parity](https://cyblow.github.io/paginate/general/parity).

## Development

```bash
git clone https://github.com/CybLow/paginate.git
cd paginate/py
uv sync                        # builds the native core (needs a Rust toolchain)

uv run pytest                  # tests
uv run pytest --cov            # coverage
uv run ruff format .           # format
uv run ruff check --fix .      # lint
```

See [CONTRIBUTING.md](https://github.com/CybLow/paginate/blob/main/CONTRIBUTING.md).

## Links

- 📖 Documentation — <https://cyblow.github.io/paginate/>
- 🦀 Rust core (`paginate-core`) — [crates.io](https://crates.io/crates/paginate-core) · [docs.rs](https://docs.rs/paginate-core)
- 📦 TypeScript package (`@cyblow/paginate`) — [npm](https://www.npmjs.com/package/@cyblow/paginate)
- 🐙 Source & issues — <https://github.com/CybLow/paginate>

## License

MIT — see [LICENSE](https://github.com/CybLow/paginate/blob/main/LICENSE).
