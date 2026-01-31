# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.2.0
- FilterModel and FilterDepends for declarative filtering
- Auto SQL WHERE clause generation
- Relationship filters with auto-join
- OrderingDepends for sorting
- Pydantic validation for filters

### Planned for v0.3.0
- Alternative pagination formats (LimitOffsetPage, CursorPage)
- HATEOAS link generation
- Custom response models and customizers

### Planned for v0.4.0
- Advanced SQL operators (between, array_contains, overlap, jsonb_path)
- Count query caching
- Additional ORM support (Django, Tortoise)

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

See the [Roadmap](contributing/roadmap.md) for detailed planning of future versions.

[Unreleased]: https://github.com/CybLow/pypaginate/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/CybLow/pypaginate/releases/tag/v0.1.0
