# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [0.2.0] - 2025-03-17

### Architecture

- **Hexagonal architecture** -- domain layer (pure types), engine layer (orchestration),
  adapter layer (backend implementations). Dependencies always point inward.
- **Protocol-based backends** -- six `@runtime_checkable` protocols in `domain/protocols.py`:
  `PaginationBackend`, `SyncPaginationBackend`, `CursorBackend`, `FilterBackend`,
  `SortBackend`, `SearchBackend`. Any object satisfying the protocol works as a backend.
- **Separate page types** -- `OffsetPage[T]` and `CursorPage[T]` as Pydantic models with
  no null leakage (offset fields only on OffsetPage, cursor fields only on CursorPage).
- **Elysia-style type inference** -- `paginate()` return type determined by params type
  (`OffsetParams` -> `OffsetPage`, `CursorParams` -> `CursorPage`).
- **Compile-once engines** -- `FilterEngine` and `SearchEngine` compile specs to closures
  once, then evaluate per item without per-item overhead.

### Added

#### Universal `paginate()` Entry Point
- Single `paginate(source, params, *, backend, overflow)` function with type overloads.
- Auto-detects sync vs async backends via coroutine introspection (cached per class).
- Fast path for in-memory lists: direct slice, no backend allocation.
- `OverflowStrategy.CLAMP` and `OverflowStrategy.EMPTY` for out-of-range pages.

#### Domain Types (Pydantic v2 Models)
- `OffsetParams` -- page + limit with `offset` computed field and `clamp(total)` method.
- `CursorParams` -- limit + after/before with mutual exclusivity validation.
- `OffsetPage[T]` -- items, total, page, pages, limit, has_next, has_previous.
- `CursorPage[T]` -- items, limit, has_next, has_previous, next_cursor, previous_cursor.
- `FilterSpec` -- field, operator (Literal type with 20 operators), value, logic.
- `SortSpec` -- field, direction (SortDirection enum), nulls (NullsPosition enum).
- `SearchSpec` -- query, fields, weights, mode, fuzzy, threshold, min_length, max_results.
- `FilterGroup` with `And()` / `Or()` builder functions for nested boolean expressions
  (validated to max 5 levels deep).
- Six enums: `SortDirection`, `NullsPosition`, `FilterLogic`, `SearchFieldMode`,
  `FuzzyMode`, `OverflowStrategy`.

#### Filter System
- 20 operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `contains`,
  `starts_with`, `ends_with`, `like`, `ilike`, `between`, `is_null`, `is_not_null`,
  `regex`, `empty`, `not_empty`, `exists`.
- `FilterEngine` compiles specs to predicate closures (flat lists or nested groups).
- `OperatorRegistry` for name-to-operator mapping (extensible).
- Nested field access via compiled accessors (`"address.city"`).
- `like`/`ilike` optimized: classified as contains/startswith/endswith when possible,
  falls back to glob matching.
- Regex compilation with optional google-re2 backend (`pypaginate[security]`).

#### Search System
- `SearchEngine` with tokenized queries, Unicode normalization, and relevance scoring.
- Three fuzzy modes: `EXACT`, `FUZZY` (partial_ratio), `TOKEN_SORT` (token_sort_ratio).
- Weighted multi-field search with configurable threshold (0-100).
- Optimized single-field fast path (no per-item list allocation).
- Falls back to substring matching when rapidfuzz is not installed.

#### SQLAlchemy Backends
- `SQLAlchemyBackend` (async) and `SyncSQLAlchemyBackend` (sync) for offset pagination.
- `SQLAlchemyCursorBackend` and `SyncSQLAlchemyCursorBackend` for keyset pagination
  via sqlakeyset.
- `SQLAlchemyFilterBackend` -- translates FilterSpec to SQLAlchemy WHERE clauses.
- `SQLAlchemySortBackend` -- translates SortSpec to ORDER BY clauses.
- `SQLAlchemySearchBackend` -- translates SearchSpec to LIKE/ILIKE conditions.
- Custom count query support on pagination backends (`count_query` parameter).
- Row deduplication support (`unique=True` parameter).

#### Pipeline
- `SyncPipeline` and `AsyncPipeline` compose filter -> sort -> search -> paginate.
- Auto-converts FastAPI dependency objects (`FilterDep`, `SortDep`, `SearchDep`)
  via `to_specs()` / `to_spec()` protocol detection.

#### FastAPI Integration
- `OffsetDep` / `CursorDep` -- `Annotated` types for pagination dependency injection.
- `FilterDep` / `FilterField` -- declarative filter dependencies from query params.
- `SortDep` -- sorting dependency from query params.
- `SearchDep` -- search dependency from query params.

#### Performance
- `pypaginate[fast]` extra: msgspec-based `FastOffsetPage` / `FastCursorPage` with
  near-zero construction overhead and `.model_dump()` / `.to_pydantic()` compatibility.
- `__slots__` on all engine classes.
- Async detection cached per backend class.

#### Exception Hierarchy
- `PaginationError` base with structured `details` dicts.
- `ConfigurationError`, `ValidationError`, `FilterError`, `FilterValidationError`,
  `SearchError`, `SearchQueryError`, `SortError`.

### Changed (vs v0.1.0)
- **Page is now a Pydantic model** -- eliminates the separate `PagedResponse` wrapper.
- **Two page types** instead of one `Page[T]` -- `OffsetPage` and `CursorPage`.
- **Params renamed** -- `PageParams` -> `OffsetParams`, `KeysetPageParams` -> `CursorParams`.
- **Module restructure** -- flat `engines/`, `filters/`, `sorting/` replaced by
  `domain/`, `engine/`, `filtering/`, `search/`, `sorting/`, `adapters/`.
- **Exception names** -- `PaginatorException` -> `PaginationError`,
  `FilterException` -> `FilterError`, etc.
- **Public API** -- old functions (`paginate_entities`, `paginate_rows`) replaced by
  universal `paginate()`.

---

## [0.1.0] - 2025-01-30

### Added

#### Core Pagination
- `Page[T]` generic response model (frozen dataclass) with metadata.
- `PageParams` dataclass for pagination parameters.
- Offset-based pagination with configurable page size.
- Keyset (cursor-based) pagination via sqlakeyset.

#### Pagination Engines
- `SqlPaginator` -- SQLAlchemy-based pagination engine.
- `MemoryPaginator` -- in-memory pagination for Python collections.
- `paginate_entities()` -- high-level async pagination API.

#### Filtering
- `FilterEngine` with JSON Logic support for complex queries.
- Predicate-based filtering system with 24 operators.
- `SqlFilterAdapter` for SQL WHERE clause generation.

#### Search
- `SqlSearchService` for full-text search.
- Fuzzy matching with RapidFuzz integration.
- Multi-field search support.

#### Sorting
- `SortEngine` for sort operations.
- `SqlSortAdapter` for SQLAlchemy integration.

#### FastAPI Integration
- `get_pagination_params()` dependency.
- `PagedResponse` Pydantic model for OpenAPI documentation.

### Technical Details
- Python 3.11+ required.
- SQLAlchemy 2.0+ for database operations.
- Pydantic v2 for data validation.
- Optional RapidFuzz for fuzzy search.

---

[Unreleased]: https://github.com/CybLow/pypaginate/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/CybLow/pypaginate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CybLow/pypaginate/releases/tag/v0.1.0
