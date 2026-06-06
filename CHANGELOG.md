# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Performance
- **Fuzzy search skips re-normalizing already-clean text.** `normalize_text_cow`
  borrows its input unchanged when it is already normalized (lowercase ASCII,
  single-spaced — the common case for emails / ids / slugs / titles), so per-item
  trigram scoring and the resident index build allocate nothing for such fields.
  Clean A/B at 100k: `fuzzy_indexed/indexed` 16.3→15.7 ms (−3.6%), `fuzzy_multi`
  −1.2% (p<0.05); behaviour identical (a `proptest` pins `cow == owned`).
- **String filters allocate nothing per row.** The `contains` / `starts_with` /
  `ends_with` / `like` / `ilike` / `regex` operators (and the `in` / `not_in`
  string/dict path) now **borrow** each item's field value
  (`coerce::to_py_str_cow` → `Cow::Borrowed`) instead of cloning it into a fresh
  `String` for every row. The per-row heap allocation is gone; on a 100k
  `contains` scan the string-operator-specific cost (the part above the
  int-comparison baseline) drops ~65% (≈0.5 ms → ≈0.2 ms), behaviour identical.
- **Row-engine sort is ~3× faster** via decorate-sort-undecorate — each item's
  sort key is resolved once instead of on every comparison (100k rows, release:
  `single_int` 25.4→7.7 ms, `multi_int` 28.7→9.7 ms, the row pipeline 21.3→9.0 ms).
- **Exact (contains/prefix) search ~36% faster** — `normalize_text` folds its
  ASCII fast path into a single allocation (`search/contains` 5.6→3.6 ms at 100k).
- **Fuzzy search rebuilt on trigram similarity** (see Changed): replacing the
  rapidfuzz edit-distance DP with O(len) trigram set-overlap drops one-shot
  `search/fuzzy_multi` from the original 117.9 ms to ~53 ms at 100k, and a
  resident `Dataset`'s exact inverted-index prefilter cuts a selective fuzzy
  query a further ~3× (`fuzzy_indexed` 48.7→16.4 ms at 100k), with more pruning
  the rarer the query.
- **Search folded into the resident pipeline.** `core::pipeline` now does
  `filter → search → sort → paginate` in one pass (`offset_page_searched`), and
  `Dataset.page` takes a `search` arg. A `Dataset.paginate(...)` combining search
  with filters/sorting is now **one** FFI crossing instead of three per-stage
  calls — search is a match-filter (explicit sorting still orders) using the
  trigram index, so results are unchanged.

### Added
- **Top-level `search` / `filter` / `sort` helpers** in both packages
  (`pypaginate.search/filter/sort`, `@cyblow/paginate` `search/filter/sort`):
  one-shot, item-returning query functions over an in-memory sequence — the
  ergonomic complement to `paginate(...)`. They wrap the native engine and
  return host items (search in ranked order, filter in original order, sort
  stable); each accepts the existing spec objects.
- **Cross-language parity harness.** A frozen golden (`tests/fixtures/parity.json`)
  asserts the Rust core, the Python binding, and the Node/TS binding produce
  byte-identical cursors and identical filter/sort/search indices — wired into
  the CI `parity` job so the wire format and engine semantics cannot drift. The
  fixture now exercises **all 20 filter operators**, the `or` combinator, both
  null-placement branches, and the `prefix`/`contains`/`exact` search modes, so
  every enum branch the core parses is pinned across all three languages.
- **Portable keyset predicate in the core** (`core::keyset::keyset_terms`,
  exposed as `_core.keyset_terms` / `keysetTerms`): the lexicographic
  cursor comparison is built once in Rust and rendered by each adapter, so
  SQLAlchemy, Django, Drizzle, and Prisma share one keyset implementation.
- **Django adapter** (`pypaginate.adapters.django`, extra `[django]`):
  offset + keyset pagination and filter/sort/search backends for QuerySets.
- **Completed `@cyblow/paginate` (JS/TS) to parity:** `OffsetParams` /
  `CursorParams` (validated), `OffsetPage<T>` / `CursorPage<T>`, `And()` /
  `Or()` builders, a top-level `paginate()`, and `express` / `prisma` /
  `drizzle` adapters that render the core keyset predicate.

### Fixed
- **`paginate()` could return the wrong page type under `pypaginate[fast]`.**
  With msgspec installed, the page factories returned a msgspec `FastOffsetPage`/
  `FastCursorPage` `cast` to the declared Pydantic `OffsetPage`/`CursorPage`, so
  `isinstance(page, OffsetPage)` was `False` and FastAPI `response_model=OffsetPage`
  received a non-Pydantic object it could not validate. The factories now always
  return the real Pydantic page.
- **In-memory fuzzy search divergence.** `MemorySearchBackend`'s
  `FuzzyMode.FUZZY` path used a character-overlap heuristic that disagreed with
  the core's rapidfuzz scoring, and `FuzzyMode.TOKEN_SORT` was silently treated
  as an exact match. Both now run through the core's fuzzy-aware match-filter.

### Changed
- **Tooling modernized.** The JS package now uses **Bun** (runtime, package
  manager, and test runner — `bun.lock`, `bun test`); the Python type checker is
  now Astral's **ty** (replacing mypy). Loose boundary narrowing was rewritten
  from blanket `# type: ignore` to explicit `typing.cast(...)`, and the engine
  orchestration returns precise page types instead of `Any`.
- **Native engine is now mandatory.** All in-memory filtering, sorting, and
  ranked search (including fuzzy / token-sort) run through the bundled Rust
  `pypaginate._core` extension (maturin, abi3, CPython 3.11+), shared with the
  JS/TS port. The resident `pypaginate.Dataset` is 6.5–27× faster than the former
  pure-Python path (release build). Installing now uses a prebuilt wheel (or a
  Rust toolchain for source builds); PyPy is unsupported.
- **BREAKING: fuzzy / token-sort search now uses trigram similarity, not
  rapidfuzz.** `FuzzyMode.FUZZY` scores trigram containment, `FuzzyMode.TOKEN_SORT`
  scores trigram Jaccard (pg_trgm model). Scores and ranking differ from the old
  edit-distance output, the default `SearchSpec.threshold` is now **30** (was 75),
  and the `rapidfuzz` dependency is dropped. Trigram is strong on
  names/titles/multi-word text, weaker on very short single-word typos. A resident
  `Dataset` builds a trigram inverted index once and prefilters candidates for
  fuzzy queries (exact — no match dropped). Boolean fields now take the columnar
  fast path (~8× on bool-inclusive filters).
- **Input validation lives once in the Rust core.** The pagination-param rules
  (`page >= 1`, `1 <= limit <= MAX_LIMIT`, `after`/`before` mutual exclusion) and
  the `MAX_LIMIT` bound were hand-written and duplicated in both packages
  (Python Pydantic validators + a hand-rolled TS constructor, with the `1000`
  literal in each). They now live once in the core (`paginate_core::validate`,
  returning `CoreError::Validation`), exposed as `validate_offset`/`validate_cursor`
  + `MAX_LIMIT`; the Python and TS `OffsetParams`/`CursorParams` are thin holders
  that delegate to it (re-raising as their native `ValidationError`). No validator
  (Pydantic, zod, …) is load-bearing for the rules anymore — only the
  language-specific integer guard stays in the JS binding. The **spec** limits
  (`SearchSpec` query ≤ `MAX_QUERY_LEN`, `FilterGroup` depth ≤ `MAX_FILTER_DEPTH`)
  moved too: Python's validators delegate, and the napi binding now enforces them
  at the engine boundary — so the **TS package gains query-length and nesting-depth
  validation it previously lacked**, identical to Python's.
- **Core is the single source of truth for the domain contract.** The string ↔
  enum parsing for filter logic, sort direction, null placement, and search
  mode/fuzzy now lives once in the Rust core as `<Enum>::from_token` (returning
  `Result`); the PyO3 and napi bindings delegate to it instead of each carrying
  their own copy, so the wire vocabulary cannot drift between languages.
- **Python enum values are now the wire tokens.** `domain/enums.py` members carry
  their canonical token as the value (`SortDirection.ASC = "asc"`, was `auto()`),
  so `_native.py` bridges with a plain `member.value` and its five enum→string
  mapping dicts are gone (the last in-Python token duplication). Minor: an enum's
  `.value` is now its string token rather than an opaque int. An
  **unknown enum token now raises** (a `FilterError`/`SortError`/`SearchError`)
  instead of silently falling back to the default — the canonical tokens the
  packages emit are unchanged, so this only surfaces genuinely invalid input.
  The domain enums/specs are re-exported flat from the crate root and `CoreError`
  is `#[non_exhaustive]`.
- **Engine reorganized into focused modules under the 250-line limit.** The Rust
  core's `search`, `cursor`, `columnar`, `pipeline`, and `sort` modules are now
  directories (`mod.rs` gateway + submodules + co-located `tests.rs`); the
  benchmark file is split into one criterion target plus per-domain files and a
  shared `common/`; the PyO3 `engines` binding is split into `project`/`filter`/
  `mod`. Internal helpers (`accessor`, `coerce`, `error`) are now private modules
  — `lib.rs`'s flat re-exports are the crate's public surface. Behavior is
  unchanged (all parity/property suites pass).

### Removed
- **The `fast` / msgspec page path** (`FastOffsetPage`, `FastCursorPage`, and the
  `pypaginate[fast]` extra). It duplicated the page types for a page-construction
  micro-optimization (never the bottleneck — the Rust core and the query are) at
  the cost of returning a type that lied about being the declared Pydantic page.
  The single Pydantic `OffsetPage` / `CursorPage` is now the only page type, so
  it validates, serializes, and works as a FastAPI `response_model` everywhere.
- **BREAKING:** the pure-Python filter/sort engine and its public API —
  `pypaginate.filtering.OperatorRegistry`, `create_default_registry`, and the
  individual operator classes — are removed; the 20 operators now live in the
  native core, and `FilterEngine()` no longer takes a `registry` argument.
  Custom Python-registered operators are no longer supported. Nested
  `And`/`Or`/`FilterGroup` filtering is unchanged (now evaluated natively).
- The pure-Python search island (`search/parser.py`, `search/matching.py`) is
  removed; ranked search delegates to the core. The `rapidfuzz` Python
  dependency is gone (it now lives in the Rust wheel) — the
  `pypaginate[search]` extra is a no-op kept for compatibility.

### Planned for v0.3.0
- JSON Logic dict-to-FilterGroup parser for frontend integration
- Django `__` filter format parser
- `add_pagination(app)` zero-config FastAPI middleware
- HATEOAS link generation
- Additional ORM support (Beanie, Tortoise)

---

## [0.2.0] - 2025-XX-XX

### Added

#### Architecture
- Hexagonal architecture with domain/engine/adapter layers
- Protocol-based backends (`PaginationBackend`, `CursorBackend`, `FilterBackend`, `SortBackend`, `SearchBackend`)
- Universal `paginate()` entry point with Elysia-style type inference
- `SyncPipeline` and `AsyncPipeline` for composing filter + sort + search + paginate

#### Pagination
- `OffsetParams` / `OffsetPage` (replaces `PageParams` / `Page`)
- `CursorParams` / `CursorPage` for cursor/keyset pagination
- `OverflowStrategy` (EMPTY or CLAMP) for out-of-range pages
- Custom count query via `SQLAlchemyBackend(session, count_query=...)`
- Row deduplication via `SQLAlchemyBackend(session, unique=True)`
- `SyncSQLAlchemyBackend` and `SyncSQLAlchemyCursorBackend` for sync sessions
- Fast in-memory path (no backend allocation for list + OffsetParams)

#### Filtering
- 20 operators: eq, ne, gt, gte, lt, lte, in, not_in, contains, starts_with, ends_with, like, ilike, between, is_null, is_not_null, regex, empty, not_empty, exists
- `FilterGroup` with `And()` / `Or()` builders for nested boolean groups (up to 5 levels)
- Compiled predicate closures (compile once, evaluate N times)
- `SQLAlchemyFilterBackend` for SQL WHERE clause generation
- `OperatorRegistry` for extensible operator lookup

#### Search
- `SearchSpec` with `weights`, `fuzzy`, `threshold`, `min_length`, `max_results`
- `FuzzyMode.EXACT`, `FuzzyMode.FUZZY` (partial_ratio), `FuzzyMode.TOKEN_SORT` (token_sort_ratio)
- `SearchFieldMode.EXACT`, `PREFIX`, `CONTAINS`
- Unicode normalization with accent removal
- `SQLAlchemySearchBackend` for SQL LIKE/ILIKE search

#### Sorting
- `SortSpec` with `direction` and `nulls` (NullsPosition.FIRST / LAST)
- Multi-key stable sorting
- `SQLAlchemySortBackend` for SQL ORDER BY

#### FastAPI Integration
- `OffsetDep`, `CursorDep` (Annotated dependency types)
- `FilterDep` with `FilterField()` for declarative filters
- `SortDep` for `?sort=name,-age` query parsing
- `SearchDep` for `?q=alice&search_fields=name,email` query parsing

#### Performance
- msgspec fast page construction (`pypaginate[fast]`)
- Compiled field accessors, pre-normalized search tokens
- `__slots__` on all stateful classes
- Optional google-re2 for ReDoS safety (`pypaginate[security]`)
- LIKE pattern string method dispatch (bypasses fnmatch/regex for common patterns)

### Changed
- Renamed `PageParams` to `OffsetParams`, `Page` to `OffsetPage`
- Replaced `paginate_entities()` / `paginate_rows()` with universal `paginate()`
- Replaced JSON Logic dict filters with typed `FilterSpec` / `FilterGroup`
- Replaced `SearchOptions` with `SearchSpec`
- Moved `FilterEngine` to `pypaginate.filtering.engine`
- Moved `SortEngine` to `pypaginate.sorting.engine`
- FastAPI deps use `Annotated` types instead of function-based `Depends`

### Removed
- `SqlPaginator`, `MemoryPaginator` (replaced by protocol backends)
- `PaginationSnapshot` (direct page return)
- `MemorySearchService`, `SqlSearchService` (replaced by `SearchEngine` + backends)
- `SqlSortAdapter`, `SqlFilterAdapter` (replaced by SA backends)
- `get_pagination_params()`, `PagedResponse` (replaced by `OffsetDep`, `OffsetPage`)
- JSON Logic dict format (replaced by typed `FilterGroup`)
- JMESPath array access (replaced by dot notation)

---

## [0.1.0] - 2025-01-30

### Added

#### Core Pagination
- `Page[T]` generic response model with metadata (total, page, limit, pages)
- `PageParams` dataclass for pagination parameters
- Offset-based pagination with configurable page size
- Keyset (cursor-based) pagination for large datasets using `sqlakeyset`

#### Pagination Engines
- `SqlPaginator` - SQLAlchemy-based pagination engine
- `MemoryPaginator` - In-memory pagination for Python collections
- `paginate_entities()` - High-level async pagination API

#### Filtering
- `FilterEngine` with JSON Logic support for complex queries
- Predicate-based filtering system
- Support for operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `like`, `ilike`, `is_null`, `startswith`, `endswith`
- Logical operators: `and`, `or`, `not`

#### Search
- `SqlSearchService` for full-text search
- Fuzzy matching with RapidFuzz integration
- Configurable similarity thresholds
- Accent-insensitive search option
- Multi-field search support

#### Sorting
- `SortEngine` for sort operations
- `SqlSortAdapter` for SQLAlchemy integration
- Multi-column sorting support
- Ascending/descending order

#### FastAPI Integration
- `get_pagination_params()` dependency for FastAPI
- `PagedResponse` Pydantic model for OpenAPI documentation
- Type-safe parameter extraction from query strings

#### Developer Experience
- Full type hints with mypy --strict compatibility
- Comprehensive docstrings
- Async/await support throughout

### Technical Details
- Python 3.11+ required
- SQLAlchemy 2.0+ for database operations
- Pydantic v2 for data validation
- Optional RapidFuzz for fuzzy search

---

## Future Releases

See the [Roadmap](https://pypaginate.readthedocs.io/contributing/roadmap/) for detailed planning of future versions.

[Unreleased]: https://github.com/CybLow/paginate/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/CybLow/paginate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CybLow/paginate/releases/tag/v0.1.0
