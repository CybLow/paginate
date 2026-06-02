# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
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

[Unreleased]: https://github.com/CybLow/pypaginate/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/CybLow/pypaginate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CybLow/pypaginate/releases/tag/v0.1.0
