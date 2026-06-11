---
sidebar_position: 6
title: Pagination
---

# Pagination

`@cyblow/paginate` covers both [pagination models](../general/pagination-models):
**offset** (page/limit) for in-memory arrays and bounded sets, and **keyset (cursor)**
for large or frequently-changing database queries. It also exposes the portable cursor
codec and a resident **`Dataset`**.

## Offset pagination

### Parameters

`OffsetParams` holds a 1-based `page` (default `1`) and a `limit` (default `20`, range
`1..=MAX_LIMIT`). Both are validated at construction by the core — an out-of-range
value throws `ValidationError`. The zero-based row `offset` is derived for you:

```ts
import { OffsetParams, MAX_LIMIT } from "@cyblow/paginate";

const params = new OffsetParams({ page: 2, limit: 20 });
params.offset;  // 20
MAX_LIMIT;      // the shared maximum page size (DoS guard)
```

### Paginating an array

```ts
import { paginate, OffsetParams } from "@cyblow/paginate";

const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));

page.total;         // total rows across all pages (number)
page.page;          // the requested page number
page.pages;         // total number of pages — ceil(total / limit)
page.limit;         // rows per page
page.hasNext;       // boolean
page.hasPrevious;   // boolean

for (const user of page.items) { /* ... */ }
page.items[0];
page.items.length;
```

:::note Page shape vs. Python
The fields match Python apart from naming style: TypeScript uses `hasNext` /
`hasPrevious` and you iterate `page.items`; Python uses `has_next` / `has_previous`
and the page is directly iterable. See [parity](../general/parity).
:::

### Pages beyond the range, and `clamp`

Requesting a page past the last one is **not** an error — you get empty `items` with
the metadata still describing the full dataset. To snap an out-of-range request to the
last valid page, `OffsetParams` offers `.clamp(total)`:

```ts
const safe = new OffsetParams({ page: 100, limit: 20 }).clamp(50); // page -> 3
```

The standalone helpers `offset`, `maxPages`, `clampPage`, and `offsetMeta(page, limit,
total)` are exported if you need the pieces directly (e.g. to build metadata around an
ORM count).

## Keyset (cursor) pagination

Keyset pagination pages by the ordering values of the last row seen, so it stays
correct and fast under writes — see [pagination models](../general/pagination-models#keyset-cursor-pagination).
It is **database-backed**; for an in-memory array, offset is simpler and just as fast.

### The cursor codec

The codec is exposed directly, and a cursor minted here decodes byte-for-byte in a
Python service and back (see [cursors](../general/cursors)):

```ts
import { encodeCursor, decodeCursor } from "@cyblow/paginate";

const cursor = encodeCursor([42, "2025-06-01T00:00:00"]);
decodeCursor(cursor); // → [42, "2025-06-01T00:00:00"]
```

### Parameters and result page

`CursorParams` holds a `limit` plus at most one of `after` / `before`:

```ts
import { CursorParams } from "@cyblow/paginate";

new CursorParams({ limit: 20 });                // first page
new CursorParams({ limit: 20, after: cursor }); // page forward
new CursorParams({ limit: 20, before: cursor }); // page backward
```

A keyset query returns a `CursorPage` with `items`, `limit`, `hasNext` /
`hasPrevious`, and `nextCursor` / `previousCursor` (no `total`). Feed `nextCursor` back
in as the next request's `after`.

### Driving it

Keyset is driven by the ORM adapters, which render the core's portable keyset predicate:

- **[Prisma](./integrations/prisma#keyset-cursor-pagination)** — `keysetWhere`.
- **[Drizzle](./integrations/drizzle#keyset-cursor-pagination)** — `keysetCondition`.

## The resident Dataset

The one-shot helpers marshal your whole array into the core on every call. When you
query the **same** rows repeatedly, a `Dataset` marshals once, then answers many queries
natively. In JS the standout win is the **fused `page()`** — filter → sort → paginate in
one native columnar pass that returns only the page (see [performance](../rust/performance)).

```ts
import { Dataset, OffsetParams } from "@cyblow/paginate";

const ds = new Dataset(users); // marshals once
ds.size;                       // number of rows held

const adults = ds.filter([{ field: "age", operator: "gte", value: 18 }]);
const newest = ds.sort([{ field: "createdAt", direction: "desc" }]);
const hits   = ds.search({ query: "alice", fields: ["name", "email"] });

const page = ds.page(new OffsetParams({ page: 1, limit: 20 }), {
  filters: [{ field: "age", operator: "gte", value: 18 }],
  sorting: [{ field: "createdAt", direction: "desc" }],
  search:  { query: "alice", fields: ["name", "email"] },
});
page.total;  // matches across all pages
page.items;  // the page's rows
```

:::tip JS performance
For a single one-shot filter/sort/search over data your host already holds, native
`Array` methods are often faster than crossing into Rust — use the helpers for
*behaviour parity*, and reach for `Dataset.page` (the fused pipeline) for the hot path.
The [benchmarks](../rust/performance) are explicit about this.
:::

## Next

- [Pagination models](../general/pagination-models) — offset vs. keyset, in depth.
- [Prisma](./integrations/prisma) · [Drizzle](./integrations/drizzle) · [Express](./integrations/express)
