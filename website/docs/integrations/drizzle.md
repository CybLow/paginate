---
sidebar_position: 5
title: Drizzle
---

# Drizzle

Build the keyset (cursor) `where` condition for Drizzle ORM from the core's
portable predicate. Drizzle's operators (`and`, `or`, `gt`, `lt`, `eq`) and
column references are **injected**, so the adapter carries no `drizzle-orm`
dependency and works with any Drizzle version. Cursors are byte-compatible with
the other adapters; see [cross-language parity](../concepts/parity).

## Install

```bash
npm i @cyblow/paginate
# drizzle-orm is your own dependency
```

```ts
import { drizzle, CursorParams, OffsetParams, encodeCursor, decodeCursor } from "@cyblow/paginate";
import { and, or, gt, lt, eq, desc } from "drizzle-orm";
```

## Public API

```ts
drizzle.keysetCondition(
  keys: readonly { column: unknown; direction?: "asc" | "desc" }[],
  cursorValues: readonly (string | number | boolean | null)[],
  ops: { and; or; gt; lt; eq },          // injected from "drizzle-orm"
  opts?: { backwards?: boolean },
): unknown;                              // a Drizzle `where` condition
```

## Keyset (cursor) pagination

`keysetCondition` renders the lexicographic OR-of-AND predicate using the
injected operators, so you can drop it straight into `.where()`:

```ts
const keys = [
  { column: posts.score, direction: "desc" },
  { column: posts.id, direction: "desc" },
] as const;
const ops = { and, or, gt, lt, eq };

async function page(params: CursorParams) {
  const token = params.after ?? params.before;
  const backwards = params.before !== null;
  const where = token
    ? drizzle.keysetCondition(keys, decodeCursor(token), ops, { backwards })
    : undefined;

  const rows = await db
    .select()
    .from(posts)
    .where(where)
    .orderBy(desc(posts.score), desc(posts.id))
    .limit(params.limit + 1);

  const hasNext = rows.length > params.limit;
  const items = hasNext ? rows.slice(0, params.limit) : rows;
  const last = items.at(-1);
  const nextCursor = hasNext && last ? encodeCursor([last.score, last.id]) : null;
  return { items, nextCursor };
}
```

To combine with your own filters, pass `and(yourCondition, keysetCondition(...))`.
Pass `{ backwards: true }` for a `before` cursor — it flips each key's strict
comparison; flip the `orderBy` and reverse the returned rows to keep display order
stable.

## Offset pagination

Drizzle's offset query is a one-liner — feed it `OffsetParams`:

```ts
const params = new OffsetParams({ page: 2, limit: 20 });
const rows = await db.select().from(posts).limit(params.limit).offset(params.offset);
```

For `total` / `pages` / `hasNext` metadata, count separately and feed the count to
the package's `offsetMeta(page, limit, total)` helper (see the
[architecture](../concepts/architecture) overview).
