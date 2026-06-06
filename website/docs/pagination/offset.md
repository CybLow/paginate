---
sidebar_position: 1
title: Offset pagination
---

# Offset pagination

Offset pagination slices a collection into fixed-size pages addressed by a 1-based
**page** number and a **limit** (rows per page). It's the simplest scheme and the
right default for in-memory lists and bounded result sets.

You build the input with `OffsetParams`, pass it to `paginate`, and get back an
`OffsetPage` carrying your rows plus the derived metadata. Both packages return
identical results — see [cross-language parity](../concepts/parity).

## Parameters

`OffsetParams` holds a `page` (1-based, defaults to `1`) and a `limit` (rows per page,
defaults to `20`, range `1..=MAX_LIMIT`). Both are validated at construction by the Rust
core, so an out-of-range value raises a `ValidationError` immediately. The zero-based
row `offset` is derived for you.

```python
from pypaginate import OffsetParams, MAX_LIMIT

params = OffsetParams(page=2, limit=20)
params.offset   # 20  (zero-based row offset)
MAX_LIMIT       # the shared maximum page size (DoS guard)
```

```ts
import { OffsetParams, MAX_LIMIT } from "@cyblow/paginate";

const params = new OffsetParams({ page: 2, limit: 20 });
params.offset;  // 20  (zero-based row offset)
MAX_LIMIT;      // the shared maximum page size (DoS guard)
```

## Paginating a list

`paginate(items, params)` slices an in-memory sequence and derives the page metadata in
the native core.

```python
from pypaginate import paginate, OffsetParams

users = [...]  # any list of dicts or objects

page = paginate(users, OffsetParams(page=1, limit=20))

page.total          # total rows across all pages (int)
page.page           # the requested page number
page.pages          # total number of pages
page.limit          # rows per page
page.has_next       # bool
page.has_previous   # bool

for user in page:   # OffsetPage is iterable…
    ...
page[0]             # …and indexable
len(page)           # number of rows on this page
```

```ts
import { paginate, OffsetParams } from "@cyblow/paginate";

const users = [/* ... */];

const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));

page.total;         // total rows across all pages (number)
page.page;          // the requested page number
page.pages;         // total number of pages
page.limit;         // rows per page
page.hasNext;       // boolean
page.hasPrevious;   // boolean

for (const user of page.items) {  // iterate page.items
  // ...
}
page.items[0];      // index into page.items
page.items.length;  // number of rows on this page
```

:::note Page shape
The fields are identical apart from naming style: Python uses `has_next` / `has_previous`,
TypeScript uses `hasNext` / `hasPrevious`. A Python `OffsetPage` is directly iterable and
indexable; in TypeScript you work through `page.items`.
:::

## The result page

`OffsetPage` carries the matched `items` (your own objects, never copied or coerced) plus
the metadata derived from `(page, limit, total)`:

| Field | Meaning |
|---|---|
| `items` | The rows on this page |
| `total` | Total matching rows across all pages |
| `page` | The requested 1-based page number |
| `pages` | Total number of pages (`ceil(total / limit)`) |
| `limit` | Rows per page |
| `has_next` / `hasNext` | `page < pages` |
| `has_previous` / `hasPrevious` | `page > 1` |

## Overflow: pages beyond the range

Requesting a page past the last one is **not** an error. You get an empty `items` list,
while the metadata still describes the full dataset: `total` and `pages` reflect the real
row count, and the requested `page` number is echoed back. `has_next` is `false` (there's
nothing after the end) and `has_previous` is `true`.

```python
from pypaginate import paginate, OffsetParams

users = list(range(50))  # 50 rows

page = paginate(users, OffsetParams(page=100, limit=20))
list(page)        # []   — no rows on this page
page.total        # 50   — dataset size preserved
page.pages        # 3    — ceil(50 / 20)
page.page         # 100  — echoed back as requested
page.has_next     # False
page.has_previous # True
```

```ts
import { paginate, OffsetParams } from "@cyblow/paginate";

const users = Array.from({ length: 50 }, (_, i) => ({ id: i }));

const page = paginate(users, new OffsetParams({ page: 100, limit: 20 }));
page.items;        // []   — no rows on this page
page.total;        // 50   — dataset size preserved
page.pages;        // 3    — ceil(50 / 20)
page.page;         // 100  — echoed back as requested
page.hasNext;      // false
page.hasPrevious;  // true
```

If you'd rather snap an out-of-range request to the last valid page, TypeScript's
`OffsetParams` offers `.clamp(total)`, which returns params with `page` clamped into
`[1, maxPage]`:

```ts
const safe = new OffsetParams({ page: 100, limit: 20 }).clamp(50); // page → 3
```

## Filtering and sorting before paginating

The one-shot `paginate` shown above is pure offset slicing. To filter, sort, and search in
the **same** native call, use the resident [Dataset](./in-memory) — that page also covers
when to reach for a `Dataset` over the one-shot helpers.

For database-backed offset pagination over an ORM query (rather than an in-memory list),
use the framework integrations instead of loading every row into memory.
