# Roadmap

Development plan for pypaginate -- from v0.2.0 forward.

**Current version:** 0.2.0
**Goal:** Universal pagination + filtering + search library with clean architecture,
full type safety, and production-grade reliability.

## Release Overview

| Version | Focus | Status |
|---------|-------|--------|
| **v0.2.0** | Architecture rewrite, universal `paginate()` | **RELEASED** |
| **v0.3.0** | Extensibility and framework adapters | PLANNED |
| **v1.0.0** | API stability and production hardening | FUTURE |

---

## v0.2.0 -- Architecture Rewrite (RELEASED)

Complete rewrite from v0.1.0 with hexagonal architecture.

### What Was Done

- **Universal `paginate()` function** -- one function for lists, SQLAlchemy (async/sync),
  and cursor-based pagination. Return type inferred from params
  (`OffsetParams` -> `OffsetPage`, `CursorParams` -> `CursorPage`).
- **Hexagonal architecture** -- domain layer (pure types), engine layer (orchestration),
  adapter layer (backend implementations). Dependencies always point inward.
- **Protocol-based backends** -- six `@runtime_checkable` protocols: `PaginationBackend`,
  `SyncPaginationBackend`, `CursorBackend`, `FilterBackend`, `SortBackend`, `SearchBackend`.
- **Pydantic v2 page models** -- `OffsetPage[T]` and `CursorPage[T]` replace the old
  `Page[T]` dataclass and `PagedResponse[T]` wrapper.
- **20 filter operators** -- eq, ne, gt, gte, lt, lte, in, not_in, contains, starts_with,
  ends_with, like, ilike, between, is_null, is_not_null, regex, empty, not_empty, exists.
- **Nested filter groups** -- `And()` / `Or()` builders for boolean expressions
  (validated to max 5 levels deep).
- **Weighted search** -- `SearchSpec(weights={"name": 2.0, "bio": 0.5})` for
  per-field relevance scoring.
- **Three fuzzy modes** -- `FuzzyMode.EXACT`, `FuzzyMode.FUZZY` (partial_ratio),
  `FuzzyMode.TOKEN_SORT` (token_sort_ratio).
- **Search safety** -- `min_length` and `max_results` on SearchSpec.
- **Custom count queries** -- SA backends accept `count_query` parameter.
- **Row deduplication** -- SA backends accept `unique=True` for eager-loaded relations.
- **FastAPI dependencies** -- `OffsetDep`, `CursorDep`, `FilterDep`, `SortDep`, `SearchDep`
  as `Annotated` types.
- **Pipeline** -- `SyncPipeline` and `AsyncPipeline` compose
  filter -> sort -> search -> paginate.
- **msgspec fast path** -- `pypaginate[fast]` extra for near-zero serialization overhead.

---

## v0.3.0 -- Extensibility and Framework Adapters (PLANNED)

**Focus:** Items transformer, optional total count, additional framework adapters,
and PostgreSQL full-text search.

### Items Transformer

Post-pagination item transformation pipeline:

```python
page = await paginate(
    stmt, params, backend=backend,
    transformer=lambda items: [UserSchema.from_orm(u) for u in items],
)
```

### Optional Total Count

Skip the COUNT query for faster pagination when total is not needed:

```python
page = await paginate(stmt, params, backend=backend, include_total=False)
# page.total is None, but page.items and page.has_next still work
```

### Django and Flask Adapters

Backend adapters for Django ORM and Flask-SQLAlchemy, following the same
protocol-based architecture as the SQLAlchemy adapters.

### PostgreSQL Full-Text Search

Native PostgreSQL `tsvector`/`tsquery` search backend for production-grade
full-text search with ranking, stemming, and language support.

### Other Planned Items

- JSON Logic parser (dict -> FilterSpec) for frontend integration
- Django `__` filter format parser for Django developer DX
- HATEOAS links (`PageWithLinks[T]` with RFC 8288 headers)
- `add_pagination(app)` auto-setup for FastAPI

### Checklist

- [ ] Items transformer pipeline
- [ ] Optional total count (skip COUNT query)
- [ ] Django ORM backend adapter
- [ ] Flask-SQLAlchemy backend adapter
- [ ] PostgreSQL full-text search backend
- [ ] JSON Logic parser (optional convenience layer)
- [ ] Django `__` filter format parser
- [ ] HATEOAS links and PageWithLinks
- [ ] Documentation and migration guide

---

## v1.0.0 -- API Stability and Production Hardening (FUTURE)

**Focus:** Stable API guarantee, full test coverage, and production confidence.

### API Stability Guarantee

No breaking changes after v1.0.0. Deprecation cycle for any future changes:
warn in 1.x, remove in 2.0.

### Quality Gates

| Gate | Target |
|------|--------|
| Test coverage | >95% |
| All public APIs documented | 100% |
| Security audit (bandit) | Zero high/critical |
| Performance benchmarks | Published baselines |
| Type coverage (mypy strict) | 100% |

### Documentation

- Complete API reference
- Getting started tutorial
- Migration guides (from fastapi-pagination, fastapi-filter)
- Cookbook with real-world examples
- Architecture guide for contributors

### Checklist

- [ ] API frozen (no breaking changes)
- [ ] >95% test coverage
- [ ] Complete documentation
- [ ] Security audit passed
- [ ] Performance benchmarks published
- [ ] Migration guides written
- [ ] Real-world examples for common patterns

---

## Contributing

Priority areas for contributions:

1. **Items transformer** -- implement the post-pagination transformation hook
2. **Optional total count** -- add `include_total` flag to skip COUNT queries
3. **Django adapter** -- implement `DjangoBackend` following SA adapter patterns
4. **PostgreSQL FTS** -- native tsvector/tsquery search backend
5. **Test coverage** -- increase coverage toward the 95% target

See the [Contributing Guide](index.md) to get started.
