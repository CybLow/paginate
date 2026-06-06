---
sidebar_position: 3
---

# Cursor encoding

Keyset (cursor) pagination encodes the ordering values of the boundary row into an
opaque, URL-safe string instead of an offset — so paging stays correct and fast even
as rows are inserted or deleted. The codec lives in the Rust core, which makes cursors
**portable across languages**.

The encoding is deterministic and typed: integers, strings, booleans, `null`, and
tagged temporal / decimal values all round-trip. The [parity](./parity) fixture pins
it byte-for-byte across Rust, Python, and TypeScript.

```ts
// TypeScript exposes the codec directly:
import { encodeCursor, decodeCursor } from "@cyblow/paginate";

const cursor = encodeCursor([42, "2025-06-01T00:00:00"]);
decodeCursor(cursor); // → [42, "2025-06-01T00:00:00"]
```

In Python, the same codec powers the SQLAlchemy and Django keyset adapters, which
over-fetch `limit + 1`, trim, and emit a `CursorPage` with `next_cursor` /
`previous_cursor`. See the integration guides for end-to-end keyset examples.
