---
sidebar_position: 2
title: Building a paginated API
description: A complete paginated, filterable, sortable REST endpoint in Python (FastAPI + SQLAlchemy) and TypeScript (Express), driven entirely by query parameters.
---

# Building a paginated API

Turn query parameters into a validated, filtered, sorted, paginated response. The
request shape is the same in both languages:

```text
GET /users?page=2&limit=20&sort=-created_at&status=active
```

## Python — FastAPI + SQLAlchemy

`OffsetDep` and `SortDep` parse pagination and sorting; a declarative `FilterDep` maps
query params onto filter conditions. The SQLAlchemy adapter builds the `WHERE` /
`ORDER BY` and paginates.

```python
from typing import Annotated
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate.adapters.fastapi import OffsetDep, SortDep, FilterDep, FilterField
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend, build_filter, build_order_by

app = FastAPI()

class UserOut(BaseModel):
    id: int
    name: str
    status: str
    model_config = {"from_attributes": True}

class UserFilters(FilterDep):
    status: str | None = FilterField(None, operator="eq")
    name: str | None = FilterField(None, operator="contains")
    min_age: int | None = FilterField(None, field="age", operator="gte")

@app.get("/users")
async def list_users(
    params: OffsetDep,
    sort: SortDep,
    filters: Annotated[UserFilters, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    stmt = select(User)
    where = build_filter(User, filters.to_specs())
    if where is not None:
        stmt = stmt.where(where)
    stmt = stmt.order_by(*build_order_by(User, sort)) if sort else stmt.order_by(User.id)

    page = await SQLAlchemyBackend(session).paginate(stmt, params)
    return {
        "items": [UserOut.model_validate(u) for u in page],
        "total": page.total,
        "page": page.page,
        "pages": page.pages,
        "has_next": page.has_next,
    }
```

Invalid `page` / `limit` values become **HTTP 422** automatically. See the
[FastAPI](../python/integrations/fastapi) and [SQLAlchemy](../python/integrations/sqlalchemy)
guides for the full surface.

## TypeScript — Express

`express.offsetParamsFromQuery` validates `page` / `limit`. For an in-memory array, hand
the params to `paginate` with filters and sorting in one native call:

```ts
import express from "express";
import { express as paginateExpress, paginate, ValidationError } from "@cyblow/paginate";

const app = express();

app.get("/users", (req, res) => {
  try {
    const params = paginateExpress.offsetParamsFromQuery(req.query);

    const filters = [];
    if (req.query.status) filters.push({ field: "status", operator: "eq", value: req.query.status });
    if (req.query.name) filters.push({ field: "name", operator: "contains", value: req.query.name });

    const page = paginate(users, params, {
      filters,
      sorting: [{ field: "created_at", direction: "desc" }],
    });

    res.json({
      items: page.items,
      total: page.total,
      page: page.page,
      pages: page.pages,
      hasNext: page.hasNext,
    });
  } catch (err) {
    if (err instanceof ValidationError) return res.status(400).json({ error: err.message });
    throw err;
  }
});
```

For a **database** instead of an in-memory array, use the
[Prisma](../typescript/integrations/prisma) adapter: `prisma.offsetArgs(params)` gives
`{ skip, take }`, and `offsetMeta(page, limit, total)` derives the metadata around a
`count`.

## Next

- [Sharing cursors across Python & TypeScript](./polyglot-cursors) — the keyset version.
- Python [pagination](../python/pagination) · TypeScript [pagination](../typescript/pagination).
