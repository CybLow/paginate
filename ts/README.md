# @cyblow/paginate

Idiomatic TypeScript over the native
[`@cyblow/paginate-core`](https://www.npmjs.com/package/@cyblow/paginate-core)
engine — the JS/TS adapter in the polyglot
[paginate](https://github.com/CybLow/paginate) workspace. The Rust core
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
  speed, prefer native `Array` methods (see
  [BENCHMARKS.md](https://github.com/CybLow/paginate/blob/main/docs/BENCHMARKS.md)).

## Usage

```ts
import { paginate, OffsetParams, And, Or, encodeCursor } from "@cyblow/paginate";

// In-memory offset pagination: filter + sort + page in one native call.
const page = paginate(rows, new OffsetParams({ page: 1, limit: 20 }), {
  filters: [{ field: "age", operator: "gte", value: 18 }],
  sorting: [{ field: "createdAt", direction: "desc" }],
});
page.items; // your own row objects for this page
page.total; // total matched (number)

// Nested boolean groups:
import { filterGroupIndices } from "@cyblow/paginate";
const group = And(
  Or(
    { field: "country", operator: "eq", value: "FR" },
    { field: "country", operator: "eq", value: "BE" },
  ),
  { field: "age", operator: "gte", value: 18 },
);
filterGroupIndices(rows, group);
```

### ORM cursor (keyset) adapters

Cursor pagination is a database concern. The `prisma` and `drizzle` adapters
render the core's portable keyset predicate, so a cursor minted here is
byte-compatible with the Python / SQLAlchemy / Django side.

```ts
import { prisma, encodeCursor, decodeCursor } from "@cyblow/paginate";

// where-fragment for the page AFTER `lastRow`, ORDER BY (createdAt asc, id asc):
const where = prisma.keysetWhere(
  [{ field: "createdAt" }, { field: "id" }],
  decodeCursor(req.query.after),
);
const rows = await db.post.findMany({
  where,
  orderBy: [{ createdAt: "asc" }, { id: "asc" }],
  take: 20,
});
const next = encodeCursor([rows.at(-1).createdAt.toISOString(), rows.at(-1).id]);
```

Drizzle is identical but takes its operators injected
(`drizzle.keysetCondition(keys, values, { and, or, gt, lt, eq })`), and
`express.offsetParamsFromQuery(req.query)` / `cursorParamsFromQuery(req.query)`
parse + validate request params.

For a stable in-memory array, build a resident `Dataset` once and call
`filter` / `sort` / `search` / `page` many times — that fused path is the one
shape where crossing into Rust pays off for JS.

## Development

```bash
bun run build   # tsc -> dist/
bun run test    # build native addon + tsc + bun test test/
bun run lint    # eslint
bun run format  # prettier --write
```

This package depends on the native addon
[`@cyblow/paginate-core`](https://www.npmjs.com/package/@cyblow/paginate-core),
which ships per-platform binaries via napi-rs `optionalDependencies`. In the
monorepo the addon is built from `crates/node` (`bun run build:native`); the
published package pulls the prebuilt addon from npm.
