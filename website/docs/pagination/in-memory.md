---
sidebar_position: 3
title: In-memory Dataset
---

# In-memory Dataset

The one-shot helpers — `paginate`, `filter`, `sort`, `search` — are perfect for a single
operation, but each one marshals your whole collection across the Python/JS ↔ Rust boundary
before it can run. When you query the **same** data repeatedly, that marshalling is wasted
work.

`Dataset` fixes that: it marshals the rows into the Rust core **once**, then answers many
filter / sort / search / page queries natively. The core works on indices internally and
the wrapper maps them back to your original objects, so your rows are never copied or
coerced. **Build once, query many.**

Both packages behave identically — see [cross-language parity](../concepts/parity).

## Building a dataset

```python
from pypaginate import Dataset

ds = Dataset(users)   # marshals once
len(ds)               # number of rows held
```

```ts
import { Dataset } from "@cyblow/paginate";

const ds = new Dataset(users); // marshals once
ds.size;                       // number of rows held
```

## Querying

`filter`, `sort`, and `search` each return a new list of matching rows (search in ranked
relevance order). They use the same spec shapes as the one-shot helpers — Python specs are
dataclasses, TypeScript specs are plain objects.

```python
from pypaginate import Dataset, FilterSpec, SortSpec, SearchSpec

ds = Dataset(users)

adults = ds.filter([FilterSpec(field="age", operator="gte", value=18)])
newest = ds.sort([SortSpec(field="created_at", direction="desc")])
hits   = ds.search(SearchSpec(query="alice", fields=["name", "email"]))
```

```ts
import { Dataset } from "@cyblow/paginate";

const ds = new Dataset(users);

const adults = ds.filter([{ field: "age", operator: "gte", value: 18 }]);
const newest = ds.sort([{ field: "created_at", direction: "desc" }]);
const hits   = ds.search({ query: "alice", fields: ["name", "email"] });
```

## Filter + sort + search + paginate, in one call

`page` runs the full pipeline — filter, then search, then sort, then offset-paginate — in a
single native call and returns an [`OffsetPage`](./offset). Each stage is optional. Here,
`search` acts as a match-filter (keep rows matching the query) while the explicit `sorting`
decides the final order.

```python
from pypaginate import Dataset, OffsetParams, FilterSpec, SortSpec, SearchSpec

ds = Dataset(users)

page = ds.page(
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="age", operator="gte", value=18)],
    sorting=[SortSpec(field="created_at", direction="desc")],
    search=SearchSpec(query="alice", fields=["name", "email"]),
)
page.total      # matches across all pages
list(page)      # the page's rows
```

```ts
import { Dataset, OffsetParams } from "@cyblow/paginate";

const ds = new Dataset(users);

const page = ds.page(new OffsetParams({ page: 1, limit: 20 }), {
  filters: [{ field: "age", operator: "gte", value: 18 }],
  sorting: [{ field: "created_at", direction: "desc" }],
  search: { query: "alice", fields: ["name", "email"] },
});
page.total;       // matches across all pages
page.items;       // the page's rows
```

## Dataset vs the one-shot helpers

Reach for the right tool:

| Use… | When |
|---|---|
| One-shot `filter` / `sort` / `search` / `paginate` | A single query over a collection, or data that changes every call |
| `Dataset` | Several queries against the **same** rows — paging plus re-sorting, faceted filtering, repeated searches |

Each one-shot call re-marshals the whole collection, so for a single operation it's the
simplest choice with no setup. In TypeScript the one-shot `paginate(items, params, opts)`
even builds a throwaway `Dataset` internally for that single call. The moment you run more
than one query over the same data, hold a `Dataset` and reuse it so the marshalling cost is
paid only once.

:::note In-memory only
A `Dataset` operates on rows you already hold in memory. For paginating a **database**
query without loading every row, use the framework integrations instead.
:::
