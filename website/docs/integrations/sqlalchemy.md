---
sidebar_position: 1
title: SQLAlchemy
---

# SQLAlchemy

Pydantic-free pagination for SQLAlchemy 2.0. The adapter translates pypaginate's
flat specs into SQLAlchemy expressions and paginates a `select()` against a sync
or async session. It supports both **offset** pages and **keyset (cursor)** pages,
and the cursors are byte-compatible with every other adapter — see
[cross-language parity](../concepts/parity).

## Install

```bash
pip install "pypaginate[sqlalchemy]"
```

This pulls in `SQLAlchemy[asyncio]>=2.0`. The native engine ships inside the
`pypaginate` wheel — no Rust toolchain needed.

## Public API

```python
from pypaginate.adapters.sqlalchemy import (
    build_filter,          # flat FilterSpec list -> WHERE expression (or None)
    build_filter_group,    # nested And/Or FilterGroup -> WHERE expression
    build_order_by,        # SortSpec list -> ORDER BY clauses
    SQLAlchemyBackend,         # async offset backend
    SyncSQLAlchemyBackend,     # sync offset backend
    SQLAlchemyCursorBackend,       # async keyset/cursor backend
    SyncSQLAlchemyCursorBackend,   # sync keyset/cursor backend
    resolve_column,        # field name -> mapped column attribute
    # low-level keyset helpers (used by the cursor backends)
    OrderColumn, build_keyset_condition, extract_order_columns,
)
```

The adapter resolves each spec's `field` to a mapped attribute with `getattr`, so
`FilterSpec(field="age", ...)` maps to `Model.age`. An unknown field raises
`ConfigurationError`.

## Building WHERE and ORDER BY

`build_filter`, `build_filter_group`, and `build_order_by` are pure translators —
you decide how to attach them to your `select()`. `build_filter` returns `None`
when the filter list is empty, so guard before calling `.where()`.

```python
from sqlalchemy import select
from pypaginate import FilterSpec, SortSpec, And
from pypaginate.adapters.sqlalchemy import build_filter, build_filter_group, build_order_by

# Flat list — each spec carries its own AND/OR `logic`:
where = build_filter(User, [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="status", operator="eq", value="active"),
])

# Nested boolean group:
where = build_filter_group(User, And(
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="name", operator="contains", value="a"),
))

order = build_order_by(User, [SortSpec(field="age", direction="desc", nulls="last")])

stmt = select(User)
if where is not None:
    stmt = stmt.where(where)
stmt = stmt.order_by(*order)
```

All 20 filter operators are supported (`eq`, `ne`, `gt`, `gte`, `lt`, `lte`,
`in`, `not_in`, `contains`, `starts_with`, `ends_with`, `like`, `ilike`,
`between`, `is_null`, `is_not_null`, `regex`, `empty`, `not_empty`, `exists`).
`empty` renders `col IS NULL OR col = ''`, `not_empty` the converse, and `exists`
renders `TRUE`. `regex` uses `Column.regexp_match` (backend-dependent).

## Offset pagination

The backend counts matching rows with `SELECT COUNT(*)` and fetches the window
with `OFFSET`/`LIMIT`, returning an `OffsetPage`. Filtering and sorting are
applied by you on the `query` before it is handed in.

```python
from pypaginate import OffsetParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyBackend

backend = SyncSQLAlchemyBackend(session)        # a sqlalchemy.orm.Session
page = backend.paginate(stmt, OffsetParams(page=1, limit=20))

page.total         # int — matched rows
page.pages         # int — total pages
page.has_next      # bool
list(page)         # the page's ORM rows (OffsetPage is iterable + indexable)
```

The async backend is identical with `await`:

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

backend = SQLAlchemyBackend(async_session)      # AsyncSession
page = await backend.paginate(stmt, OffsetParams(page=1, limit=20))
```

Both backends also expose `count(query)` and `fetch(query, offset, limit)` if you
need the pieces separately.

## Keyset (cursor) pagination

The cursor backend over-fetches `limit + 1` rows for a keyset-ordered query and
returns a `CursorPage` with `next_cursor` / `previous_cursor`. The query **must**
carry an `ORDER BY` that uniquely orders rows — append a trailing primary key.

```python
from sqlalchemy import select
from pypaginate import CursorParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend

stmt = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
backend = SyncSQLAlchemyCursorBackend(session)

first = backend.fetch_page(stmt, CursorParams(limit=20))
next_page = backend.fetch_page(stmt, CursorParams(limit=20, after=first.next_cursor))
prev_page = backend.fetch_page(stmt, CursorParams(limit=20, before=next_page.previous_cursor))
```

`CursorParams` accepts at most one of `after` / `before`; passing both raises a
`ValidationError`. The backend decodes the cursor, applies the lexicographic
keyset `WHERE` (e.g. `(a > v1) OR (a = v1 AND b < v2)`), re-orders, over-fetches,
trims, and re-encodes — all derived from the query's own `ORDER BY`. The async
backend (`SQLAlchemyCursorBackend`) has the same `fetch_page` signature with
`await`.
