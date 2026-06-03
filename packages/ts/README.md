# @cyblow/paginate

Idiomatic TypeScript over the native [`paginate-core`](../../crates/node) engine —
the JS/TS adapter in the polyglot [paginate-core](../../) workspace. The Rust core
owns all computation and speaks only plain data; this package maps your ORM models
(Prisma / Drizzle / TypeORM / …) to the DTO _port_ the engine understands. The ORM
lives **here**, never in the core:

```
ORM model ─▶ plain DTO ─▶ native core call ─▶ result ─▶ apply to DB
```

## What to reach for

- **Cursor codec** (`encodeCursor` / `decodeCursor`) — the headline: a cursor minted
  by a Python service decodes byte-for-byte here and vice-versa, so a polyglot system
  shares one keyset scheme with zero drift. `normalize` and the pagination math are
  here for the same behaviour-consistency reason.
- **Resident `Dataset`** — marshal a stable in-memory array **once**, then run
  `filter` / `sort` / `search` / `page` many times. The fused one-call `page()`
  (filter → sort → paginate, returning only the page) is the one shape where crossing
  into Rust pays off for JS; the per-op helpers and one-shot `filterIndices` /
  `sortIndices` / `searchIndices` exist for _behaviour parity_ — for raw single-op
  speed, prefer native `Array` methods (see [`BENCHMARKS.md`](../../BENCHMARKS.md)).

## Usage

```ts
import { Dataset, encodeCursor, decodeCursor } from "@cyblow/paginate";

const ds = new Dataset(rows); // marshalled into the core once
const page = ds.page(1, 20, {
  filters: [{ field: "age", op: "gte", value: 18 }],
  sorting: [{ field: "createdAt", direction: "desc" }],
});
page.items; // your own row objects for this page

const cursor = encodeCursor([lastRow.createdAt.toISOString(), lastRow.id]);
const values = decodeCursor(cursor);
```

## Development & publishing

```bash
npm run build   # tsc -> dist/
npm test        # build + node --test
npm run lint    # eslint
npm run format  # prettier --write
```

During development this package depends on the addon via a workspace path
(`"paginate-core": "file:../../crates/node"`). **Before publishing**, that must point
at the published native addon (and the addon ships per-platform binaries via napi-rs
`optionalDependencies`). Publishing is not yet wired up.
