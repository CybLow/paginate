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

**New — one-shot `search` / `filter` / `sort`.** For querying an in-memory list
directly (no backend), the package now exports three helpers alongside
`paginate`:

```python
from pypaginate import search, filter, sort
from pypaginate import FilterSpec, SortSpec, SearchSpec, SortDirection

adults = filter(users, FilterSpec(field="age", operator="gte", value=18))
ranked = search(users, SearchSpec(query="alice", fields=("name", "email")))
ordered = sort(users, SortSpec(field="created_at", direction=SortDirection.DESC))
```

Each returns a new list of host items (search in ranked order). The TS package
(`@cyblow/paginate`) exports the same `search` / `filter` / `sort` for symmetry.

What changed under the hood (only relevant if you imported internals):

- **Invalid enum tokens now raise instead of defaulting.** The canonical
  string↔enum parsing moved into the Rust core (`<Enum>::from_token`), shared by
  every binding. The tokens the package emits are unchanged, so this only affects
  hand-built specs that passed an unrecognized value (e.g. a misspelled mode),
  which now raise a `FilterError`/`SortError`/`SearchError` rather than silently
  using the default.

- **The native `_core` extension is mandatory** — there is no pure-Python
  fallback for the cursor codec, offset math, or fuzzy search. Install a wheel
  (or build from source with a Rust toolchain); PyPy is unsupported.
- **Fuzzy / token-sort search now uses trigram similarity (pg_trgm model), not
  rapidfuzz.** `FuzzyMode.FUZZY` scores trigram *containment* (the query's
  trigrams found in the field) and `FuzzyMode.TOKEN_SORT` scores trigram
  *Jaccard* (word-order agnostic). This is O(len) set-overlap (no edit-distance
  DP), much faster, length-normalized, and transposition-tolerant — and it lets a
  resident `Dataset` prefilter candidates with an exact inverted index. **Scores
  and ranking differ from the old rapidfuzz output**, and the default
  `SearchSpec.threshold` drops from **75 → 30** (trigram similarity, like
  pg_trgm's 0.3). Trigram is strong on names/titles/multi-word text but weaker on
  very short single-word typos; raise/lower `threshold` for your data. The
  `rapidfuzz` dependency is removed.
- Page metadata and `OffsetParams.clamp` are derived from `_core`
  (`offset_meta` / `clamp_page`) instead of recomputed in Python — no behavior
  change, one source of truth.

Removed (breaking, but **dev/internal only** — no public API affected):

- **The `pypaginate` console-script CLI is gone.** It was a dev wrapper around
  `ruff` / `mypy` / `pytest` / `uv`; use the repository's `just` (or `make`)
  recipes instead (`just py-lint`, `just py-type`, `just py-test`, …).
- **The internal in-memory "engine" import paths were removed:**
  `pypaginate.filtering` / `pypaginate.sorting` / `pypaginate.search` (the
  `FilterEngine` / `SortEngine` / `SearchEngine` classes), `pypaginate.filtering.accessor`,
  and `pypaginate.text.normalize`. These were thin facades over the native
  `_core` engine. In-memory filtering, sorting, and ranked search are available
  through the public `Dataset`, the `pypaginate.adapters.memory.*` backends, or
  the internal `pypaginate._native` functions; `normalize_text` is now
  `pypaginate._native.normalize_text` (field-path resolution lives in the core).
- `pypaginate.__version__` is now read from the installed package metadata
  instead of a hard-coded literal, so it always matches the released version.

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

New public API: `keyset::keyset_terms` (portable lexicographic keyset predicate),
`search::{trigram, TrigramIndex, search_with_index, retain_matching}` for
trigram-similarity fuzzy search with an exact inverted-index prefilter, and
`pipeline::{offset_page_searched, SearchStage}` —
which folds an optional search match-filter into the one-pass `filter → search →
sort → paginate` (so `Dataset.page`/`paginate` does any combination in a single
FFI call). The `rapidfuzz` dependency was dropped (the fuzzy/token-sort scorers
are now trigram-based, see the Python section above).
