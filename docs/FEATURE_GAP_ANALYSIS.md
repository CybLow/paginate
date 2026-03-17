# Feature Gap Analysis — v0.1 Documentation vs v0.2 Code

> Complete inventory of features documented in v0.1 that are missing, changed,
> or intentionally removed in v0.2. Each gap is analyzed for whether it should
> be re-implemented, redesigned, or permanently dropped.

---

## Summary

| Category | Present | Improved | Removed (design) | Missing (gaps) |
|---|---|---|---|---|
| Pagination | 7 | 6 | 7 | 2 |
| Filtering | 5 | 2 | 2 | 6 |
| Search | 4 | 2 | 3 | 6 |
| Sorting | 4 | 2 | 2 | 1 |
| FastAPI | 2 | 1 | 2 | 5 |
| SQLAlchemy | 3 | 0 | 0 | 2 |
| **Total** | **25** | **13** | **16** | **22** |

---

## PAGINATION GAPS

### GAP P1: Custom Count Query -- IMPLEMENTED in v0.2.0

- **v0.1**: `paginate_entities(session, stmt, params, count_statement=custom_count)`
- **v0.2**: `paginate(stmt, params, backend=SQLAlchemyBackend(session, count_query=custom))`
- **Status**: **IMPLEMENTED** in v0.2.0. SA backends accept a `count_query` parameter.

### GAP P2: Deduplication (unique=True) -- IMPLEMENTED in v0.2.0

- **v0.1**: `paginate_entities(session, stmt, params, unique=True)`
- **v0.2**: `paginate(stmt, params, backend=SQLAlchemyBackend(session, unique=True))`
- **Status**: **IMPLEMENTED** in v0.2.0. SA backends accept a `unique` parameter for row deduplication.

---

## FILTERING GAPS

### GAP F1: Missing Operators — empty, not_empty, exists -- IMPLEMENTED in v0.2.0

- **v0.1**: `empty` (checks `None`, `""`, `[]`), `not_empty`, `exists` (field present)
- **v0.2**: `empty`, `not_empty`, `exists` operators registered in `OperatorRegistry`
- **Status**: **IMPLEMENTED** in v0.2.0. All three operators are available.

### GAP F2: Operator Aliases (==, !=, >, >=, <, <=)

- **v0.1**: `eq` aliased as `==` and `equals`, etc.
- **v0.2**: Only primary names (`eq`, `ne`, `gt`, etc.)
- **Impact**: Low. DX convenience for users who prefer symbol syntax.
- **Verdict**: **SKIP** — aliases add confusion about canonical name. One name per operator is clearer.

### GAP F3: Array Operators (any, all)

- **v0.1**: `any` (array contains any of values), `all` (array contains all)
- **v0.2**: Not available
- **Impact**: Low. Niche use case for array-typed fields.
- **Verdict**: **SKIP for v0.2** — consider for v0.3 if users request it

### GAP F4: JSON Logic Evaluation -- PARTIALLY ADDRESSED in v0.2.0

- **v0.1**: Full JSON Logic with `{"and": [{"or": [...]}]}` nested expressions
- **v0.2**: `FilterGroup` with `And()` / `Or()` builders support nested groups up to 5 levels deep.
  Flat `FilterSpec` lists still use AND/OR logic enum for simple cases.
- **Status**: Nested group expressions like `(a OR b) AND (c OR d)` are now possible via
  `And(Or(...), Or(...))`. JSON Logic dict format is not supported -- users use typed builders instead.
- **Verdict**: **CONSIDER for v0.3** -- add optional JSON Logic parser that converts dicts to FilterGroup.
  FilterGroup is the primary API (type-safe, compiled predicates).

### GAP F5: Array Field Access (JMESPath `[*]` notation)

- **v0.1**: `"orders[*].quantity"` for accessing nested arrays
- **v0.2**: Only dot notation (`"profile.address.city"`)
- **Dot notation explained**:
  ```python
  compile_accessor("profile.address.city")
  # Traverses: item → item["profile"] → ["address"] → ["city"]
  # Works for dicts AND objects (getattr fallback)
  ```
- **What JMESPath added**: array indexing (`people[0]`), array filtering (`items[?price>100]`), wildcards (`*.name`)
- **Impact**: Low. 99% of real use cases use dot notation. Array access is niche.
- **Verdict**: **SKIP** — removed by design. Users can pre-process arrays before passing to pypaginate.

### GAP F6: Dict-Style Filter Format (`{"field__op": value}`)

- **v0.1**: `{"name__ilike": "%john%", "age__gte": 18}` Django-style
- **v0.2**: `FilterSpec(field="name", operator="ilike", value="%john%")`
- **Impact**: DX convenience for Django developers
- **Verdict**: **CONSIDER for v0.3** — could add a `parse_django_filters()` utility

---

## SEARCH GAPS

### GAP S1: Weighted Field Search -- IMPLEMENTED in v0.2.0

- **v0.1**: `SearchOptions(fields={"name": 2.0, "bio": 0.5})`
- **v0.2**: `SearchSpec(fields=("name", "bio"), weights={"name": 2.0, "bio": 0.5})`
- **Status**: **IMPLEMENTED** in v0.2.0. SearchSpec accepts a `weights` dict for per-field scoring.

### GAP S2: Token Sort Ratio (fuzzy matching mode) -- IMPLEMENTED in v0.2.0

- **v0.1**: Configurable fuzzy strategy (ratio, partial_ratio, token_sort_ratio)
- **v0.2**: `FuzzyMode.FUZZY` (partial_ratio), `FuzzyMode.TOKEN_SORT` (token_sort_ratio)
- **Status**: **IMPLEMENTED** in v0.2.0. FuzzyMode enum includes TOKEN_SORT.

### GAP S3: min_query_length -- IMPLEMENTED in v0.2.0

- **v0.1**: `SearchOptions(min_query_length=2)` — reject short queries
- **v0.2**: `SearchSpec(query="a", min_length=2)` — rejects queries shorter than min_length
- **Status**: **IMPLEMENTED** in v0.2.0. SearchSpec accepts `min_length` parameter.

### GAP S4: max_results Limit -- IMPLEMENTED in v0.2.0

- **v0.1**: `SearchOptions(max_results=100)` — cap results
- **v0.2**: `SearchSpec(query="alice", max_results=100)` — caps ranked results
- **Status**: **IMPLEMENTED** in v0.2.0. SearchSpec accepts `max_results` parameter.

### GAP S5: TF-IDF Scoring

- **v0.1 docs**: Mention TF-IDF (term frequency-inverse document frequency)
- **v0.2**: Simple token-based scoring (100 if match, 0 if not)
- **Impact**: Low. TF-IDF is overkill for in-memory search on <100K items.
- **Verdict**: **SKIP** — our scoring is sufficient. TF-IDF adds complexity without practical benefit at our scale.

### GAP S6: Result Highlighting

- **v0.1 docs**: `highlight_tag="<mark>"` for highlighting matching text
- **v0.2**: Not available
- **Impact**: Low. This is a UI concern, not a pagination library concern.
- **Verdict**: **SKIP** — users handle highlighting in their frontend/templates

---

## SORTING GAPS

### GAP T1: Tie-Breaker Field

- **v0.1**: `sort_items(users, sort_field="age", tie_breaker_field="id")`
- **v0.2**: User adds secondary SortSpec manually:
  ```python
  SortEngine.apply(items, [
      SortSpec(field="age"),
      SortSpec(field="id"),  # tie-breaker
  ])
  ```
- **Impact**: None. v0.2 approach is MORE flexible (any number of sort keys).
- **Verdict**: **SKIP** — v0.2 is better. Document the pattern instead.

---

## FASTAPI GAPS

### GAP FA1: get_pagination_params()

- **v0.1**: `params = Depends(get_pagination_params)` — function dependency
- **v0.2**: `params: OffsetDep` — Annotated type alias
- **Impact**: None. v0.2 uses modern FastAPI Annotated pattern (better DX).
- **Verdict**: **SKIP** — v0.2 is better

### GAP FA2: PagedResponse[T]

- **v0.1**: `@app.get("/users", response_model=PagedResponse[UserSchema])`
- **v0.2**: Return `result.model_dump()` or use `OffsetPage` as response model
- **Impact**: Low. OffsetPage IS the response model.
- **Verdict**: **SKIP** — OffsetPage serves this purpose

### GAP FA3: FilterDepends / OrderingDepends / SearchDepends -- IMPLEMENTED in v0.2.0

- **v0.1 docs**: Planned declarative filter/ordering/search dependencies
- **v0.2**: `FilterDep`, `SortDep`, `SearchDep` implemented in `pypaginate.adapters.fastapi`
- **Status**: **IMPLEMENTED** in v0.2.0. `FilterDep` uses `FilterField()` for declarative filters.
  `SortDep` parses `?sort=name,-age`. `SearchDep` parses `?q=alice&search_fields=name,email`.

### GAP FA4: add_pagination(app)

- **v0.1 docs**: Auto-setup middleware
- **v0.2**: Not implemented — explicit setup required
- **Impact**: Medium. fastapi-pagination has this.
- **Verdict**: **CONSIDER for v0.3** — requires ContextVar architecture

### GAP FA5: Custom Parameter Names

- **v0.1 docs**: Alias page→skip, limit→take
- **v0.2**: Fixed names (page, limit)
- **Impact**: Low. Users write a 3-line FastAPI dependency.
- **Verdict**: **SKIP** — not worth framework complexity

---

## SQLALCHEMY GAPS

### GAP SA1: Custom Count Query

Same as GAP P1. See Pagination Gaps section.

### GAP SA2: Deduplication

Same as GAP P2. See Pagination Gaps section.

---

## IMPLEMENTATION PRIORITY

### Must Add (Production Blockers) -- ALL IMPLEMENTED in v0.2.0

| # | Feature | Status |
|---|---|---|
| P1 | Custom count query for SA | **IMPLEMENTED** in v0.2.0 |
| P2 | Deduplication (unique) for SA | **IMPLEMENTED** in v0.2.0 |

### Should Add (DX Improvements) -- MOSTLY IMPLEMENTED in v0.2.0

| # | Feature | Status |
|---|---|---|
| S1 | Weighted field search | **IMPLEMENTED** in v0.2.0 |
| S2 | Token sort ratio fuzzy mode | **IMPLEMENTED** in v0.2.0 |
| S3 | min_query_length | **IMPLEMENTED** in v0.2.0 |
| S4 | max_results limit | **IMPLEMENTED** in v0.2.0 |
| F1 | empty/not_empty/exists operators | **IMPLEMENTED** in v0.2.0 |

### Consider for v0.3

| # | Feature | Effort | Impact |
|---|---|---|---|
| F4 | JSON Logic parser (dict → FilterGroup) | High | Medium — frontend integration |
| F6 | Django `__` filter format parser | Medium | Medium — Django developer DX |
| FA4 | add_pagination(app) | High | Medium — zero-config setup |

### Skip Permanently

| # | Feature | Reason |
|---|---|---|
| F2 | Operator aliases (==, !=) | One canonical name is clearer |
| F3 | Array operators (any, all) | Niche, users pre-process arrays |
| F5 | JMESPath array access | Removed by design, dot notation covers 99% |
| S5 | TF-IDF scoring | Overkill for in-memory search |
| S6 | Result highlighting | UI concern, not pagination library |
| T1 | Tie-breaker field | Multi-key SortSpec is more flexible |
| FA1 | get_pagination_params() | OffsetDep (Annotated) is better |
| FA2 | PagedResponse[T] | OffsetPage IS the response model |
| FA5 | Custom parameter names | 3-line user dependency |

---

## What v0.2 Does BETTER Than v0.1

| Area | v0.1 | v0.2 | Winner |
|---|---|---|---|
| **Performance** | ~15ms filter | ~1ms filter | v0.2 (7.6x faster) |
| **Type safety** | Dict-based filters (no mypy) | FilterSpec (full mypy) | v0.2 |
| **Dependencies** | 8 external libs | 1 (pydantic only) | v0.2 |
| **API surface** | 15+ functions/classes | 1 function (paginate) | v0.2 |
| **Sync/async** | Separate functions | Auto-detected | v0.2 |
| **Page construction** | PaginationSnapshot.to_page() | Direct return | v0.2 |
| **FastAPI deps** | Function-based Depends | Annotated types | v0.2 |
| **Architecture** | Monolithic engines | Protocol-based backends | v0.2 |
| **Nested groups** | JSON Logic (unlimited) | And()/Or() nested groups (max 5 deep) | v0.2 (typed) |
| **Array access** | JMESPath (powerful) | Dot notation (simple) | v0.1 for power |
| **Fuzzy modes** | 3+ strategies | EXACT, FUZZY, TOKEN_SORT | v0.2 (typed) |
| **Field weights** | SearchOptions(fields={...}) | SearchSpec(weights={...}) | v0.2 (typed) |

---

## Deep Analysis: Key Design Decisions

### DA1: JSON Logic vs FilterSpec — Complete Comparison

**v0.1 (JSON Logic dict):**
```python
# Complex nested filter with AND/OR
filters = {
    "and": [
        {"age": {"gte": 18}},
        {"or": [
            {"country": {"eq": "FR"}},
            {"country": {"eq": "BE"}},
        ]},
    ],
}
result = engine.filter(items, filters)
```

| Aspect | JSON Logic (v0.1) | FilterSpec (v0.2) |
|---|---|---|
| **Speed** | ~15-30ms / 10K items (dict parsing per item) | ~1ms / 10K items (compiled predicates) |
| **Type safety** | None — plain dict, mypy can't validate | Full — Literal types, IDE autocomplete |
| **Debugging** | Hard — nested dicts, runtime errors only | Easy — each FilterSpec is a clear object |
| **Dependencies** | json-logic-qubit (external lib) | None — Pydantic models only |
| **Serialization** | Native JSON — frontend can send directly | Pydantic model — needs API parsing |
| **Nesting depth** | Unlimited — `(a OR b) AND (c OR d)` works | Up to 5 levels via `And()`/`Or()` `FilterGroup` builders |
| **Dynamic rules** | Yes — rule engines, form builders | Yes — build `FilterGroup` trees programmatically |

**The nesting limitation was addressed in v0.2.0 with `FilterGroup`:**
```python
# v0.2 can now express: (a=1 OR b=2) AND (c=3 OR d=4)
from pypaginate import And, Or, FilterSpec

group = And(
    Or(FilterSpec(field="a", value=1), FilterSpec(field="b", value=2)),
    Or(FilterSpec(field="c", value=3), FilterSpec(field="d", value=4)),
)
```

**Remaining difference:** JSON Logic uses plain dicts (frontend-friendly), while FilterGroup uses
typed Python builders. A JSON Logic dict-to-FilterGroup parser could be added in v0.3 for
frontend integration use cases.

### DA2: Dot Notation vs JMESPath — With Examples

**Dot notation (v0.2)** — simple nested field access:
```python
from pypaginate.filtering.accessor import compile_accessor

user = {
    "name": "Alice",
    "profile": {
        "settings": {"theme": "dark", "language": "en"},
        "address": {"city": "Paris", "country": "France"}
    }
}

compile_accessor("name")(user)                    # → "Alice"
compile_accessor("profile.address")(user)         # → {"city": "Paris", ...}
compile_accessor("profile.settings.theme")(user)  # → "dark"
compile_accessor("profile.address.city")(user)    # → "Paris"
```

**JMESPath (v0.1)** — powerful query language for nested data:
```python
import jmespath

# Array filtering (DOT NOTATION CANNOT DO THIS):
jmespath.search("orders[*].items[?price > 100].name", data)

# Array indexing:
jmespath.search("people[0].name", data)

# Wildcard access:
jmespath.search("*.name", data)  # all top-level fields' .name

# Nested array flattening:
jmespath.search("departments[*].employees[*].name", data)
```

| Aspect | Dot Notation (v0.2) | JMESPath (v0.1) |
|---|---|---|
| **Speed** | ~110ns per call (pre-compiled) | ~1-5us per call (expression parsing) |
| **Dependencies** | None (stdlib only) | jmespath library |
| **Nested dicts** | `"a.b.c"` — full support | `"a.b.c"` — full support |
| **Array indexing** | Not supported | `"items[0]"` — supported |
| **Array filtering** | Not supported | `"items[?price>100]"` — supported |
| **Wildcards** | Not supported | `"*.name"` — supported |
| **Real-world coverage** | 99% of use cases | 100% of use cases |

**Verdict:** Dot notation is 10-50x faster and covers 99% of real use cases.
The 1% needing array access can pre-process data before passing to pypaginate.

### DA3: Token Sort Ratio vs Partial Ratio — Fuzzy Matching

**What rapidfuzz offers (3 main algorithms):**

```python
from rapidfuzz import fuzz

# 1. ratio — simple character comparison
fuzz.ratio("Alice Smith", "Smith Alice")       # → 45 (low — different order)

# 2. partial_ratio — substring matching (WE USE THIS)
fuzz.partial_ratio("Alice Smith", "Alice")     # → 100 (substring match)
fuzz.partial_ratio("Smith Alice", "Alice Smith") # → 72 (bad for reordered names)

# 3. token_sort_ratio — sorts words before comparing (v0.1 HAD THIS)
fuzz.token_sort_ratio("Smith Alice", "Alice Smith") # → 100 (perfect!)
# How: "Smith Alice" → sort → "alice smith"
#      "Alice Smith" → sort → "alice smith"
#      → identical after word-level sorting
```

| Scenario | partial_ratio | token_sort_ratio | Winner |
|---|---|---|---|
| "Alice" vs "Alice Smith" | 100 | 100 | Tie |
| "Smith" vs "Alice Smith" | 100 | 100 | Tie |
| "Smith Alice" vs "Alice Smith" | 72 | **100** | token_sort |
| "John Doe" vs "Doe, John" | 60 | **100** | token_sort |
| "New York" vs "York New" | 57 | **100** | token_sort |
| "alice" vs "alice123" | **100** | 77 | partial_ratio |
| Partial query "ali" vs "alice" | **100** | 60 | partial_ratio |

**Conclusion:** Both have different strengths:
- `partial_ratio` — best for **partial queries** and **substring search**
- `token_sort_ratio` — best for **reordered full names** and **address components**

**Recommendation:** Add `FuzzyMode.TOKEN_SORT` as an option in SearchSpec.
Users choose the strategy based on their data type. Default stays `partial_ratio`.

### DA4: Tie-Breaker Field — v0.1 vs v0.2

**The problem:** Sorting by non-unique field → unstable page results:
```
Sort by "age": Alice(30), Bob(30), Charlie(30)
Page 1: [Alice, Bob]
*refresh*
Page 1: [Bob, Alice]  ← ORDER CHANGED!
```

**v0.1 solution** — dedicated parameter:
```python
sort_items(users, sort_field="age", tie_breaker_field="id")
```

**v0.2 solution** — multi-key SortSpec:
```python
SortEngine.apply(items, [
    SortSpec(field="age"),
    SortSpec(field="id"),  # tie-breaker = any unique field
])
```

**v0.2 is better because:**
- User chooses the tie-breaker (not always `id` — could be `created_at`, `uuid`)
- Supports N sort keys, not just primary + tie-breaker
- No hidden behavior — explicit is better than implicit
- Same syntax for 1 sort key or 5

### DA5: PagedResponse vs OffsetPage — FastAPI Speed Impact

**Question:** Would a dedicated `PagedResponse` FastAPI model increase speed?

**Analysis:**

The current flow:
```python
@app.get("/users")
def get_users(params: OffsetDep):
    page = paginate(data, params)  # Returns FastOffsetPage (msgspec)
    return page.model_dump()       # Convert to dict for FastAPI
```

FastAPI then:
1. Receives the dict
2. Serializes it to JSON via `json.dumps()` or `orjson.dumps()`
3. Sends HTTP response

If we had `PagedResponse[T]`:
```python
@app.get("/users", response_model=PagedResponse[UserSchema])
def get_users(params: OffsetDep):
    return paginate(data, params)  # FastAPI auto-serializes
```

**Would this be faster?**

| Path | Steps | Speed |
|---|---|---|
| Current (`model_dump()`) | paginate → msgspec → dict → FastAPI json.dumps | ~3.9us page + FastAPI overhead |
| `response_model=` | paginate → FastAPI validates → Pydantic serializes | SLOWER — Pydantic re-validates |
| Raw `Response` | paginate → msgspec.json.encode → bytes directly | Fastest but kills OpenAPI/types |

**The answer is NO — PagedResponse would NOT be faster.**

- FastAPI's `response_model=` triggers Pydantic re-validation of the response, which is SLOWER
- Our `model_dump()` already uses msgspec (289ns) — near-zero cost
- The ~3ms HTTP overhead is FastAPI's request/response parsing, not our serialization
- A `PagedResponse` class would just be a wrapper that adds a validation step

**FastAPI overhead breakdown (from benchmarks):**
```
Filter ops only:     928 us
+ Paginate:          942 us (+14 us)   ← paginate is FREE
+ Serialize:         918 us (+0 us)    ← serialize is FREE
+ Full HTTP:       11.51 ms (+10.6 ms) ← FastAPI stack adds ~10ms
```

The 10ms HTTP overhead is:
- Request parsing (headers, query params, validation)
- ASGI middleware chain
- Response JSON encoding
- ASGI response writing

None of this is affected by a `PagedResponse` class. Our page construction (289ns) and
serialization (model_dump) are negligible compared to FastAPI's own overhead.

**Verdict:** Skip PagedResponse. It would add API surface without speed benefit.
OffsetPage already serves as the response model.

---

## Complete Documentation vs Code Discrepancy Table

Every feature mentioned in old docs with its actual status:

| Feature | Old Import Path | Current Status | Current Import |
|---|---|---|---|
| `PageParams` | `pypaginate.PageParams` | Renamed | `pypaginate.OffsetParams` |
| `Page[T]` | `pypaginate.Page` | Renamed | `pypaginate.domain.pages.OffsetPage` |
| `KeysetPageParams` | `pypaginate.core.KeysetPageParams` | Renamed | `pypaginate.CursorParams` |
| `paginate_entities()` | `pypaginate.paginate_entities` | Removed | `pypaginate.paginate()` |
| `paginate_rows()` | `pypaginate.paginate_rows` | Removed | `pypaginate.paginate()` |
| `MemoryPaginator` | `pypaginate.engines.MemoryPaginator` | Removed | `pypaginate.paginate(list, params)` |
| `SqlPaginator` | `pypaginate.engines.SqlPaginator` | Removed | `paginate(q, p, backend=SA)` |
| `PaginationSnapshot` | `pypaginate.core.PaginationSnapshot` | Removed | Direct `OffsetPage` return |
| `FilterEngine` | `pypaginate.filters.predicates.FilterEngine` | Moved | `pypaginate.filtering.engine.FilterEngine` |
| `MemorySearchService` | `pypaginate.filters.search.MemorySearchService` | Removed | `SearchEngine` + `MemorySearchBackend` |
| `SqlSearchService` | `pypaginate.filters.search.SqlSearchService` | Removed | `SQLAlchemySearchBackend` |
| `SearchOptions` | `pypaginate.filters.search.options.SearchOptions` | Removed | `pypaginate.domain.specs.SearchSpec` |
| `SortEngine` | `pypaginate.sorting.SortEngine` | Moved | `pypaginate.sorting.engine.SortEngine` |
| `sort_items()` | `pypaginate.sorting.sort_items` | Removed | `SortEngine.apply()` |
| `SqlSortAdapter` | `pypaginate.sorting.SqlSortAdapter` | Removed | `SQLAlchemySortBackend` |
| `get_pagination_params` | `pypaginate.integrations.fastapi` | Removed | `pypaginate.adapters.fastapi.OffsetDep` |
| `PagedResponse[T]` | `pypaginate.integrations.fastapi` | Removed | `OffsetPage` is response model |
| `SqlFilterAdapter` | `pypaginate.filters.sql_adapter` | Removed | `SQLAlchemyFilterBackend` |
| JSON Logic dicts | `FilterEngine.filter(items, {...})` | Removed | `FilterEngine.apply(items, [FilterSpec])` |
| `decode_cursor()` | `pypaginate.engines.keyset.decode_cursor` | Not public | Internal to `AsyncCursorPaginator` |
| `count_statement` param | `paginate_entities(..., count_statement=)` | **Implemented** | `SQLAlchemyBackend(session, count_query=...)` |
| `unique=True` param | `paginate_entities(..., unique=True)` | **Implemented** | `SQLAlchemyBackend(session, unique=True)` |
| `empty` operator | Registry | **Implemented** | `FilterSpec(operator="empty")` |
| `exists` operator | Registry | **Implemented** | `FilterSpec(operator="exists")` |
| `any`/`all` operators | Registry | Skipped | Not registered (niche use case) |
| Weighted search fields | `SearchOptions(fields={...})` | **Implemented** | `SearchSpec(weights={"name": 2.0})` |
| token_sort_ratio | `SearchOptions(fuzzy_threshold=)` | **Implemented** | `FuzzyMode.TOKEN_SORT` |
| `min_query_length` | `SearchOptions(min_query_length=)` | **Implemented** | `SearchSpec(min_length=2)` |
| `max_results` | `SearchOptions(max_results=)` | **Implemented** | `SearchSpec(max_results=100)` |
| TF-IDF scoring | Concept docs | Skipped | Simple token scoring (sufficient for in-memory) |
| Highlighting | `highlight_tag="<mark>"` | Skipped | UI concern, not pagination library |
| Operator aliases | `==`, `!=`, `>` etc. | Skipped | One canonical name per operator |
