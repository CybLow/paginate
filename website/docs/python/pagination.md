---
sidebar_position: 6
title: Pagination
---

# Pagination

`pypaginate` covers both [pagination models](../general/pagination-models): **offset**
(page/limit) for in-memory lists and bounded sets, and **keyset (cursor)** for large or
frequently-changing database queries. It also offers a resident **`Dataset`** that
fuses filter → sort → paginate into one native call.

## Offset pagination

You build the input with `OffsetParams`, pass it to `paginate`, and get back an
`OffsetPage`.

### Parameters

`OffsetParams` holds a 1-based `page` (default `1`) and a `limit` (default `20`, range
`1..=MAX_LIMIT`). Both are validated at construction by the core — an out-of-range
value raises `ValidationError`. The zero-based row `offset` is derived for you:

```python
from pypaginate import OffsetParams, MAX_LIMIT

params = OffsetParams(page=2, limit=20)
params.offset   # 20
MAX_LIMIT       # the shared maximum page size (DoS guard)
```

### Paginating a list

```python
from pypaginate import paginate, OffsetParams

page = paginate(users, OffsetParams(page=1, limit=20))

page.total          # total rows across all pages (int)
page.page           # the requested page number
page.pages          # total number of pages — ceil(total / limit)
page.limit          # rows per page
page.has_next       # bool
page.has_previous   # bool

for user in page:   # OffsetPage is iterable…
    ...
page[0]             # …indexable…
len(page)           # …and sized
```

### Pages beyond the range

Requesting a page past the last one is **not** an error — you get empty `items` while
the metadata still describes the full dataset:

```python
users = list(range(50))
page = paginate(users, OffsetParams(page=100, limit=20))
list(page)        # []
page.total        # 50
page.pages        # 3
page.has_next     # False
page.has_previous # True
```

### Beyond plain slicing

The one-shot `paginate` is pure offset slicing. To filter, sort, and search in the
**same** native call, use a [`Dataset`](#the-resident-dataset). To paginate a **database** query
without loading every row, use the [SQLAlchemy](./integrations/sqlalchemy) or
[Django](./integrations/django) integrations.

## Keyset (cursor) pagination

Keyset pagination pages by the ordering values of the last row seen, so it stays
correct and fast under writes — see [pagination models](../general/pagination-models#keyset-cursor-pagination).
It is **database-backed**; there is no in-memory keyset helper (for a list you hold,
offset is simpler and just as fast).

### Parameters

`CursorParams` holds a `limit` plus at most one of `after` / `before` (mutually
exclusive — `after` pages forward, `before` backward, neither for the first page):

```python
from pypaginate import CursorParams

CursorParams(limit=20)                 # first page
CursorParams(limit=20, after=cursor)   # page forward
CursorParams(limit=20, before=cursor)  # page backward
```

### The result page

A keyset query returns a `CursorPage` carrying the rows and the navigation cursors —
but no `total` or page number:

| Field | Meaning |
|---|---|
| `items` | the rows on this page |
| `limit` | requested page size |
| `has_next` / `has_previous` | a following / preceding page exists |
| `next_cursor` / `previous_cursor` | cursor to fetch the next / previous page, or `None` |

Feed `next_cursor` back in as the next request's `after`, and `previous_cursor` as
`before`. The cursor codec is shared across languages — see [cursors](../general/cursors).

### Driving it

Keyset is driven by the ORM integrations, which read your query's `ORDER BY`, render
the keyset predicate, over-fetch `limit + 1`, trim, and assemble the `CursorPage`:

- **[SQLAlchemy](./integrations/sqlalchemy#keyset-cursor-pagination)** — sync + async
  cursor backends.
- **[Django](./integrations/django#keyset-cursor-pagination)** — `paginate_keyset`.

## The resident Dataset

The one-shot helpers marshal your whole collection into the core on every call. When
you query the **same** rows repeatedly, a `Dataset` marshals once, then answers many
queries natively (returning indices the wrapper maps back to your objects). **Build
once, query many.**

```python
from pypaginate import Dataset

ds = Dataset(users)   # marshals once
len(ds)               # number of rows held
```

### Querying

`filter`, `sort`, and `search` each return a new list, using the same spec shapes as
the one-shot helpers:

```python
from pypaginate import Dataset, FilterSpec, SortSpec, SearchSpec

ds = Dataset(users)

adults = ds.filter([FilterSpec(field="age", operator="gte", value=18)])
newest = ds.sort([SortSpec(field="created_at", direction="desc")])
hits   = ds.search(SearchSpec(query="alice", fields=["name", "email"]))
```

### The whole pipeline in one call

`page` runs filter → search → sort → offset-paginate in a single native call, returning
an `OffsetPage`. Each stage is optional:

```python
page = ds.page(
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="age", operator="gte", value=18)],
    sorting=[SortSpec(field="created_at", direction="desc")],
    search=SearchSpec(query="alice", fields=["name", "email"]),
)
page.total      # matches across all pages
list(page)      # the page's rows
```

### When to reach for it

| Use… | When |
|---|---|
| one-shot `filter` / `sort` / `search` / `paginate` | a single query, or data that changes every call |
| `Dataset` | several queries against the **same** rows — paging plus re-sorting, faceted filtering, repeated searches |

A `Dataset` operates on rows you already hold in memory; for a **database** query, use
the integrations. See [performance](../rust/performance) for the measured speedups.

## Next

- [Pagination models](../general/pagination-models) — offset vs. keyset, in depth.
- [SQLAlchemy](./integrations/sqlalchemy) · [Django](./integrations/django) · [FastAPI](./integrations/fastapi)
