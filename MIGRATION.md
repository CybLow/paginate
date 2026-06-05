# Migration guide

## → v0.3 ("fat core, thin adapters")

v0.3 finishes the move of **all** computation into the shared Rust core
(`paginate-core`): cursor codec, offset math, page assembly, filter/sort/search,
and the keyset (cursor) predicate now have a single implementation that the
Python (`pypaginate`) and JS (`@cyblow/paginate`) packages wrap as thin, typed
adapters. The headline guarantee is cross-language parity — a frozen fixture
asserts the Rust, Python, and JS engines produce byte-identical cursors and
identical filter/sort/search results.

### Python (`pypaginate`)

Most code needs **no change** — `paginate(...)`, `OffsetParams` / `CursorParams`,
`FilterSpec` / `SortSpec` / `SearchSpec`, `OffsetPage` / `CursorPage`, and the
FastAPI / SQLAlchemy adapters are unchanged.

What changed under the hood (only relevant if you imported internals):

- **The native `_core` extension is mandatory** — there is no pure-Python
  fallback for the cursor codec, offset math, or fuzzy search. Install a wheel
  (or build from source with a Rust toolchain); PyPy is unsupported.
- **Fuzzy / token-sort search is now correct and consistent.** The in-memory
  `MemorySearchBackend` previously scored `FuzzyMode.FUZZY` with a hand-rolled
  character-overlap heuristic that diverged from the rapidfuzz scoring used
  everywhere else, and silently treated `FuzzyMode.TOKEN_SORT` as an exact
  match. Both now run through the core's rapidfuzz `partial_ratio` /
  `token_sort_ratio`. If you relied on the old approximate scores, results may
  shift slightly (they are now correct).
- Page metadata and `OffsetParams.clamp` are derived from `_core`
  (`offset_meta` / `clamp_page`) instead of recomputed in Python — no behavior
  change, one source of truth.

New: **`pypaginate.adapters.django`** — `DjangoBackend`,
`DjangoFilterBackend`, `DjangoSortBackend`, `DjangoSearchBackend`, and
`DjangoCursorBackend` for Django QuerySets (offset + keyset). Install with
`pip install pypaginate[django]`.

### JavaScript / TypeScript (`@cyblow/paginate`)

The package was completed to parity with the Python one and split into modules.
**Breaking changes** (it was a 0.1.x preview):

| Before | After |
| --- | --- |
| `filterIndices(items, [{ field, op, value }])` | `[{ field, operator, value }]` — `operator` is canonical (`op` still accepted by the binding) |
| `searchIndices(items, query, fields, opts)` | `searchIndices(items, { query, fields, mode, fuzzy, threshold, ... })` |
| `ds.page(1, 20, opts)` | `ds.page(new OffsetParams({ page: 1, limit: 20 }), opts)` |
| `ds.search(query, fields, opts)` | `ds.search({ query, fields, mode, ... })` |

New surface:

- `OffsetParams` / `CursorParams` (validated, with `MAX_LIMIT`, `.offset`,
  `.clamp`), `OffsetPage<T>` / `CursorPage<T>` + `offsetPage` / `cursorPage`
  builders, `And()` / `Or()` filter-group builders, a top-level `paginate()`
  for arrays, and `ValidationError` / `PaginateError`.
- Adapters: `express` (req.query → params), `prisma` (`where` + `skip`/`take`),
  `drizzle` (keyset `where` with injected operators). All render the core's
  portable keyset predicate, so cursors match the Python/SQLAlchemy side.

### Rust core (`paginate-core`)

Additive only. New public API: `keyset::keyset_terms` (portable lexicographic
keyset predicate) and a `fuzzy`-aware `search::match_indices`.
