# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Performance
- **Row-engine sort is ~3× faster** via decorate-sort-undecorate — each item's
  sort key is resolved once instead of on every comparison (100k rows, release:
  `single_int` 25.4→7.7 ms, `multi_int` 28.7→9.7 ms, the row pipeline 21.3→9.0 ms).
- **Text-heavy search faster** — `normalize_text` (run per item per field in
  every search / contains-filter) folds the ASCII fast path into a single
  allocation. `search/contains` 5.6→3.6 ms (−36%); combined with the
  alloc-free rapidfuzz `partial_ratio` (now scoring on char slices, no
  per-window `String`), `search/fuzzy_multi` drops 117.9→76.6 ms (−35%) at 100k.
  Output is byte-identical (guarded by the parity suites).

### Added
- **Cross-language parity harness.** A frozen golden (`tests/fixtures/parity.json`)
  asserts the Rust core, the Python binding, and the Node/TS binding produce
  byte-identical cursors and identical filter/sort/search indices — wired into
  the CI `parity` job so the wire format and engine semantics cannot drift.
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
- **Fuzzy / token-sort search now runs in the core** (rapidfuzz-based
  `partial_ratio` / `token_sort_ratio` in Rust), replacing the pure-Python
  search island — which also fixes the prior rapidfuzz-version-dependent score
  flakiness. Boolean fields now take the columnar fast path (~8× on
  bool-inclusive filters).

### Removed
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
