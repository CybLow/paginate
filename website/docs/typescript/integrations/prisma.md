---
sidebar_position: 2
title: Prisma
---

# Prisma

Build the `where` fragment and `skip`/`take` args for offset and keyset (cursor)
pagination. The adapter is **pure data** — it carries no `@prisma/client`
dependency, so it works with any Prisma version. Cursors are byte-compatible with
the Python and Rust adapters; see [cross-language parity](../../general/parity).

## Install

```bash
npm i @cyblow/paginate
# @prisma/client is your own dependency
```

The adapter is exposed as a namespace from the main package:

```ts
import { prisma, OffsetParams, CursorParams, encodeCursor, decodeCursor } from "@cyblow/paginate";
```

## Public API

```ts
// { skip, take } for prisma.model.findMany offset pagination
prisma.offsetArgs(params: OffsetParams): { skip: number; take: number };

// A `where` fragment selecting rows strictly after `cursorValues` along `keys`
prisma.keysetWhere(
  keys: readonly { field: string; direction?: "asc" | "desc" }[],
  cursorValues: readonly (string | number | boolean | null)[],
  opts?: { backwards?: boolean },
): Record<string, unknown>;
```

## Offset pagination

```ts
const params = new OffsetParams({ page: 2, limit: 20 });
const [items, total] = await Promise.all([
  db.user.findMany({ where: { status: "active" }, ...prisma.offsetArgs(params) }),
  db.user.count({ where: { status: "active" } }),
]);
```

`offsetArgs` returns `{ skip: params.offset, take: params.limit }`. Pair the count
with the package's `offsetMeta(page, limit, total)` helper if you want
`pages` / `hasNext` metadata (see the [architecture](../../general/architecture)
overview).

## Keyset (cursor) pagination

`keysetWhere` renders the core's portable keyset predicate as a nested boolean
`where` object. For `keys: [{ field: "score", direction: "desc" }, { field: "id",
direction: "desc" }]` after `[42, 100]` it produces:

```json
{ "OR": [ { "score": { "lt": 42 } },
          { "AND": [ { "score": 42 }, { "id": { "lt": 100 } } ] } ] }
```

A full forward page, over-fetching `limit + 1` to detect a next page:

```ts
const keys = [
  { field: "score", direction: "desc" },
  { field: "id", direction: "desc" },
] as const;

async function page(params: CursorParams) {
  const token = params.after ?? params.before;
  const backwards = params.before !== null;
  const cursorWhere = token
    ? prisma.keysetWhere(keys, decodeCursor(token), { backwards })
    : undefined;

  const rows = await db.post.findMany({
    where: cursorWhere ? { AND: [{ published: true }, cursorWhere] } : { published: true },
    orderBy: keys.map((k) => ({ [k.field]: k.direction })),
    take: params.limit + 1,
  });

  const hasNext = rows.length > params.limit;
  const items = hasNext ? rows.slice(0, params.limit) : rows;
  const last = items.at(-1);
  const nextCursor = hasNext && last ? encodeCursor([last.score, last.id]) : null;
  return { items, nextCursor };
}
```

Combine `keysetWhere` with your own filters via `{ AND: [yourWhere, keysetWhere(...)] }`
as shown. Pass `{ backwards: true }` for a `before` cursor — it flips each key's
strict comparison; flip your `orderBy` and reverse the returned rows to keep
display order stable.
