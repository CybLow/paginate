---
sidebar_position: 2
title: Quickstart
---

# Quickstart

Paginate, filter, sort, and search an in-memory collection with `@cyblow/paginate`.
Items can be plain objects; your rows are returned untouched.

## Paginate an array

```ts
import { paginate, OffsetParams } from "@cyblow/paginate";

const users = [/* ... */];

const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));

page.total;     // total rows across all pages (number)
page.pages;     // total number of pages
page.hasNext;   // boolean
page.items;     // the page's items (an array of your objects)
```

## Filter, sort, and search

The one-shot helpers each run a single operation and return a new array:

```ts
import { filter, sort, search, And } from "@cyblow/paginate";

const adults = filter(users, { field: "age", operator: "gte", value: 18 });

const grouped = filter(users, And(
  { field: "age", operator: "gte", value: 18 },
  { field: "role", operator: "in", value: ["admin", "owner"] },
));

const newest = sort(users, { field: "createdAt", direction: "desc" });

const hits = search(users, { query: "alice", fields: ["name", "email"] });
```

Specs are plain objects; operators, directions, and search modes are plain strings
(`"gte"`, `"desc"`, `"contains"`) — see the [shared reference](../general/filtering).

## Query the same data repeatedly — `Dataset`

Each one-shot call marshals the whole array into the engine. When you query the
**same** rows many times, build a `Dataset` once and reuse it — its fused `page()`
runs filter → sort → paginate in a single native call (the one shape where crossing
into Rust pays off for JS — see [performance](../rust/performance)):

```ts
import { Dataset, OffsetParams } from "@cyblow/paginate";

const ds = new Dataset(users); // marshals once

const page = ds.page(new OffsetParams({ page: 1, limit: 20 }), {
  filters: [{ field: "age", operator: "gte", value: 18 }],
  sorting: [{ field: "createdAt", direction: "desc" }],
});
page.total;   // matches across all pages
page.items;   // the page's rows
```

## Where next

| You want to… | Go to |
|---|---|
| Filter with all 20 operators and boolean groups | [Filtering](./filtering) |
| Sort by multiple keys with null placement | [Sorting](./sorting) |
| Rank results, fuzzy / typo-tolerant search | [Search](./search) |
| Offset, keyset (cursor), the cursor codec, and `Dataset` | [Pagination](./pagination) |
| Paginate a database query | [Prisma](./integrations/prisma) · [Drizzle](./integrations/drizzle) |
| Parse pagination from a request | [Express](./integrations/express) |
