---
sidebar_position: 5
title: Pagination models
description: Offset (page/limit) vs. keyset (cursor) pagination — how each works, their trade-offs, and which to choose.
---

# Pagination models

paginate supports the two standard pagination models. They solve the same problem —
returning data one page at a time — but make different trade-offs. Both are available
in every package; this page explains *which to choose*. For runnable code see the
[Python](../python/pagination) and [TypeScript](../typescript/pagination) pagination
guides.

## Offset pagination

Offset pagination addresses a page by a **1-based page number** and a **limit** (rows
per page). Page 3 with a limit of 20 means "skip 40 rows, take 20".

```text
page 1: rows  1–20      page 2: rows 21–40      page 3: rows 41–60
```

The result page carries the rows plus derived metadata: `total`, `pages`, `limit`, and
`has_next` / `has_previous`.

**Reach for offset when:**

- you want **jump-to-page** navigation or a page count (`Page 3 of 27`);
- the result set is **bounded** and not changing under you;
- you're paginating an **in-memory list** — it's the simplest model and just as fast.

**Be aware that:**

- requesting a page **past the end** is not an error — you get empty items with the
  metadata still describing the full dataset;
- on a large or frequently-written table, deep pages get **slow** (the database scans
  and discards the skipped rows) and can **skip or repeat** rows when data shifts
  between requests. That's what keyset fixes.

## Keyset (cursor) pagination

Keyset pagination — also called cursor pagination — pages by remembering the
**ordering values of the last row you saw** instead of counting rows. Where offset
says "skip 80, take 20", keyset says "give me the 20 rows ordered *after this
boundary*".

```text
?after=<cursor for row 40>  →  the next 20 rows after that boundary
```

```mermaid
flowchart LR
    P1["Page 1: first rows"] -->|"next_cursor"| P2["Page 2: after = cursor"]
    P2 -->|"next_cursor"| P3["Page 3: after = cursor"]
    P3 -->|"next_cursor"| P4["..."]
```

The result page carries the rows plus a `next_cursor` and `previous_cursor` (opaque,
URL-safe strings) and `has_next` / `has_previous` — but **no** `total` or page number,
since counting rows is exactly the offset model keyset avoids.

**Reach for keyset when:**

- the data is **large** or **changes often** — keyset is stable under inserts/deletes,
  so you never skip or repeat rows between page loads;
- you page **deep** into a result set — the database seeks to the boundary using the
  `ORDER BY` index instead of scanning the skipped rows;
- you're building **infinite scroll** or a **"load more"** API, where relative
  next/previous navigation is exactly the model.

**Be aware that:**

- you can only move **relative** to a cursor (next / previous), not jump to an
  arbitrary page;
- the query **must** have an `ORDER BY` that uniquely orders rows — append a primary
  key as a tiebreaker.

## The cursor is portable

A keyset cursor encodes the boundary row's ordering values with the shared codec, so a
cursor minted in one language decodes byte-for-byte in another. See
[cursors](./cursors) for the format and round-trip guarantees.

## Side by side

| | Offset | Keyset (cursor) |
|---|---|---|
| Addressed by | page number + limit | a cursor (after / before) |
| Jump to arbitrary page | ✅ | ❌ (next / previous only) |
| `total` / page count | ✅ | ❌ (by design) |
| Stable under writes | ❌ | ✅ |
| Deep-page performance | degrades | constant (index seek) |
| In-memory support | ✅ | ❌ (database-backed) |
| Best for | admin tables, bounded lists | feeds, infinite scroll, large tables |

## Next

- Python: [pagination guide](../python/pagination) (offset, keyset, `Dataset`).
- TypeScript: [pagination guide](../typescript/pagination).
- [Cursors](./cursors) — the portable, typed wire format.
