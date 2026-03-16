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

### GAP P1: Custom Count Query

- **v0.1**: `paginate_entities(session, stmt, params, count_statement=custom_count)`
- **v0.2**: No equivalent — COUNT(*) always auto-generated via subquery
- **Impact**: Production-critical. Complex JOINs produce slow COUNT(*) subqueries.
- **Competitors**: fastapi-pagination has `count_query` parameter
- **Verdict**: **MUST ADD** — blocks production SA users with complex queries
- **Design**: Add `count_query` param to `paginate()` and pipeline, pass to SA backend

### GAP P2: Deduplication (unique=True)

- **v0.1**: `paginate_entities(session, stmt, params, unique=True)`
- **v0.2**: Not available — one-to-many JOINs return duplicate rows
- **Impact**: Production-critical. Users with relationship eager loading get wrong results.
- **Competitors**: fastapi-pagination has `unique` parameter
- **Verdict**: **MUST ADD** — SA backend should call `result.unique()` when flag is set
- **Design**: Add `unique` param to SA backend's `fetch()` method

---

## FILTERING GAPS

### GAP F1: Missing Operators — empty, not_empty, exists

- **v0.1**: `empty` (checks `None`, `""`, `[]`), `not_empty`, `exists` (field present)
- **v0.2**: Only `is_null` / `is_not_null` (checks `None` only)
- **Impact**: Medium. Users need to check for empty strings/lists, not just None.
- **Verdict**: **SHOULD ADD** — 3 small operator classes

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

### GAP F4: JSON Logic Evaluation

- **v0.1**: Full JSON Logic with `{"and": [{"or": [...]}]}` nested expressions
- **v0.2**: Flat FilterSpec list with AND/OR logic enum
- **Impact**: Medium. JSON Logic supports nested groups that FilterSpec cannot express:
  `(a OR b) AND (c OR d)` — impossible with flat AND + OR partition.
- **Difference from v0.2**:
  - JSON Logic: unlimited nesting depth, standard format, frontend-compatible
  - FilterSpec: type-safe, 15x faster, IDE autocomplete, but flat AND/OR only
- **Verdict**: **CONSIDER for v0.3** — add optional JSON Logic parser that converts dicts to FilterSpec.
  Keep FilterSpec as primary API (performance + type safety). JSON Logic as convenience layer.

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

### GAP S1: Weighted Field Search

- **v0.1**: `SearchOptions(fields={"name": 2.0, "bio": 0.5})`
- **v0.2**: `SearchSpec(fields=("name", "bio"))` — all fields equal weight
- **Impact**: High. Name matches should score higher than bio matches.
- **How it would work**: Multiply field score by weight in `_best_score()`:
  ```python
  score = match_score(norm_value, norm_token, mode) * weight
  ```
- **Verdict**: **SHOULD ADD** — real DX win, simple to implement
- **Design**: Change `SearchSpec.fields` from `tuple[str, ...]` to `tuple[str, ...] | dict[str, float]`

### GAP S2: Token Sort Ratio (fuzzy matching mode)

- **v0.1**: Configurable fuzzy strategy (ratio, partial_ratio, token_sort_ratio)
- **v0.2**: Hardcoded `partial_ratio` only
- **Difference**:
  - `partial_ratio("Alice Smith", "Alice")` → 100 (substring match) ✓
  - `partial_ratio("Smith Alice", "Alice Smith")` → 72 ✗
  - `token_sort_ratio("Smith Alice", "Alice Smith")` → 100 ✓ (sorts words first)
- **Use case**: Name search where "John Doe" should match "Doe, John"
- **Impact**: Medium. Real value for name/address search.
- **Verdict**: **SHOULD ADD** — extend FuzzyMode enum with TOKEN_SORT
- **Design**: `FuzzyMode.FUZZY` (partial_ratio), `FuzzyMode.TOKEN_SORT` (token_sort_ratio)

### GAP S3: min_query_length

- **v0.1**: `SearchOptions(min_query_length=2)` — reject short queries
- **v0.2**: No minimum — 1-char queries return everything
- **Impact**: Safety. Short queries cause full table scans.
- **Verdict**: **SHOULD ADD** — trivial check in SearchEngine.apply()
- **Design**: Add `min_length: int = 1` to SearchSpec

### GAP S4: max_results Limit

- **v0.1**: `SearchOptions(max_results=100)` — cap results
- **v0.2**: No limit — search returns ALL matches
- **Impact**: Safety. Prevents returning 1M results from search.
- **Verdict**: **SHOULD ADD** — trivial slice in _rank_items()
- **Design**: Add `max_results: int | None = None` to SearchSpec

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

### GAP FA3: FilterDepends / OrderingDepends / SearchDepends

- **v0.1 docs**: Planned declarative filter/ordering/search dependencies
- **v0.2**: Not implemented — users build FilterSpec/SortSpec/SearchSpec manually
- **Impact**: Medium. More endpoint boilerplate than competitors.
- **Verdict**: **CONSIDER for v0.3** — needs proper API design, not a quick hack

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

### Must Add (Production Blockers)

| # | Feature | Effort | Impact |
|---|---|---|---|
| P1 | Custom count query for SA | Medium | Critical — blocks complex JOIN pagination |
| P2 | Deduplication (unique) for SA | Low | Critical — blocks eager-loaded relations |

### Should Add (DX Improvements)

| # | Feature | Effort | Impact |
|---|---|---|---|
| S1 | Weighted field search | Low | High — real relevance improvement |
| S2 | Token sort ratio fuzzy mode | Low | Medium — name/address search |
| S3 | min_query_length | Trivial | Medium — safety |
| S4 | max_results limit | Trivial | Medium — safety |
| F1 | empty/not_empty/exists operators | Low | Medium — common filter patterns |

### Consider for v0.3

| # | Feature | Effort | Impact |
|---|---|---|---|
| F4 | JSON Logic parser (dict → FilterSpec) | High | Medium — frontend integration |
| F6 | Django `__` filter format parser | Medium | Medium — Django developer DX |
| FA3 | FilterDepends / OrderingDepends | High | Medium — endpoint boilerplate |
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
| **Nested groups** | JSON Logic (unlimited) | Flat AND/OR | v0.1 |
| **Array access** | JMESPath (powerful) | Dot notation (simple) | v0.1 for power |
| **Fuzzy modes** | 3+ strategies | partial_ratio only | v0.1 |
| **Field weights** | SearchOptions(fields={...}) | Equal weight only | v0.1 |
