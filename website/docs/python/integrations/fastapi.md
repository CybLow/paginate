---
sidebar_position: 3
title: FastAPI
---

# FastAPI

Turn a request's query string into pypaginate specs with plain FastAPI
dependency callables (and ready-made `Annotated` aliases). Invalid
page/limit/cursor combinations are reported as **HTTP 422** responses. This is
the only adapter that uses Pydantic — it ships under the `[fastapi]` extra.

## Install

```bash
pip install "pypaginate[fastapi]"
```

This pulls in `fastapi>=0.95` and `pydantic>=2.0`.

## Public API

```python
from pypaginate.adapters.fastapi import (
    OffsetDep, CursorDep, SortDep, SearchDep,   # Annotated dependency aliases
    offset_params, cursor_params,               # the underlying callables
    sort_params, search_params,
    parse_sort, parse_search,                   # pure string parsers
    FilterDep, FilterField,                     # declarative filter models
)
```

## Pagination, sort, and search params

The `*Dep` aliases are `Annotated[..., Depends(...)]`, so just annotate a
handler argument:

```python
from fastapi import FastAPI
from pypaginate.adapters.fastapi import OffsetDep, SortDep, SearchDep

app = FastAPI()

@app.get("/users")
def list_users(params: OffsetDep, sort: SortDep, search: SearchDep):
    # params: OffsetParams from ?page=&limit=  (defaults page=1, limit=20)
    # sort:   list[SortSpec] from ?sort=name,-age  ('-' prefix = descending)
    # search: SearchSpec | None from ?q=&search_fields=name,email
    ...
```

For cursor endpoints use `CursorDep`, which reads `?limit=&after=&before=`
(`after` and `before` are mutually exclusive):

```python
from pypaginate.adapters.fastapi import CursorDep

@app.get("/posts")
def list_posts(params: CursorDep):
    # params: CursorParams(limit=..., after=..., before=...)
    ...
```

The standalone callables (`offset_params`, `cursor_params`, `sort_params`,
`search_params`) are useful with `Depends()` directly, and `parse_sort(value)` /
`parse_search(query, fields_csv)` are pure functions you can call outside a
request.

## Declarative filters

Subclass `FilterDep` and declare fields with `FilterField` to map query
parameters onto `FilterSpec` conditions. Only fields whose value is **not
`None`** become conditions. `FilterField` carries the operator and an optional
target `field` (defaults to the attribute name).

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
    specs = filters.to_specs()   # list[FilterSpec]
    ...
```

A request like `?name=al&min_age=18` yields
`[FilterSpec(field="name", operator="contains", value="al"),
FilterSpec(field="age", operator="gte", value=18)]`.

## End-to-end with SQLAlchemy

The FastAPI adapter only parses the request — pair it with a query-building
adapter (see [SQLAlchemy](./sqlalchemy)) to return an actual page:

```python
from typing import Annotated
from fastapi import Query
from sqlalchemy import select
from pypaginate.adapters.fastapi import OffsetDep, SortDep, FilterDep, FilterField
from pypaginate.adapters.sqlalchemy import (
    build_filter, build_order_by, SyncSQLAlchemyBackend,
)

class UserFilters(FilterDep):
    status: str | None = FilterField(None, operator="eq")
    min_age: int | None = FilterField(None, field="age", operator="gte")

@app.get("/users")
def list_users(
    params: OffsetDep,
    sort: SortDep,
    filters: Annotated[UserFilters, Query()],
):
    stmt = select(User)
    where = build_filter(User, filters.to_specs())
    if where is not None:
        stmt = stmt.where(where)
    stmt = stmt.order_by(*build_order_by(User, sort))

    page = SyncSQLAlchemyBackend(session).paginate(stmt, params)
    return {"items": list(page), "total": page.total, "pages": page.pages}
```
