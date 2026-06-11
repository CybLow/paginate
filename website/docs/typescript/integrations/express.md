---
sidebar_position: 1
title: Express
---

# Express

Parse `req.query` into validated pagination params. The adapter is
framework-agnostic — it only needs an object of query values, so it also fits
**Fastify**, **Koa**, and `URLSearchParams` (via `Object.fromEntries`). The
parsed `OffsetParams` / `CursorParams` are validated by the Rust core, so the
range and exclusivity rules match every other package — see
[cross-language parity](../../general/parity).

## Install

```bash
npm i @cyblow/paginate
```

```ts
import { express, paginate } from "@cyblow/paginate";
```

## Public API

```ts
// { page, limit } from the query (validated; throws ValidationError if bad)
express.offsetParamsFromQuery(query: QueryLike): OffsetParams;

// { limit, after?, before? } from the query (after/before mutually exclusive)
express.cursorParamsFromQuery(query: QueryLike): CursorParams;
```

`QueryLike` is `Record<string, string | string[] | undefined>` — Express's
`req.query` shape. Missing or empty values fall back to the defaults
(`page=1`, `limit=20`). When a query value is an array, the first element wins.

## Offset endpoint

Parse the params, then paginate your data. For an in-memory array, hand the
params straight to `paginate` (identical results to pypaginate — see
[parity](../../general/parity)):

```ts
import express from "express";
import { express as paginateExpress, paginate, ValidationError } from "@cyblow/paginate";

const app = express();

app.get("/users", (req, res) => {
  try {
    const params = paginateExpress.offsetParamsFromQuery(req.query);
    const page = paginate(users, params, {
      filters: [{ field: "status", operator: "eq", value: "active" }],
      sorting: [{ field: "created_at", direction: "desc" }],
    });
    res.json({ items: page.items, total: page.total, pages: page.pages });
  } catch (err) {
    if (err instanceof ValidationError) {
      return res.status(400).json({ error: err.message });
    }
    throw err;
  }
});
```

## Cursor endpoint

`cursorParamsFromQuery` reads `?limit=&after=&before=` (passing both `after` and
`before` throws `ValidationError`). In-memory keyset pagination is not supported —
forward the parsed `CursorParams` to a database adapter such as
[Prisma](./prisma) or [Drizzle](./drizzle):

```ts
app.get("/posts", async (req, res) => {
  const params = paginateExpress.cursorParamsFromQuery(req.query);
  const { items, nextCursor } = await page(params); // your Prisma/Drizzle keyset query
  res.json({ items, nextCursor });
});
```

## Other frameworks

Any object of query values works. With the WHATWG `URLSearchParams` (Fetch /
Koa / Fastify), convert first:

```ts
const url = new URL(request.url);
const params = paginateExpress.offsetParamsFromQuery(Object.fromEntries(url.searchParams));
```
