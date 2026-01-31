# Roadmap

This roadmap outlines the planned development of pypaginate towards feature parity with existing pagination libraries.

**Current Version:** 0.1.0  
**Goal:** Cover 100% of fastapi-pagination and fastapi-filters functionality

## Version Overview

| Version | Focus | Target |
|---------|-------|--------|
| v0.2.0 | Declarative FastAPI Integration | Q1 2025 |
| v0.3.0 | Multiple Pagination Formats | Q1 2025 |
| v0.4.0 | Optimizations & Relations | Q2 2025 |
| v1.0.0 | Production Ready | Q2 2025 |

## v0.2.0 - Declarative FastAPI Integration

**Status:** In Development  
**Focus:** Declarative filtering and dependencies

### Goals

- Achieve parity with fastapi-filters for FastAPI integration
- Make pypaginate production-ready for 80% of use cases
- Drastically simplify user code

### Planned Features

#### 1. FilterModel + FilterDepends

```python
class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator='ilike')
    age: int | None = FilterField(None, operator='gte')
    
    class Config:
        model = User

@app.get("/users")
async def list_users(
    filters: UserFilter = FilterDepends(UserFilter),
):
    stmt = select(User).where(*filters.to_sql_conditions())
```

#### 2. Auto SQL WHERE Generation

```python
stmt = select(User).where(*filters.to_sql_conditions())
# Automatically builds WHERE clauses from filter model
```

#### 3. Relations with Auto-Join

```python
class UserFilter(FilterModel):
    posts__title: str | None = None  # Auto-JOIN
```

#### 4. OrderingDepends

```python
ordering: OrderingParams = OrderingDepends(['name', 'created_at'])
stmt = stmt.order_by(*ordering.to_sql_order_by(User))
```

### Expected Impact

- **Code Reduction:** ~35 lines → ~15 lines per endpoint
- **Maintainability:** +300%
- **Auto-documentation:** OpenAPI schema generation

## v0.3.0 - Multiple Pagination Formats

**Focus:** Flexibility and compatibility

### Planned Features

#### 1. Alternative Page Formats

```python
from pypaginator.core import LimitOffsetPage, CursorPage, PageWithLinks

# Limit/Offset style
page: LimitOffsetPage[User]  # items, total, limit, offset

# Cursor-based
page: CursorPage[User]  # items, next_cursor, prev_cursor

# With HATEOAS links
page: PageWithLinks[User]  # items, total, links
```

#### 2. PageParams Factory

```python
from pypaginator.core import PageParamsFactory

# Custom parameter names
get_params = PageParamsFactory(
    page_name='offset',
    limit_name='count',
    max_limit=50,
).create()
```

#### 3. Link Generator

```python
from pypaginator.core import LinkGenerator

generator = LinkGenerator(base_url='/api/users')
links = generator.generate(page=2, limit=20, total=100)
# links.next = '/api/users?page=3&limit=20'
```

## v0.4.0 - Optimizations & Relations

**Focus:** Performance and advanced features

### Planned Features

#### 1. Count Query Caching

```python
# Cache count results for improved performance
paginator = SqlPaginator(session, count_cache_ttl=60)
```

#### 2. Advanced SQL Operators

```python
filters = {
    "price": {"between": [10, 100]},
    "tags": {"array_contains": "python"},
    "metadata": {"jsonb_path": "$.author.name"},
}
```

#### 3. Complex Relations

- Many-to-many support
- Polymorphic relations
- Self-referential relations

### Performance Goals

- Count queries: 10x faster (with cache)
- Optimized relations: 3x faster

## v1.0.0 - Production Ready

**Focus:** Stability and documentation

### Goals

- >95% test coverage
- Complete documentation
- API stability guarantee
- Security audit
- Performance benchmarks

### Checklist

- [ ] All major features implemented
- [ ] Comprehensive test suite
- [ ] Complete API documentation
- [ ] Migration guides from v0.x
- [ ] Real-world examples
- [ ] Performance profiling

## Current Strengths

pypaginate already excels in:

- **Architecture**: Clean, layered design
- **Type Safety**: Full mypy --strict compatibility
- **Advanced Search**: Fuzzy matching with RapidFuzz
- **JSON Logic**: Flexible filter expressions

## Feature Comparison

| Feature | fastapi-pagination | fastapi-filters | pypaginate |
|---------|-------------------|-----------------|------------|
| Offset pagination | Yes | - | Yes |
| Cursor pagination | Yes | - | Partial |
| FilterDepends | - | Yes | Planned v0.2 |
| Auto-joins | - | Yes | Planned v0.2 |
| Fuzzy search | - | No | **Yes** |
| JSON Logic | - | No | **Yes** |
| Type safety | Partial | Partial | **Strict** |

## Contributing

We welcome contributions! Priority areas:

1. **v0.2.0**: FilterModel and FilterDepends
2. **Testing**: Integration tests for FastAPI
3. **Documentation**: Examples and tutorials

See [Contributing Guide](index.md) to get started.

## Timeline

```
2025 Q1
├── Week 1-2:   FilterModel + FilterField
├── Week 3-4:   SqlFilterAdapter + Relations
├── Week 5-6:   OrderingDepends
├── Week 7-8:   Tests + Documentation
└── Release v0.2.0

2025 Q1-Q2
├── Week 9-10:  Alternative formats
├── Week 11-12: Links + Customizers
└── Release v0.3.0

2025 Q2
├── Week 13-16: Optimizations
├── Week 17-18: Complex relations
└── Release v0.4.0

2025 Q2
├── Week 19-20: Stabilization
├── Week 21-22: Final documentation
└── Release v1.0.0
```
