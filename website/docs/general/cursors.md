---
sidebar_position: 6
title: Cursors
---

# Cursors

Keyset ([cursor](./pagination-models#keyset-cursor-pagination)) pagination encodes the
ordering values of the boundary row into an opaque, URL-safe string instead of an
offset — so paging stays correct and fast even as rows are inserted or deleted. The
codec lives in the Rust core, which makes cursors **portable across languages**.

## A typed, deterministic format

The encoding is deterministic and typed: integers, strings, booleans, `null`, and
tagged temporal / decimal values all round-trip. A cursor is the ordered list of the
`ORDER BY` columns' values for the boundary row, serialized to JSON and base64url-
encoded. Typed scalars (datetime, date, decimal, uuid) are tagged so they decode back
to the same type, which is what lets keyset comparisons stay correct across languages.

The [parity](./parity) fixture pins the format **byte-for-byte** across Rust, Python,
and TypeScript.

## Encoding and decoding

TypeScript exposes the codec directly:

```ts
import { encodeCursor, decodeCursor } from "@cyblow/paginate";

const cursor = encodeCursor([42, "2025-06-01T00:00:00"]);
decodeCursor(cursor); // → [42, "2025-06-01T00:00:00"]
```

:::tip
Try `encodeCursor` / `decodeCursor` live in the **[Playground](/playground)** — it runs
the same Rust codec in your browser.
:::

In Python the same codec powers the SQLAlchemy and Django keyset adapters rather than
being called directly: the adapters over-fetch `limit + 1`, trim, and emit a
`CursorPage` with `next_cursor` / `previous_cursor`. See the
[Python](../python/pagination#keyset-cursor-pagination) and [TypeScript](../typescript/pagination#keyset-cursor-pagination)
pagination guides for end-to-end keyset examples.

## Why it's shared

Because the codec is one implementation:

- a cursor minted by a **Python** service decodes in a **TypeScript** client and back;
- switching a service's implementation language **never invalidates** a client's
  existing cursors;
- every ORM adapter (SQLAlchemy, Django, Prisma, Drizzle) produces the **same** cursor
  bytes for the same ordering values.

## The keyset predicate

For `ORDER BY (a ASC, b DESC)` and a cursor `(v1, v2)`, the boundary comparison is:

```text
(a > v1) OR (a = v1 AND b < v2)
```

The Rust core owns the **structure** of that OR-of-AND predicate (and flips the
directions for backward paging); each ORM adapter only renders the `column OP value`
comparisons in its own query builder. That's how every language agrees on exactly
which rows a cursor includes.
