---
sidebar_position: 2
title: Quickstart
---

# Quickstart

Paginate, filter, sort, and search an in-memory collection with `pypaginate`. Items
can be dicts or objects; your rows are returned untouched.

## Paginate a list

```python
from pypaginate import paginate, OffsetParams

users = [...]  # any list of dicts or objects

page = paginate(users, OffsetParams(page=1, limit=20))

page.total       # total rows across all pages (int)
page.pages       # total number of pages
page.has_next    # bool
list(page)       # the page's items (OffsetPage is iterable, indexable, sized)
page[0]          # first item on the page
```

## Filter, sort, and search

The one-shot helpers each run a single operation and return a new list:

```python
from pypaginate import filter, sort, search, FilterSpec, SortSpec, SearchSpec, And

adults = filter(users, FilterSpec(field="age", operator="gte", value=18))

grouped = filter(users, And(
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="role", operator="in", value=["admin", "owner"]),
))

newest = sort(users, SortSpec(field="created_at", direction="desc"))

hits = search(users, SearchSpec(query="alice", fields=["name", "email"]))
```

Operators, directions, and search modes are plain strings (`"gte"`, `"desc"`,
`"contains"`) — see the [shared reference](../general/filtering).

## Query the same data repeatedly — `Dataset`

Each one-shot call marshals the whole collection into the engine. When you query the
**same** rows many times, build a `Dataset` once and reuse it — it runs the full
filter → search → sort → paginate pipeline in a single native call:

```python
from pypaginate import Dataset, OffsetParams, FilterSpec, SortSpec

ds = Dataset(users)   # marshals once

page = ds.page(
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="age", operator="gte", value=18)],
    sorting=[SortSpec(field="created_at", direction="desc")],
)
page.total   # matches across all pages
list(page)   # the page's rows
```

## Where next

| You want to… | Go to |
|---|---|
| Filter with all 20 operators and boolean groups | [Filtering](./filtering) |
| Sort by multiple keys with null placement | [Sorting](./sorting) |
| Rank results, fuzzy / typo-tolerant search | [Search](./search) |
| Offset, keyset (cursor), and `Dataset` in depth | [Pagination](./pagination) |
| Paginate a database query | [SQLAlchemy](./integrations/sqlalchemy) · [Django](./integrations/django) |
| Parse pagination from a request | [FastAPI](./integrations/fastapi) |
