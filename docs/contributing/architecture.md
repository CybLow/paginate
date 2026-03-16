# Architecture Guide

> How pypaginate is structured and why.

---

## Directory Structure

```
src/pypaginate/
├── __init__.py          # Public API (23 exports)
├── _dispatch.py         # Universal paginate() — type overloads + auto-detection
│
├── domain/              # Pure domain — Pydantic models + protocols
│   ├── enums.py         # SortDirection, FilterLogic, FuzzyMode, etc.
│   ├── exceptions.py    # PaginationError hierarchy
│   ├── models.py        # Re-export hub
│   ├── pages.py         # OffsetPage, CursorPage
│   ├── fast_pages.py    # msgspec.Struct pages (optional acceleration)
│   ├── params.py        # OffsetParams, CursorParams
│   ├── protocols.py     # Backend protocol definitions
│   └── specs.py         # FilterSpec, SortSpec, SearchSpec
│
├── engine/              # Core orchestration (backend-agnostic)
│   ├── paginator.py     # Paginator, AsyncPaginator
│   ├── pipeline.py      # SyncPipeline, AsyncPipeline
│   └── cursor.py        # AsyncCursorPaginator
│
├── filtering/           # Filter engine + 17 operators
│   ├── accessor.py      # compile_accessor() — field path resolution
│   ├── engine.py        # FilterEngine (compiled predicates)
│   ├── operators.py     # Eq, Gt, Like, Regex, Between, etc.
│   ├── registry.py      # OperatorRegistry + create_default_registry()
│   ├── like.py          # LIKE pattern classification (string methods)
│   └── regex.py         # Optional google-re2 wrapper
│
├── sorting/             # Sort engine
│   ├── engine.py        # SortEngine (stable multi-key)
│   └── keys.py          # build_sort_key() with null handling
│
├── search/              # Search engine
│   ├── engine.py        # SearchEngine (token-based relevance)
│   ├── matching.py      # matches_field(), fuzzy_score()
│   └── parser.py        # TokenParser (shlex-based)
│
├── text/                # Text utilities
│   └── normalize.py     # normalize_text() — LRU cached + ASCII fast path
│
└── adapters/            # Backend implementations
    ├── memory/          # In-memory (list, tuple)
    ├── sqlalchemy/      # SQLAlchemy ORM (sync + async)
    └── fastapi/         # FastAPI dependency injection
```

---

## Layer Rules

| Layer | Depends On | Never Depends On |
|---|---|---|
| **Domain** | Pydantic only | Engine, Adapters, Text |
| **Engine** | Domain | Adapters |
| **Filtering/Sorting/Search** | Domain, Text | Adapters |
| **Adapters** | Domain, Filtering, Sorting, Search | Engine (via protocols) |
| **Dispatch** | Domain, Engine, Adapters | — |

**Enforced by** `tests/architecture/test_imports.py`.

---

## Key Design Patterns

### Protocol-Based Backends (Dependency Inversion)

Backends implement protocols, not base classes. The engine layer depends on abstractions:

```python
# domain/protocols.py
class PaginationBackend(Protocol[T]):
    async def count(self, query: object) -> int: ...
    async def fetch(self, query: object, offset: int, limit: int) -> list[T]: ...
```

Any class with matching methods satisfies the protocol — no inheritance required.

### Compile-Once, Apply-N (Strategy Pattern)

Specs are compiled into closures ONCE, then applied to every item:

```python
# Accessor: split path once, reuse closure
accessor = compile_accessor("user.profile.email")  # O(1)
for item in items:
    value = accessor(item)  # O(1) per call, no string split

# Filter: compile predicate once
predicate = _compile_predicate(FilterSpec(field="age", operator="gte", value=30), registry)
results = [item for item in items if predicate(item)]
```

### Partition-Sort (Null Handling)

Instead of wrapping every sort key in a `(is_null, value)` tuple, the memory sort backend partitions items into nulls and non-nulls, sorts non-nulls directly, then concatenates:

```python
nulls, non_nulls = _partition_nulls(items, accessor)
non_nulls.sort(key=lambda item: accessor(item))
return _join_partitions(nulls, non_nulls, null_position)
```

### Optional Acceleration (Strategy + Feature Flag)

Optional dependencies follow the try/except pattern:

```python
try:
    from rapidfuzz import fuzz as _fuzz
    _HAS_RAPIDFUZZ = True
except ImportError:
    _HAS_RAPIDFUZZ = False
```

Used for: `rapidfuzz` (search), `msgspec` (page construction), `google-re2` (regex safety).

---

## Adding a New Feature

1. **Read** existing code in the target module
2. **Check** similar implementations for patterns
3. **Keep** functions ≤ 12 lines, files ≤ 200 lines
4. **Add** `__slots__` to any new class with instance attributes
5. **Write** tests in the matching `tests/unit/` directory
6. **Run** `uv run ruff check src/ && uv run mypy src/ && uv run pytest tests/ --ignore=tests/perf -q`
