---
sidebar_position: 10
title: Errors & limits
description: The shared exception hierarchy (PaginateError and friends), what raises each one, how to handle them in Python and TypeScript, and the engine's built-in limits.
---

# Errors & limits

Every failure raised by the engine belongs to **one shared taxonomy**. The Rust core
classifies the error; each language binding maps it to a host-native exception with the
**same hierarchy and message**, so handling code is parallel across languages — see
[parity](./parity).

## The exception hierarchy

```text
PaginateError                 (TypeScript & Python; aliased PaginationError)
├── ConfigurationError        invalid adapter / ORM configuration
├── ValidationError           bad page / limit / cursor input
├── FilterError               a filter could not be evaluated
│   └── FilterValidationError a filter spec failed validation (e.g. nesting depth)
├── SortError                 values are not order-comparable
└── SearchError               a search operation failed
    └── SearchQueryError      the search query failed validation (e.g. too long)
```

Catch `PaginateError` (Python) / `PaginateError` (TypeScript) to handle any of them at
once, or a specific subclass for finer control. In Python, `FilterError` and
`ValidationError` also carry an optional `field`, and **every** error carries a
structured `details` mapping for programmatic handling.

## What raises each error

| Error | Raised when… | Example message |
|---|---|---|
| `ValidationError` | `page < 1`, `limit < 1`, `limit > MAX_LIMIT`, or both `after` and `before` set | `limit must not exceed 1000` · `after and before are mutually exclusive` |
| `FilterError` | unknown operator, an unresolved field path, a `_`-prefixed segment, an operand of the wrong type, `between` without exactly 2 elements, or a regex over 200 chars | `unknown operator: zzz` · `Between requires exactly 2 elements` |
| `FilterValidationError` | a filter group is nested beyond `MAX_FILTER_DEPTH` (checked at construction) | `FilterGroup nesting must not exceed 5 levels` |
| `SortError` | a sort key compares values that aren't order-comparable (e.g. number vs string) | `field values are not order-comparable` |
| `SearchQueryError` | a search query exceeds `MAX_QUERY_LEN` (validated via `search_spec`) | `Query must not exceed 500 characters` |
| `ConfigurationError` | an adapter can't resolve a field to a column, or a backend is misconfigured | — |

## Malformed cursors

Decoding a keyset cursor is separate from the validation above. When the ORM keyset
adapters decode a client-supplied `after` / `before`, a malformed, truncated, or
tampered cursor raises **`InvalidCursorError`** (`invalid cursor: …`) from the native
core — **not** a `ValidationError`.

:::caution Catch it as `ValueError`
In Python, `InvalidCursorError` is a subclass of `ValueError` (via the native
`pypaginate._core.PaginateError`) but is **not** part of the `pypaginate.errors`
hierarchy — so `except PaginateError` will **not** catch it. Catch `ValueError` (or
`pypaginate._core.InvalidCursorError`). In TypeScript, `decodeCursor` likewise throws on
a malformed cursor.
:::

Because cursors arrive from clients, treat a decode failure as a bad request:

```python
from pypaginate import CursorParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend

try:
    page = SyncSQLAlchemyCursorBackend(session).fetch_page(stmt, CursorParams(limit=20, after=token))
except ValueError:           # malformed / tampered cursor
    raise HTTPException(status_code=400, detail="invalid cursor")
```

## Handling errors

### Python

```python
from pypaginate import paginate, OffsetParams
from pypaginate.errors import ValidationError, FilterError, PaginateError

try:
    page = paginate(items, OffsetParams(page=0))
except ValidationError as exc:
    print(exc)          # "page must be >= 1"
    print(exc.details)  # structured context
except PaginateError:
    ...                 # any other paginate failure
```

### TypeScript

The error classes are exported for `instanceof` checks:

```ts
import { paginate, OffsetParams, ValidationError, PaginateError } from "@cyblow/paginate";

try {
  const page = paginate(items, new OffsetParams({ page: 0 }));
} catch (err) {
  if (err instanceof ValidationError) console.error(err.message);
  else if (err instanceof PaginateError) {/* any other paginate failure */}
  else throw err;
}
```

## Limits

These limits live once in the core and are shared by every language (the Python values
are exposed as constants, e.g. `pypaginate.MAX_LIMIT`):

| Limit | Value | Applies to |
|---|---|---|
| `MAX_LIMIT` | **1000** | page size — `limit` on `OffsetParams` / `CursorParams` |
| `MAX_FILTER_DEPTH` | **5** | nesting depth of `And()` / `Or()` filter groups |
| `MAX_QUERY_LEN` | **500** | search query length (enforced when you call `search_spec`) |
| regex length | **200** chars | the `regex` filter operator's value |
| `between` arity | exactly **2** | the `between` operator's `[lo, hi]` value |

`MAX_LIMIT` is a denial-of-service guard: a request for a larger page is rejected with a
`ValidationError` rather than silently clamped. The trigram `threshold` (search) is a
`0–100` similarity; values outside that range simply match nothing rather than raising.

## See also

- [Filtering & operators](./filtering) · [Sorting](./sorting) · [Search & ranking](./search)
- Language handling in context: [Python filtering](../python/filtering#errors) ·
  [TypeScript filtering](../typescript/filtering#errors)
