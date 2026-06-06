---
sidebar_position: 2
title: Keyset (cursor) pagination
---

# Keyset (cursor) pagination

Keyset pagination — also called cursor pagination — pages by remembering the **ordering
values of the last row you saw** instead of counting rows. Where offset pagination says
"skip 80 rows, take 20", keyset says "give me the 20 rows ordered after this boundary".

That difference matters at scale:

- **Stable under writes.** Inserts and deletes don't shift a `LIMIT/OFFSET` window, so you
  never skip or repeat rows between page loads.
- **Fast deep into the result set.** The database seeks to the boundary using the
  `ORDER BY` index instead of scanning and discarding `OFFSET` rows.

The trade-off is that you can only move relative to a cursor (next / previous), not jump to
an arbitrary page number — which is exactly the model APIs and infinite-scroll UIs want.

## The cursor is portable

A cursor is an opaque, URL-safe string that encodes the boundary row's ordering values.
The codec lives in the Rust core, so a cursor minted by one language decodes byte-for-byte
in another — a Python service and a TypeScript client share one keyset scheme. See
[cursor encoding](../concepts/cursor-encoding) for the format and round-trip guarantees.

```ts
import { encodeCursor, decodeCursor } from "@cyblow/paginate";

const cursor = encodeCursor([42, "2025-06-01T00:00:00"]);
decodeCursor(cursor); // → [42, "2025-06-01T00:00:00"]
```

## Parameters

`CursorParams` holds a `limit` plus at most one of `after` / `before` (they're mutually
exclusive — pass `after` to page forward, `before` to page backward, or neither for the
first page). The combination is validated at construction by the core.

```python
from pypaginate import CursorParams

first   = CursorParams(limit=20)                 # first page
forward = CursorParams(limit=20, after=cursor)   # page forward
back    = CursorParams(limit=20, before=cursor)  # page backward
```

```ts
import { CursorParams } from "@cyblow/paginate";

const first   = new CursorParams({ limit: 20 });                // first page
const forward = new CursorParams({ limit: 20, after: cursor }); // page forward
const back    = new CursorParams({ limit: 20, before: cursor }); // page backward
```

## The result page

A keyset query returns a `CursorPage`. It carries the page's `items` and the cursors for
navigating outward — but no `total` or `page`/`pages`, since counting rows is the offset
model that keyset deliberately avoids.

| Field | Meaning |
|---|---|
| `items` | The rows on this page |
| `limit` | Requested page size |
| `has_next` / `hasNext` | A following page exists (`next_cursor` is set) |
| `has_previous` / `hasPrevious` | A preceding page exists (`previous_cursor` is set) |
| `next_cursor` / `nextCursor` | Cursor to fetch the next page, or `null` |
| `previous_cursor` / `previousCursor` | Cursor to fetch the previous page, or `null` |

To page forward, feed `next_cursor` back in as the next request's `after`; to page
backward, feed `previous_cursor` in as `before`.

## Keyset pagination is database-backed

There is no in-memory keyset helper — for a list you already hold, offset pagination is
simpler and just as fast. Keyset pays off against a **database query**, where it's driven
by the ORM integrations. They read the `ORDER BY` of your query, render the lexicographic
keyset comparison (the core supplies the predicate structure), over-fetch `limit + 1` rows
to detect a further page, trim, and assemble a `CursorPage` with the edge cursors.

The keyset-capable integrations are **SQLAlchemy** and **Django** (Python) and **Prisma**
and **Drizzle** (TypeScript). See their integration guides for end-to-end examples; the
cursor format is the same across all of them because the codec is shared.

:::tip Why the predicate is shared
For `ORDER BY (a ASC, b DESC)` and a cursor `(v1, v2)`, the boundary comparison is
`(a > v1) OR (a = v1 AND b < v2)`. The Rust core owns the *structure* of that OR-of-AND
predicate (and flips the directions for backward paging); each adapter only renders the
`column OP value` comparisons in its own query builder. That's how every language agrees on
which rows a cursor includes.
:::
