# Refactoring Plan v0.1.1

> **Comprehensive execution guide for architecture refactoring**
>
> This document provides step-by-step instructions for refactoring pypaginate
> from v0.1.0 to v0.1.1. Each task includes specific file targets, prescribed
> refactoring techniques, verification criteria, and dependencies.

---

## Executive Summary

**Objective:** Fix architectural violations, SOLID principle violations, and code
smells BEFORE adding new features in v0.2.0+.

**Scope:** 11 files >200 lines, 52 boolean parameters, 11 function violations,
14 documented code smells, 8 untested modules, **directory structure violations**.

**Duration estimate:** 4-5 focused sessions (12-16 hours total)

**Key metrics to achieve:**

| Metric | Current | Target |
|--------|---------|--------|
| Files >200 lines | 11 | 0 |
| Functions >12 lines | 11 | 0 |
| Boolean parameters | 52 | 0 |
| French comments | 19 lines | 0 |
| Untested modules | 8 | 0 |
| Test coverage | ~85% | 90%+ |
| Duplicated file names | 6 | 0 |
| Architecture layers | unclear | 4 distinct |

---

## Critical Architecture Issues

Before diving into phases, understand the **structural problems** in the current codebase:

### Problem 1: Duplicated File Names (Confusing)

| File Name | Locations | Problem |
|-----------|-----------|---------|
| `types.py` | root, `database/` | Two different purposes, confusing imports |
| `engine.py` | `filters/predicates/`, `sorting/` | Same name, different concerns |
| `helpers.py` | `filters/search/` | Generic name, unclear purpose |
| `api.py` | `text/` | Vague name |

### Problem 2: Scattered Concerns (No Clear Layers)

| Concern | Current Location | Problem |
|---------|-----------------|---------|
| Protocols | `types.py` (root) | Mixed with SQLAlchemy abstractions |
| SQLAlchemy types | `database/types.py` | Separate from other SQL code |
| FastAPI deps | `dependencies.py` (root) + `integrations/fastapi.py` | **DUPLICATED** `PagedResponse`! |
| SQL adapters | `filters/sql_adapter.py`, `sorting/sql_adapter.py` | Scattered, not in `adapters/` |

### Problem 3: Unclear Separation of Concerns

Current structure mixes pure logic with database-specific code. SQL concerns are
scattered across 6+ packages (`engines/`, `filters/`, `sorting/`, `database/`,
`query/`), while `database/` is a near-empty 2-file orphan. The `query/` package
is a thin async wrapper that could live with its engine. The `core/` name is vague
and `snapshots.py` inside it depends on `sqlakeyset` — violating the principle that
core models should be dependency-free.

```
CURRENT (scattered SQL):            TARGET (consolidated):
pypaginate/                         pypaginate/
├── types.py (protocols+sql)        ├── protocols.py      # All Protocol definitions
├── core/ (models+sql dep)          ├── core/             # Pure models (no I/O deps)
├── engines/ (sql+memory)           ├── engines/          # Pagination strategies
├── filters/ (logic+sql)            │   ├── sql/          # SQLAlchemy backend
├── query/ (thin sql wrapper)       │   └── memory.py     # In-memory backend
├── database/ (orphan)              ├── filters/          # Filtering (keep as-is, clean)
├── sorting/ (logic+sql)            ├── sorting/          # Sorting (keep as-is, clean)
├── text/ (utility)                 ├── text/             # Text utilities (keep as-is)
├── integrations/ (duplicate)       └── integrations/     # Framework support (deduplicated)
└── dependencies.py (duplicate)
```

### Problem 4: Duplicate Code

`PagedResponse` is defined in **TWO** files:
- `dependencies.py:24-48`
- `integrations/fastapi.py:31-40+`

This violates DRY and causes confusion about which to use.

---

## Phase Overview

| Phase | Focus | Tasks | Dependency |
|-------|-------|-------|------------|
| **Phase 0** | Preparation | Install tools, run baselines, create branch | None |
| **Phase 1** | Test Coverage First | Test untested modules BEFORE refactoring | Phase 0 |
| **Phase 1.5** | **Directory Restructure** | Reorganize to hexagonal architecture | Phase 1 |
| **Phase 2** | Architecture | Protocols, DIP, layer separation | Phase 1.5 |
| **Phase 3** | SOLID & Patterns | Boolean elimination, strategy patterns | Phase 2 |
| **Phase 4** | Code Smells | Large files, long methods, dead code | Phase 3 |
| **Phase 5** | Cleanup | French comments, public API audit | Phase 4 |
| **Phase 6** | Verification | Full quality pass, documentation | Phase 5 |

---

## Phase 0: Preparation

### Task 0.1: Install Analysis Tools

**Objective:** Ensure all analysis tools are available.

```bash
# Verify tools are installed
uv add --dev vulture  # Dead code detection (DONE)
uv run vulture --version
uv run bandit --version
uv run radon --version
```

**Verification:** All commands execute without error.

---

### Task 0.2: Run Baseline Analysis

**Objective:** Capture current state metrics for comparison.

```bash
# Security scan
uv run bandit -r src/ -f txt > baseline-security.txt

# Dead code scan
uv run vulture src/ --min-confidence 80 > baseline-deadcode.txt

# Complexity analysis
uv run radon cc src/ -a -s > baseline-complexity.txt

# Test coverage
uv run pytest --cov --cov-report=term-missing > baseline-coverage.txt
```

**Verification:** Four baseline files created. Store these for before/after comparison.

---

### Task 0.3: Create Feature Branch

**Objective:** Create dedicated branch for v0.1.1 refactoring.

```bash
git checkout main
git pull origin main
git checkout -b refactor/v0.1.1-architecture
```

**Verification:** Branch created, clean working tree.

---

## Phase 1: Test Coverage First

> **Rationale:** Tests must exist BEFORE refactoring. They serve as a safety net
> to catch regressions. Without tests, we cannot refactor with confidence.

### Task 1.1: Test `_cli.py` (CRITICAL)

**File:** `src/pypaginate/_cli.py` (390 lines)
**Priority:** CRITICAL — 8 of 11 function violations are here

**Current state:** Completely untested, excluded from coverage.

**Approach:**
1. Create `tests/unit/test_cli.py`
2. Test each command function (`cmd_*`) in isolation
3. Mock subprocess calls to avoid actual command execution
4. Test argument parsing and help output

**Test structure:**

```python
# tests/unit/test_cli.py
import pytest
from unittest.mock import patch, MagicMock
from pypaginate._cli import (
    cmd_test, cmd_test_cov, cmd_quality, cmd_quality_strict,
    cmd_build, cmd_clean, main, _run, _show_help
)

class TestCmdTest:
    def test_runs_pytest_with_default_args(self): ...
    def test_passes_additional_args(self): ...

class TestCmdTestCov:
    def test_runs_pytest_with_coverage(self): ...
    def test_generates_html_report(self): ...

class TestCmdQuality:
    def test_runs_all_quality_checks(self): ...
    def test_stops_on_first_failure(self): ...

class TestMain:
    def test_dispatches_to_correct_command(self): ...
    def test_shows_help_with_no_args(self): ...
    def test_shows_help_with_help_flag(self): ...
```

**Verification:**
- `uv run pytest tests/unit/test_cli.py -v` passes
- Coverage for `_cli.py` reaches 80%+

**Technique:** None (test writing, not refactoring)

---

### Task 1.2: Test `query/async_api.py` (HIGH)

**File:** `src/pypaginate/query/async_api.py` (289 lines)
**Priority:** HIGH — Core async pagination API

**Approach:**
1. Create `tests/unit/query/test_async_api.py`
2. Test `paginate_entities()`, `paginate_scalars()`, `paginate_keyset()`
3. Use async test fixtures with mock sessions

**Test structure:**

```python
# tests/unit/query/test_async_api.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from pypaginate.query.async_api import paginate_entities, paginate_scalars

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    return session

class TestPaginateEntities:
    @pytest.mark.asyncio
    async def test_returns_page_with_items(self, mock_session): ...
    
    @pytest.mark.asyncio
    async def test_applies_filters(self, mock_session): ...
```

**Verification:**
- `uv run pytest tests/unit/query/test_async_api.py -v` passes
- Coverage for `async_api.py` reaches 80%+

---

### Task 1.3: Test `query/execution/async_executor.py` (HIGH)

**File:** `src/pypaginate/query/execution/async_executor.py` (~120 lines)
**Priority:** HIGH — Async execution engine

**Approach:**
1. Create `tests/unit/query/execution/test_async_executor.py`
2. Test `AsyncQueryExecutor` class methods
3. Mock database operations

**Verification:**
- Coverage for `async_executor.py` reaches 80%+

---

### Task 1.4: Test `filters/search/sql_search.py` (HIGH)

**File:** `src/pypaginate/filters/search/sql_search.py` (~100 lines)
**Priority:** HIGH — SQL search service

**Approach:**
1. Create `tests/unit/filters/search/test_sql_search.py`
2. Test SQL clause generation
3. Verify correct LIKE/ILIKE patterns

**Verification:**
- Coverage for `sql_search.py` reaches 80%+

---

### Task 1.5: Test Remaining Modules (MEDIUM/LOW)

**Files:**
- `filters/search/strategies.py` (~80 lines) — MEDIUM
- `filters/search/conditions.py` (~90 lines) — MEDIUM
- `filters/search/factories.py` (~60 lines) — MEDIUM
- `database/types.py` (~30 lines) — LOW (type definitions only)

**Approach:** Create corresponding test files for each.

**Verification:**
- All 8 previously untested modules have test coverage
- `uv run pytest --cov` shows no uncovered source files

---

### Task 1.6: Enable CLI Coverage Measurement

**File:** `pyproject.toml`

**Current state:** `_cli.py` is excluded from coverage:
```toml
[tool.coverage.run]
omit = ["src/pypaginate/_cli.py"]
```

**Action:** Remove the omit after Task 1.1 completes.

**Verification:**
- `uv run pytest --cov` includes `_cli.py` in coverage report
- Overall coverage remains at or above `fail_under = 85`

---

## Phase 1.5: Directory Architecture Restructure

> **Rationale:** Before adding protocols and fixing SOLID violations, we must have a
> coherent directory structure. Moving files AFTER adding protocols would require
> updating many more imports.
>
> **Design principles:**
> 1. Keep folder names that already describe their purpose well (`engines/`, `filters/`, `sorting/`, `text/`)
> 2. Fix the actual problems: duplicate files, scattered SQL, orphan packages
> 3. Consolidate SQL code under `engines/sql/` — the natural home for all SQLAlchemy concerns
> 4. Keep the structure flat enough to be navigable, deep enough to separate concerns
> 5. Plan for future backends (Tortoise, Beanie) as siblings alongside `engines/sql/`

### Task 1.5.1: Design Target Directory Structure

**Objective:** Define the target structure that fixes all structural problems.

**Target structure:**

```
src/pypaginate/
├── __init__.py              # Public API (unchanged surface)
├── py.typed                 # PEP 561 marker
├── exceptions.py            # Exception hierarchy (stays at root — used everywhere)
├── protocols.py             # All Protocol definitions (was types.py — renamed for clarity)
│
├── core/                    # PURE MODELS — no I/O, no SQLAlchemy, no external deps
│   ├── __init__.py          # Re-exports: Page, PageParams, KeysetPageParams, etc.
│   ├── pages.py             # Page[T], PageParams, KeysetPageParams (stays — clean)
│   ├── context.py           # PaginationContext, clamp_page_params (stays — clean)
│   └── enums.py             # NEW: OverflowStrategy, ResultMode, etc. (Phase 3)
│
├── engines/                 # PAGINATION STRATEGIES — one sub-package per backend
│   ├── __init__.py          # Re-exports public engines
│   ├── memory.py            # MemoryPaginator (stays — already clean, no SQL deps)
│   └── sql/                 # ALL SQLAlchemy code consolidated here
│       ├── __init__.py      # Re-exports: SqlPaginator, paginate_entities, etc.
│       ├── paginator.py     # SqlPaginator (was engines/sql.py)
│       ├── keyset.py        # select_keyset_page (was engines/keyset.py)
│       ├── snapshots.py     # PaginationSnapshot, KeysetPaginationSnapshot (was core/snapshots.py)
│       ├── count.py         # build_count_statement, fetch_count (was query/builders/count_builder.py)
│       ├── executor.py      # Execution, gather_snapshot (was query/execution/async_executor.py)
│       ├── api.py           # paginate_entities, paginate_scalars, etc. (was query/async_api.py)
│       ├── filters.py       # SqlFilterAdapter (was filters/sql_adapter.py)
│       ├── sorting.py       # SqlSortAdapter (was sorting/sql_adapter.py)
│       ├── search.py        # SqlSearchService (was filters/search/sql_search.py)
│       ├── collations.py    # Database collation provisioning (was database/collations.py)
│       └── types.py         # SQLAlchemy type aliases (was database/types.py)
│
├── filters/                 # FILTERING SUBSYSTEM (keep — well-organized, large enough)
│   ├── __init__.py          # Public API
│   └── predicates/          # JSON Logic predicate engine (keep as-is — self-contained)
│       ├── __init__.py
│       ├── builder.py
│       ├── engine.py
│       ├── field_accessor.py
│       ├── jsonlogic_evaluator.py
│       ├── operator_arguments.py
│       ├── registry.py
│       └── operators/
│           ├── __init__.py
│           ├── comparison.py
│           ├── patterns.py
│           ├── range.py
│           ├── simple.py
│           └── text.py
│
├── search/                  # TEXT SEARCH SUBSYSTEM (promoted from filters/search/)
│   ├── __init__.py          # Public API
│   ├── conditions.py        # Search condition builders
│   ├── factories.py         # Service factories
│   ├── fuzzy.py             # Fuzzy matching
│   ├── helpers.py           # SQL clause helpers
│   ├── memory_search.py     # MemorySearchService (pure Python, stays here)
│   ├── options.py           # Search configuration
│   ├── parser.py            # Query parser
│   └── strategies.py        # Search strategies
│
├── sorting/                 # SORTING SUBSYSTEM (keep — clean separation)
│   ├── __init__.py
│   └── engine.py            # SortEngine — in-memory sorting (pure Python)
│
├── text/                    # TEXT UTILITIES (keep as-is — clean, self-contained)
│   ├── __init__.py
│   ├── api.py
│   ├── utf8.py
│   ├── patterns.py
│   └── pipelines.py
│
├── integrations/            # FRAMEWORK SUPPORT (keep — single source of truth)
│   ├── __init__.py
│   └── fastapi.py           # PagedResponse + get_pagination_params (DEDUPLICATED)
│
└── _cli/                    # CLI (split from _cli.py in Phase 4)
    ├── __init__.py
    ├── commands.py
    ├── runner.py
    └── output.py
```

**Key design decisions:**

| Decision | Rationale |
|----------|-----------|
| Rename `types.py` → `protocols.py` | Fixes duplicate name, describes actual content |
| Move `snapshots.py` from `core/` → `engines/sql/` | It depends on `sqlakeyset` — not pure, belongs with SQL |
| Consolidate all SQL in `engines/sql/` | Fixes scattered concerns — single place for all SQLAlchemy code |
| Absorb `database/` into `engines/sql/` | `database/` was an orphan (2 files) — its content is SQL-specific |
| Absorb `query/` into `engines/sql/` | `query/` was a thin async wrapper over `engines/sql` — same concern |
| Promote `filters/search/` → `search/` | Search is a top-level concern, not a sub-concern of filtering |
| Remove `filters/sql_adapter.py` | SQL filtering belongs in `engines/sql/filters.py` |
| Remove `sorting/sql_adapter.py` | SQL sorting belongs in `engines/sql/sorting.py` |
| Delete `dependencies.py` | Duplicate of `integrations/fastapi.py` — keep one source |
| Keep `engines/memory.py` flat | Single file, no sub-package needed |
| Keep `filters/predicates/` as-is | Well-organized, self-contained, no changes needed |
| Keep `text/` as-is | Clean, no external deps, no issues |
| Keep `sorting/engine.py` | Pure Python sorting — no SQL deps |

**What this solves:**

| Problem | Solution |
|---------|----------|
| Duplicate `types.py` | Root renamed to `protocols.py`, SQL aliases in `engines/sql/types.py` |
| Duplicate `engine.py` | `filters/predicates/engine.py` stays, `sorting/engine.py` stays — different packages |
| Duplicate `PagedResponse` | Delete `dependencies.py`, keep `integrations/fastapi.py` |
| Scattered SQL concerns | All consolidated under `engines/sql/` |
| Orphan `database/` package | Absorbed into `engines/sql/` |
| Thin `query/` wrapper | Absorbed into `engines/sql/` |
| `snapshots.py` in pure `core/` | Moved to `engines/sql/` where its `sqlakeyset` dep belongs |
| No clear layers | Pure core → engines (backends) → integrations (frameworks) |

**Future evolution (v0.2.0+):**

```
engines/
├── memory.py              # Existing in-memory backend
├── sql/                   # Existing SQLAlchemy backend
│   └── ...
├── tortoise/              # NEW: Tortoise ORM backend
│   ├── __init__.py
│   ├── paginator.py
│   ├── filters.py
│   └── sorting.py
└── beanie/                # NEW: Beanie/MongoDB backend
    ├── __init__.py
    ├── paginator.py
    └── filters.py
```

New backends become sibling packages under `engines/`. Each backend contains
its own paginator, filters, sorting, and search — no scattered concerns.

**Verification:**
- Target structure documented and reviewed
- No `domain/`, `application/`, `adapters/`, or `_internal/` directories

---

### Task 1.5.2: Create New Directories

**Objective:** Create the new directory structure.

```bash
# engines/sql/ — the main new package
mkdir -p src/pypaginate/engines/sql

# search/ — promoted from filters/search/
mkdir -p src/pypaginate/search

# _cli/ — will be used in Phase 4 (Task 4.1), create now for consistency
mkdir -p src/pypaginate/_cli
```

**Create `__init__.py` for each new package:**

```python
# engines/sql/__init__.py
"""SQLAlchemy pagination backend."""
from __future__ import annotations

# search/__init__.py
"""Text search subsystem."""
from __future__ import annotations

# _cli/__init__.py
"""CLI commands for pypaginate."""
from __future__ import annotations
```

**Verification:**
- All new directories exist with `__init__.py`
- Existing directories untouched

---

### Task 1.5.3: Rename `types.py` → `protocols.py`

**Technique:** Rename Method/Class (`guru-refactor-calls`) — applied to module

**Problem:** `types.py` at root collides with `database/types.py`. The root file
contains Protocol definitions, not type aliases. Name should reflect content.

**Process:**
1. Copy `types.py` → `protocols.py`
2. Update all imports: `from pypaginate.types import ...` → `from pypaginate.protocols import ...`
3. Add backward-compatible re-export in `types.py` temporarily
4. Verify all tests pass
5. Remove `types.py` after all imports updated

**Files to update (imports):**
- `__init__.py`
- `engines/sql.py`
- `filters/sql_adapter.py`
- `sorting/engine.py`
- `sorting/sql_adapter.py`
- Any test files importing from `types`

**Verification:**
- `protocols.py` contains all Protocol definitions
- No import errors
- `rg "from pypaginate.types" src/` returns only the re-export stub

---

### Task 1.5.4: Move SQL Code into `engines/sql/`

**Technique:** Move Method/Class (`guru-refactor-moving`)

**This is the core consolidation step.** All SQLAlchemy-dependent code moves here.

**Files to move:**

| Source | Target | Notes |
|--------|--------|-------|
| `engines/sql.py` | `engines/sql/paginator.py` | Rename for clarity |
| `engines/keyset.py` | `engines/sql/keyset.py` | Same name, new home |
| `core/snapshots.py` | `engines/sql/snapshots.py` | Depends on `sqlakeyset` — not pure core |
| `database/types.py` | `engines/sql/types.py` | SQLAlchemy type aliases |
| `database/collations.py` | `engines/sql/collations.py` | Database-specific |
| `query/builders/count_builder.py` | `engines/sql/count.py` | SQL count building |
| `query/execution/async_executor.py` | `engines/sql/executor.py` | SQL execution |
| `query/async_api.py` | `engines/sql/api.py` | Async API over SQL engine |
| `filters/sql_adapter.py` | `engines/sql/filters.py` | SQL filter building |
| `sorting/sql_adapter.py` | `engines/sql/sorting.py` | SQL ORDER BY building |
| `filters/search/sql_search.py` | `engines/sql/search.py` | SQL text search |

**Process for each file:**
1. Copy to new location
2. Update internal imports (relative paths change)
3. Add temporary re-export in old location
4. Run `uv run pytest` after each move
5. After all moves, update external imports
6. Remove re-export stubs

**Backward compatibility stub example:**
```python
# engines/sql.py (after move, temporary)
"""Deprecated: Import from pypaginate.engines.sql.paginator instead."""
from pypaginate.engines.sql.paginator import SqlPaginator  # noqa: F401
```

**Import update strategy:**
- Internal imports (within the moved files) — fix relative paths immediately
- External imports (from other packages) — update after all moves complete
- Public API (`__init__.py`) — update last to maintain compatibility during migration

**Verification:**
- `engines/sql/` contains 11 files + `__init__.py`
- All SQLAlchemy imports are within `engines/sql/`
- `rg "from sqlalchemy" src/ --files-with-matches` shows only files in `engines/sql/` and `integrations/`
- All tests pass

---

### Task 1.5.5: Promote `filters/search/` → `search/`

**Technique:** Move Method/Class (`guru-refactor-moving`)

**Rationale:** Search is a significant subsystem (8 files, ~1500 lines) that handles
its own concerns: parsing, fuzzy matching, strategies, memory search. It deserves
top-level visibility rather than being nested under `filters/`.

The SQL search service (`sql_search.py`) already moved to `engines/sql/search.py`
in Task 1.5.4. The remaining files are pure Python or memory-based.

**Files to move:**

| Source | Target |
|--------|--------|
| `filters/search/conditions.py` | `search/conditions.py` |
| `filters/search/factories.py` | `search/factories.py` |
| `filters/search/fuzzy.py` | `search/fuzzy.py` |
| `filters/search/helpers.py` | `search/helpers.py` |
| `filters/search/memory_search.py` | `search/memory_search.py` |
| `filters/search/options.py` | `search/options.py` |
| `filters/search/parser.py` | `search/parser.py` |
| `filters/search/strategies.py` | `search/strategies.py` |
| `filters/search/__init__.py` | `search/__init__.py` |

**Process:**
1. Move all files at once (they're self-contained)
2. Update internal imports between search files
3. Update imports from other packages that reference `filters.search`
4. Remove `filters/search/` directory
5. Run tests

**Verification:**
- `search/` exists as top-level package
- `filters/search/` removed
- `rg "from.*filters.search" src/` returns 0 results
- All search tests pass

---

### Task 1.5.6: Delete Duplicate FastAPI Code

**Technique:** Inline Class (`guru-refactor-moving`) — merge duplicates
**Smell:** Duplicate Code

**Problem:** `PagedResponse` defined in both:
- `dependencies.py:24-48` (unconditional `fastapi` import — breaks if fastapi missing)
- `integrations/fastapi.py:31-65` (proper try/except — graceful fallback)

**Solution:**
1. Keep `integrations/fastapi.py` as the single source of truth (it has proper error handling)
2. Delete `dependencies.py` entirely
3. Update `__init__.py` if it imports from `dependencies`
4. Update any test files

**Verification:**
- `dependencies.py` deleted
- `rg "from.*dependencies" src/` returns 0 results
- `from pypaginate.integrations.fastapi import PagedResponse` works
- `PagedResponse` definition exists in exactly 1 file

---

### Task 1.5.7: Clean Up Empty Packages

**After all moves complete:**

```bash
# Remove absorbed packages
rm -rf src/pypaginate/database/          # Absorbed into engines/sql/
rm -rf src/pypaginate/query/             # Absorbed into engines/sql/
rm -rf src/pypaginate/filters/search/    # Promoted to search/
rm src/pypaginate/dependencies.py        # Duplicate deleted
rm src/pypaginate/types.py               # Renamed to protocols.py

# Remove old engine files (now in engines/sql/)
rm src/pypaginate/engines/sql.py         # Now engines/sql/paginator.py
rm src/pypaginate/engines/keyset.py      # Now engines/sql/keyset.py

# Remove moved adapters
rm src/pypaginate/filters/sql_adapter.py # Now engines/sql/filters.py
rm src/pypaginate/sorting/sql_adapter.py # Now engines/sql/sorting.py

# Remove snapshots from core (now in engines/sql/)
rm src/pypaginate/core/snapshots.py      # Now engines/sql/snapshots.py
```

**Verification:**
- No orphan directories remain
- No empty `__init__.py`-only packages
- `find src/pypaginate -type d -empty` returns nothing

---

### Task 1.5.8: Update `engines/sql/__init__.py` Public API

**Objective:** Make `engines/sql/` a clean public package with well-defined exports.

```python
# engines/sql/__init__.py
"""SQLAlchemy pagination backend.

This package provides all SQLAlchemy-specific pagination functionality:
- SqlPaginator: Offset and keyset pagination orchestrator
- Async API: paginate_entities, paginate_scalars, paginate_keyset
- Filters: SqlFilterAdapter for WHERE clause building
- Sorting: SqlSortAdapter for ORDER BY building
- Search: SqlSearchService for text search
"""
from __future__ import annotations

from .api import paginate_entities, paginate_keyset, paginate_scalars
from .paginator import SqlPaginator

__all__ = [
    "SqlPaginator",
    "paginate_entities",
    "paginate_keyset",
    "paginate_scalars",
]
```

**Verification:**
- `from pypaginate.engines.sql import SqlPaginator` works
- `from pypaginate.engines.sql import paginate_entities` works

---

### Task 1.5.9: Update Root `__init__.py` Public API

**File:** `src/pypaginate/__init__.py`

**Update imports to use new locations:**

```python
# Models (from core — unchanged)
from pypaginate.core.pages import Page, PageParams, KeysetPageParams

# Protocols (renamed module)
from pypaginate.protocols import (
    PageParamsProtocol,
    PageProtocol,
    SupportsTotalOrdering,
)

# Engines
from pypaginate.engines.sql import SqlPaginator
from pypaginate.engines.memory import MemoryPaginator

# Async API (new location)
from pypaginate.engines.sql.api import (
    paginate_entities,
    paginate_scalars,
    paginate_keyset,
)

# Exceptions (unchanged)
from pypaginate.exceptions import (
    PaginationError,
    PageOutOfRangeError,
    # ... all exceptions
)
```

**Key constraint:** The *public* API surface must not change. Users who do
`from pypaginate import Page, paginate_entities` must not break.

**Verification:**
- `from pypaginate import Page, paginate_entities, SqlPaginator` works
- `python -c "from pypaginate import *; print(dir())"` shows expected names
- All existing tests pass without import changes in test files

---

### Task 1.5.10: Update All Internal Imports

**Technique:** Rename Method (`guru-refactor-calls`) — applied to imports

**Systematic process:**
1. Search for all imports of moved modules
2. Update to new locations
3. Remove all backward compatibility stubs
4. Run full test suite

**Search patterns:**
```bash
rg "from pypaginate.database" src/          # → engines/sql/types, engines/sql/collations
rg "from pypaginate.query" src/             # → engines/sql/api, engines/sql/executor, engines/sql/count
rg "from pypaginate.engines.sql import" src/  # → engines/sql/paginator (if referencing old sql.py)
rg "from pypaginate.engines.keyset" src/    # → engines/sql/keyset
rg "from pypaginate.types" src/             # → protocols
rg "from pypaginate.dependencies" src/      # → integrations/fastapi
rg "from pypaginate.core.snapshots" src/    # → engines/sql/snapshots
rg "from.*filters.sql_adapter" src/         # → engines/sql/filters
rg "from.*sorting.sql_adapter" src/         # → engines/sql/sorting
rg "from.*filters.search" src/              # → search/
```

**Also update test files:**
```bash
rg "from pypaginate" tests/                 # Check all test imports
```

**Verification:**
- All `rg` patterns above return 0 results (or only `__init__.py` re-exports)
- `uv run pytest` passes with 0 failures
- `uv run mypy src/` passes
- `uv run ruff check src/` passes

---

### Phase 1.5 Summary

**Before → After file count:**

| Package | Before | After | Change |
|---------|--------|-------|--------|
| Root modules | 5 (`__init__`, `types`, `exceptions`, `dependencies`, `_cli`) | 4 (`__init__`, `protocols`, `exceptions`, `_cli`) | -1 (deleted duplicate) |
| `core/` | 4 (`__init__`, `pages`, `context`, `snapshots`) | 3 (`__init__`, `pages`, `context`) | -1 (snapshots moved to sql) |
| `engines/` | 4 (`__init__`, `sql`, `keyset`, `memory`) | 2+12 (`__init__`, `memory` + `sql/` package) | Consolidated |
| `engines/sql/` | — | 12 | New (consolidated from 5 packages) |
| `database/` | 3 | 0 | Absorbed into `engines/sql/` |
| `query/` | 6 | 0 | Absorbed into `engines/sql/` |
| `filters/` | 2 (`__init__`, `sql_adapter`) + search + predicates | 1 (`__init__`) + predicates only | SQL moved, search promoted |
| `search/` | — | 9 | Promoted from `filters/search/` |
| `sorting/` | 3 (`__init__`, `engine`, `sql_adapter`) | 2 (`__init__`, `engine`) | SQL moved |
| `text/` | 5 | 5 | Unchanged |
| `integrations/` | 3 | 3 | Unchanged (duplicate deleted elsewhere) |
| **Total** | 57 | ~57 | Same count, better organization |

**Dependency flow after restructure:**

```
pypaginate/
├── protocols.py           ← depends on: nothing (pure Protocol definitions)
├── exceptions.py          ← depends on: nothing
├── core/                  ← depends on: exceptions (pure models)
├── text/                  ← depends on: nothing (pure utilities)
├── filters/predicates/    ← depends on: nothing (pure logic)
├── search/                ← depends on: text/ (pure + memory)
├── sorting/               ← depends on: protocols (pure logic)
├── engines/memory.py      ← depends on: core/ (no SQL)
├── engines/sql/           ← depends on: core/, protocols, sqlalchemy, sqlakeyset
└── integrations/fastapi   ← depends on: core/, fastapi, pydantic
```

Each layer only depends on layers above it. SQL is fully contained.
Pure logic has zero external dependencies. Clean separation.

---

## Phase 2: Architecture (Protocols & DIP)

> **Rationale:** With clean directory structure in place, we can now add protocol
> interfaces and apply Dependency Inversion properly.

### Task 2.1: Add Backend Protocol Interfaces

**File:** `src/pypaginate/protocols.py` (was `types.py`, renamed in Phase 1.5)
**Smell:** Alternative Classes with Different Interfaces
**Principle:** Dependency Inversion Principle (DIP)
**Technique:** Extract Superclass (`guru-refactor-generalization`)

**Objective:** Define abstract protocols that both `SqlPaginator` and `MemoryPaginator`
can implement, enabling future multi-ORM support.

**Add these protocols:**

```python
from typing import Protocol, TypeVar, Generic, Any

T = TypeVar("T")

class PaginationBackend(Protocol[T]):
    """Protocol for pagination backends (SQLAlchemy, Tortoise, Beanie, etc.)."""
    
    async def count(self, query: Any) -> int:
        """Return total count for query."""
        ...
    
    async def fetch(self, query: Any, offset: int, limit: int) -> list[T]:
        """Fetch paginated results."""
        ...

class FilterBackend(Protocol):
    """Protocol for filter backends."""
    
    def apply_filters(self, query: Any, filters: FilterValues) -> Any:
        """Apply filters to query and return modified query."""
        ...

class SortBackend(Protocol):
    """Protocol for sorting backends."""
    
    def apply_sorting(self, query: Any, sorting: SortValues) -> Any:
        """Apply sorting to query and return modified query."""
        ...
```

**Verification:**
- `uv run mypy src/pypaginate/protocols.py` passes
- Protocols are exported in `protocols.py.__all__`

---

### Task 2.2: Implement PaginationBackend for SqlPaginator

**File:** `src/pypaginate/engines/sql/paginator.py` (was `engines/sql.py`)
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure `SqlPaginator` implements `PaginationBackend` protocol
2. Add async `count()` and `fetch()` methods if missing
3. Use `typing_extensions.Self` for method chaining

**Verification:**
- `isinstance(SqlPaginator(), PaginationBackend)` returns `True` (via Protocol)
- Existing tests still pass

---

### Task 2.3: Implement PaginationBackend for MemoryPaginator

**File:** `src/pypaginate/engines/memory.py`
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure `MemoryPaginator` implements `PaginationBackend` protocol
2. Add async wrappers if needed (memory operations are sync but API is async)

**Verification:**
- `isinstance(MemoryPaginator(), PaginationBackend)` returns `True`
- Existing tests still pass

---

### Task 2.4: Implement FilterBackend for SqlFilterAdapter

**File:** `src/pypaginate/engines/sql/filters.py` (was `filters/sql_adapter.py`)
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure `SqlFilterAdapter` implements `FilterBackend` protocol
2. Rename or add `apply_filters()` method

**Verification:**
- Protocol conformance verified
- Existing filter tests still pass

---

### Task 2.5: Implement SortBackend for SqlSortingAdapter

**File:** `src/pypaginate/engines/sql/sorting.py` (was `sorting/sql_adapter.py`)
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure sorting adapter implements `SortBackend` protocol
2. Add `apply_sorting()` method

**Verification:**
- Protocol conformance verified
- Existing sorting tests still pass

---

### Task 2.6: Refactor Page to Pydantic Model

**File:** `src/pypaginate/core/pages.py`
**Smell:** Duplicate Code (Page + PagedResponse)
**Technique:** Inline Class (`guru-refactor-moving`)

**Objective:** Convert `Page[T]` from frozen dataclass to frozen Pydantic model,
eliminating the need for separate `PagedResponse[T]`.

**Before:**
```python
@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    limit: int
```

**After:**
```python
from pydantic import BaseModel, ConfigDict, computed_field

class Page(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True)
    
    items: list[T]
    total: int
    page: int
    limit: int
    
    @computed_field
    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.limit) if self.limit else 0
    
    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @computed_field
    @property
    def has_prev(self) -> bool:
        return self.page > 1
```

**Follow-up actions:**
1. Remove `PagedResponse` from `integrations/fastapi.py`
2. Update all imports referencing `PagedResponse`
3. Update tests

**Verification:**
- `Page[T]` works directly as FastAPI `response_model`
- All existing Page tests pass
- `PagedResponse` is removed

---

## Phase 3: SOLID & Design Patterns

> **Rationale:** With protocols in place, we can now fix SOLID violations and apply
> proper design patterns.

### Task 3.1: Create Enum Types for Boolean Replacements

**New file:** `src/pypaginate/core/enums.py`
**Smell:** Primitive Obsession, Long Parameter List
**Technique:** Replace Type Code with Class (`guru-refactor-data`)

**Create these enums:**

```python
from enum import Enum, auto

class OverflowStrategy(Enum):
    """How to handle page numbers exceeding total pages."""
    CLAMP = auto()   # Clamp to last page
    ERROR = auto()   # Raise error
    EMPTY = auto()   # Return empty page

class ResultMode(Enum):
    """Whether to deduplicate results."""
    UNIQUE = auto()  # Remove duplicates
    ALL = auto()     # Keep all results

class ReturnType(Enum):
    """What type to return from queries."""
    SCALARS = auto()  # Return scalar values
    ROWS = auto()     # Return row objects

class SortDirection(Enum):
    """Sort direction."""
    ASC = auto()
    DESC = auto()

class SearchFieldMode(Enum):
    """How to match search terms against fields."""
    PREFIX = auto()    # Match start of field
    EXACT = auto()     # Exact match
    CONTAINS = auto()  # Match anywhere in field

class CaseTransform(Enum):
    """Case transformation for text processing."""
    NONE = auto()      # No transformation
    LOWER = auto()     # Lowercase
    UPPER = auto()     # Uppercase
    FOLD = auto()      # Unicode case folding

class CaseSensitivity(Enum):
    """Case sensitivity for matching."""
    SENSITIVE = auto()
    INSENSITIVE = auto()

class CopyDepth(Enum):
    """Depth for object copying."""
    SHALLOW = auto()
    DEEP = auto()

class MatchPosition(Enum):
    """Which match to return when multiple exist."""
    FIRST = auto()
    LAST = auto()
    ALL = auto()
```

**Verification:**
- File is under 200 lines
- All enums have clear docstrings
- Exported in `__init__.py`

---

### Task 3.2: Replace Boolean Parameters — Batch 1 (prefix, 10 occurrences)

**Files:**
- `search/conditions.py`
- `search/fuzzy.py`
- `search/helpers.py`
- `search/memory_search.py`

**Technique:** Replace Parameter with Explicit Methods (`guru-refactor-calls`)

**Before:**
```python
def build_condition(field, term, prefix=True): ...
```

**After:**
```python
def build_condition(field, term, mode: SearchFieldMode = SearchFieldMode.PREFIX): ...
```

**Process:**
1. Add `mode` parameter alongside `prefix`
2. Map `prefix=True` to `SearchFieldMode.PREFIX`, `prefix=False` to appropriate mode
3. Update all call sites
4. Remove `prefix` parameter
5. Run tests

**Verification:**
- `rg "prefix\s*=" src/` returns 0 results for parameter usage
- All tests pass

---

### Task 3.3: Replace Boolean Parameters — Batch 2 (unique, 9 occurrences)

**Files:**
- `engines/sql/keyset.py`
- `engines/sql/paginator.py`
- `engines/sql/count.py`
- `engines/sql/executor.py`

**Technique:** Replace Parameter with Explicit Methods (`guru-refactor-calls`)

**Before:**
```python
def fetch(self, query, unique=True): ...
```

**After:**
```python
def fetch(self, query, mode: ResultMode = ResultMode.UNIQUE): ...
```

**Verification:**
- `rg "unique\s*=" src/` returns 0 results for parameter usage
- All tests pass

---

### Task 3.4: Replace Boolean Parameters — Batch 3 (scalars, 8 occurrences)

**Files:**
- `engines/sql/snapshots.py`
- `engines/sql/paginator.py`
- `engines/sql/api.py`
- `engines/sql/executor.py`

**Technique:** Replace Parameter with Explicit Methods (`guru-refactor-calls`)

**Verification:**
- `rg "scalars\s*=" src/` returns 0 results for parameter usage
- All tests pass

---

### Task 3.5: Replace Boolean Parameters — Batch 4 (reverse, 5 occurrences)

**File:** `sorting/engine.py`
**Technique:** Separate methods (`sort_ascending()`, `sort_descending()`)

**Before:**
```python
def sort(self, items, field, reverse=False): ...
```

**After:**
```python
def sort_ascending(self, items, field): ...
def sort_descending(self, items, field): ...
```

**Verification:**
- `rg "reverse\s*=" src/` returns 0 results for parameter usage
- All tests pass

---

### Task 3.6: Replace Boolean Parameters — Remaining (14 occurrences)

**Parameters:** `predicate`, `clamp`, `deep`, `comparator`, `case_sensitive`,
`check`, `capture`, `conditions`, `first`, `flags`, `descending`, `lowercase`,
`casefold_output`

**Apply appropriate technique for each:**
- Single occurrences: Enum parameter or separate methods
- `check`/`capture` in `_cli.py`: Can use enums for clarity

**Verification:**
- `rg ":\s*bool\s*=" src/` returns 0 results
- All tests pass

---

### Task 3.7: Refactor SqlFilterAdapter.build_condition (35 lines)

**File:** `src/pypaginate/engines/sql/filters.py` (was `filters/sql_adapter.py`)
**Smell:** Long Method + Switch Statements
**Technique:** Replace Conditional with Polymorphism (`guru-refactor-conditionals`)

**Before (35-line match/case):**
```python
@staticmethod
def build_condition(column, operator, value):
    match operator:
        case "eq" | "equals": return column == value
        case "ne" | "not_equals": return column != value
        # ... 12 more cases
```

**After (strategy dict + 5-line method):**
```python
_OPERATORS: ClassVar[dict[str, Callable[[Column, Any], ClauseElement]]] = {
    "eq": lambda col, val: col == val,
    "equals": lambda col, val: col == val,
    "ne": lambda col, val: col != val,
    "not_equals": lambda col, val: col != val,
    "gt": lambda col, val: col > val,
    # ... remaining operators
}

@staticmethod
def build_condition(column: Column, operator: str, value: Any) -> ClauseElement:
    """Build SQL condition from operator and value.
    
    Args:
        column: SQLAlchemy column to filter.
        operator: Operator name (eq, ne, gt, etc.).
        value: Value to compare against.
        
    Returns:
        SQLAlchemy clause element.
        
    Raises:
        ValueError: If operator is not supported.
    """
    builder = SqlFilterAdapter._OPERATORS.get(operator)
    if builder is None:
        raise ValueError(f"Unknown operator: {operator}")
    return builder(column, value)
```

**Verification:**
- Function body is ≤12 lines
- All existing filter tests pass
- New tests cover unknown operator error

---

### Task 3.8: Add Missing SQL Adapter Operators (10 operators)

**File:** `src/pypaginate/engines/sql/filters.py` (was `filters/sql_adapter.py`)
**Smell:** Incomplete Library Class
**Technique:** Introduce Foreign Method (`guru-refactor-moving`)

**Add these operators to `_OPERATORS` dict:**

| Operator | SQL Implementation |
|----------|-------------------|
| `between` | `col.between(val[0], val[1])` |
| `range` | Same as `between` |
| `icontains` | `col.ilike(f"%{val}%")` |
| `istartswith` | `col.ilike(f"{val}%")` |
| `iendswith` | `col.ilike(f"%{val}")` |
| `regex` | `col.op("~")(val)` (PostgreSQL) |
| `iregex` | `col.op("~*")(val)` (PostgreSQL) |
| `is_not_null` | `col.isnot(None)` |
| `empty` | `col == ""` or `col.is_(None)` |
| `not_empty` | `col != ""` and `col.isnot(None)` |

**Verification:**
- `SqlFilterAdapter._OPERATORS` has 24+ entries
- New tests cover each new operator

---

## Phase 4: Code Smells — File & Function Size

> **Rationale:** With tests in place and boolean parameters eliminated, we can safely
> split large files and extract long methods.

### Task 4.1: Split `_cli.py` (390 lines → 3 files)

**Smell:** Large Class (God Class with 4 concerns)
**Technique:** Extract Class (`guru-refactor-moving`)

**Target structure:**
```
src/pypaginate/_cli/
├── __init__.py      # Main entry point, import dispatcher
├── commands.py      # All cmd_* functions (~150 lines)
├── runner.py        # _run(), subprocess handling (~80 lines)
└── output.py        # _show_help(), formatting (~60 lines)
```

**Process:**
1. Create `_cli/` directory
2. Move `_run()` to `runner.py`
3. Move `_show_help()` to `output.py`
4. Move `cmd_*` functions to `commands.py`
5. Keep `main()` in `__init__.py` with imports
6. Update `pyproject.toml` entry point
7. Run tests

**Verification:**
- Each file under 200 lines
- `uv run pypaginate --help` works
- All CLI tests pass

---

### Task 4.2: Split `memory_search.py` (448 lines → 3 files)

**Smell:** Large Class
**Technique:** Extract Class (`guru-refactor-moving`)

**Target structure:**
```
src/pypaginate/search/
├── memory_engine.py    # Core MemorySearchService (~150 lines)
├── memory_scoring.py   # Scoring/ranking logic (~150 lines)
├── memory_matching.py  # Pattern matching (~150 lines)
└── memory_search.py    # Re-exports for backward compatibility
```

**Verification:**
- Each file under 200 lines
- All search tests pass
- Public API unchanged

---

### Task 4.3: Split `helpers.py` (302 lines → 2 files)

**File:** `src/pypaginate/search/helpers.py` (was `filters/search/helpers.py`)
**Technique:** Extract Class (`guru-refactor-moving`)

**Target structure:**
```
src/pypaginate/search/
├── sql_helpers.py    # SQL clause building (~150 lines)
├── field_helpers.py  # Field expression building (~150 lines)
└── helpers.py        # Re-exports for backward compatibility
```

**Verification:**
- Each file under 200 lines
- All tests pass

---

### Task 4.4: Split Remaining Large Files

**Files to split:**

| File | Lines | Target Structure |
|------|-------|-----------------|
| `search/options.py` | 298 | `config.py` + `validation.py` |
| `engines/sql/api.py` | 289 | Extract `options.py` |
| `engines/sql/paginator.py` | 287 | Extract count/fetch helpers |
| `parser.py` | 245 | Extract `tokens.py` |
| `engines/sql/snapshots.py` | 228 | Extract `serialization.py` |
| `sorting/engine.py` | 217 | Extract `null_handling.py` |
| `field_accessor.py` | 206 | Extract `path_resolver.py` |

**Process for each:**
1. Identify cohesive responsibility to extract
2. Create new file with extracted code
3. Update imports
4. Add backward-compatible re-exports if public API
5. Run tests

**Verification:**
- All 11 files now under 200 lines
- All tests pass

---

### Task 4.5: Extract Long CLI Functions

**File:** `src/pypaginate/_cli/commands.py` (after Task 4.1)
**Smell:** Long Method
**Technique:** Extract Method (`guru-refactor-methods`)

**Functions to refactor:**

| Function | Body Lines | Action |
|----------|------------|--------|
| `cmd_clean` | 37 | Extract `_clean_directories()`, `_clean_caches()` |
| `_show_help` | 32 | Extract help text to constant or template |
| `cmd_quality_strict` | 31 | Merge with `cmd_quality` using config param |
| `cmd_quality` | 30 | Merge with `cmd_quality_strict` |
| `cmd_build` | 16 | Extract `_build_wheel()`, `_build_sdist()` |
| `_run` | 15 | Extract `_handle_output()` |
| `cmd_test_cov` | 14 | Extract test configuration |
| `main` | 13 | Extract command dispatch dict |

**Verification:**
- All functions ≤12 body lines
- All CLI tests pass

---

### Task 4.6: Extract `_patched_json_logic_env` (16 lines)

**File:** `src/pypaginate/filters/predicates/jsonlogic_evaluator.py`
**Technique:** Extract Method (`guru-refactor-methods`)

**Before:**
```python
def _patched_json_logic_env():
    # 16 lines of env setup
```

**After:**
```python
def _create_base_env() -> dict: ...
def _add_custom_operators(env: dict) -> None: ...

def _patched_json_logic_env():
    env = _create_base_env()
    _add_custom_operators(env)
    return env
```

**Verification:**
- Function body ≤12 lines
- All predicate tests pass

---

### Task 4.7: Extract `_coerce_mode_option` (13 lines)

**File:** `src/pypaginate/search/options.py` (or `validation.py` after split)
**Technique:** Extract Method (`guru-refactor-methods`)

**Verification:**
- Function body ≤12 lines
- All search tests pass

---

## Phase 5: Cleanup

### Task 5.1: Remove French Comments (19 lines)

**Smell:** Comments (Dispensables)
**Technique:** Delete or translate

**Files and actions:**

| File | Lines | Action |
|------|-------|--------|
| `sorting/engine.py` | 27, 174, 175, 185, 214 | Delete (changelog-style comments) |
| `filters/predicates/jsonlogic_evaluator.py` | 3–4, 99, 131, 150 | Translate docstrings to English |
| `search/__init__.py` | 21, 27, 29, 33 | Translate to English |
| `filters/__init__.py` | 24, 36, 54, 65 | Translate to English |
| `search/helpers.py` | 85 | Translate to English |

**Verification:**
- `rg "[àâäéèêëîïôùûüç]" src/` returns 0 results (no French characters)
- All docstrings are in English

---

### Task 5.2: Audit Public API Exports

**Files:** All `__init__.py` files

**Actions:**
1. Add explicit `__all__` to every `__init__.py`
2. Ensure all public classes/functions are in `__all__`
3. Remove any accidental exports
4. Add the 3 missing imports to `pypaginate/__init__.py.__all__`

**Currently missing from main `__all__`:**
- `PaginationError`
- `PageOutOfRangeError`
- `InvalidFilterOperatorError`

**Verification:**
- Every `__init__.py` has explicit `__all__`
- `from pypaginate import *` exports exactly what's intended

---

### Task 5.3: Run Dead Code Detection

**Tool:** vulture

```bash
uv run vulture src/ --min-confidence 80
```

**Current known false positives:**
- `protocols.py:121` — `other` in Protocol method (ignore)
- `protocols.py:132` — `other` in Protocol method (ignore)

**Process:**
1. Run vulture
2. Investigate each finding
3. Remove confirmed dead code
4. Create `.vulture_whitelist.py` for false positives
5. Add vulture to CI

**Verification:**
- `uv run vulture src/ --min-confidence 80` reports only whitelisted items

---

### Task 5.4: Flatten Deep Module Nesting

**Current:** `filters/predicates/operators/` has 5-level nesting

**Action:** Evaluate if flattening is beneficial. If operators are small, consider:
- Merge into single `operators.py`
- Or keep as-is if organization aids maintainability

**Decision criteria:**
- If total lines < 200, merge
- If distinct responsibilities, keep separate

**Verification:**
- Module structure follows project conventions
- All imports work

---

## Phase 6: Verification

### Task 6.1: Run Full Quality Suite

```bash
uv run ruff format .
uv run ruff check --fix .
uv run mypy src/
uv run pytest --cov
```

**Verification:**
- All commands pass with 0 errors
- Coverage ≥90%

---

### Task 6.2: Run Security Scan

```bash
uv run bandit -r src/ -f txt
```

**Expected results:**
- Only known low-severity subprocess issues in `_cli/`
- No medium or high severity issues

**Verification:**
- Compare to baseline-security.txt
- No new issues introduced

---

### Task 6.3: Run Complexity Analysis

```bash
uv run radon cc src/ -a -s
```

**Verification:**
- Average complexity ≤5
- No function with complexity >10
- Compare to baseline-complexity.txt

---

### Task 6.4: Update Documentation

**Files to update:**
- `docs/contributing/roadmap.md` — Mark v0.1.1 tasks complete
- `docs/contributing/architecture.md` — Update with new structure
- `docs/concepts/architecture.md` — Update current state description
- `CHANGELOG.md` — Document all changes

**Verification:**
- All documentation reflects actual code state
- No references to removed code (PagedResponse, etc.)

---

### Task 6.5: Create Pull Request

```bash
git add .
git commit -m "refactor: complete v0.1.1 architecture refactoring

- Eliminate 52 boolean parameters with enums
- Split 11 large files to under 200 lines each
- Reduce 11 long functions to under 12 lines each
- Add 3 Protocol interfaces (PaginationBackend, FilterBackend, SortBackend)
- Migrate Page[T] to Pydantic model
- Add 10 missing SQL adapter operators
- Add tests for 8 previously untested modules
- Remove 19 lines of French comments
- Run dead code detection with vulture

Closes #XXX"

git push -u origin refactor/v0.1.1-architecture
```

**PR checklist:**
- [ ] All quality checks pass
- [ ] Coverage ≥90%
- [ ] No regressions in existing tests
- [ ] Documentation updated
- [ ] CHANGELOG updated

---

## Appendix A: Verification Checklist

Copy this checklist and check off items as you complete them:

### Phase 1: Test Coverage
- [ ] `_cli.py` has 80%+ coverage
- [ ] `async_api.py` has 80%+ coverage
- [ ] `async_executor.py` has 80%+ coverage
- [ ] `sql_search.py` has 80%+ coverage
- [ ] `strategies.py` has tests
- [ ] `conditions.py` has tests
- [ ] `factories.py` has tests
- [ ] `database/types.py` has tests (or documented as type-only)
- [ ] `_cli.py` included in coverage measurement

### Phase 1.5: Directory Architecture
- [ ] Target directory structure designed and documented
- [ ] New directories created (`engines/sql/`, `search/`, `_cli/`)
- [ ] `types.py` renamed to `protocols.py`
- [ ] All SQL code consolidated in `engines/sql/` (11 files moved)
- [ ] `filters/search/` promoted to top-level `search/`
- [ ] Duplicate `dependencies.py` deleted
- [ ] Empty packages cleaned up (`database/`, `query/`)
- [ ] `engines/sql/__init__.py` exports configured
- [ ] Root `__init__.py` exports updated to new locations
- [ ] All internal imports updated
- [ ] `rg "from sqlalchemy" src/ --files-with-matches` shows only `engines/sql/` and `integrations/`
- [ ] Public API surface unchanged for users

### Phase 2: Architecture
- [ ] `PaginationBackend` protocol added
- [ ] `FilterBackend` protocol added
- [ ] `SortBackend` protocol added
- [ ] `SqlPaginator` implements `PaginationBackend`
- [ ] `MemoryPaginator` implements `PaginationBackend`
- [ ] `Page[T]` is a Pydantic model
- [ ] `PagedResponse` removed

### Phase 3: SOLID & Patterns
- [ ] All enums created in `core/enums.py`
- [ ] `prefix` boolean replaced (10 occurrences)
- [ ] `unique` boolean replaced (9 occurrences)
- [ ] `scalars` boolean replaced (8 occurrences)
- [ ] `reverse` boolean replaced (5 occurrences)
- [ ] Remaining booleans replaced (14 occurrences)
- [ ] `SqlFilterAdapter.build_condition` refactored
- [ ] 10 missing SQL operators added

### Phase 4: Code Smells
- [ ] `_cli.py` split into 3 files
- [ ] `memory_search.py` split into 3 files
- [ ] `helpers.py` split into 2 files
- [ ] All 11 large files under 200 lines
- [ ] All 11 long functions under 12 lines

### Phase 5: Cleanup
- [ ] All French comments removed/translated
- [ ] All `__init__.py` have explicit `__all__`
- [ ] Dead code scan run
- [ ] No confirmed dead code remains

### Phase 6: Verification
- [ ] `ruff format .` passes
- [ ] `ruff check .` passes
- [ ] `mypy src/` passes
- [ ] `pytest --cov` passes with ≥90%
- [ ] `bandit -r src/` shows no new issues
- [ ] Documentation updated
- [ ] PR created and ready for review

---

## Appendix B: Skill Quick Reference

| Task Type | Skill |
|-----------|-------|
| Code smells identification | `guru-smells` |
| Extract Method, Inline Method | `guru-refactor-methods` |
| Move Method, Extract Class | `guru-refactor-moving` |
| Replace Type Code with Class | `guru-refactor-data` |
| Replace Conditional with Polymorphism | `guru-refactor-conditionals` |
| Replace Parameter with Explicit Methods | `guru-refactor-calls` |
| Extract Superclass, Pull Up Method | `guru-refactor-generalization` |
| Strategy, Observer, Command patterns | `guru-patterns-behavioral` |
| Factory, Builder, Singleton patterns | `guru-patterns-creational` |
| Adapter, Facade, Decorator patterns | `guru-patterns-structural` |
| Layered architecture, DIP | `arch-principles` |
| Input validation, SQL injection | `sec-basics` |

---

## Appendix C: Command Quick Reference

```bash
# Quality checks
uv run ruff format .           # Format
uv run ruff check --fix .      # Lint
uv run mypy src/               # Type check
uv run pytest                  # Test
uv run pytest --cov            # Coverage

# Analysis tools
uv run vulture src/            # Dead code
uv run bandit -r src/          # Security
uv run radon cc src/ -a        # Complexity

# Search for violations
rg ":\s*bool\s*=" src/         # Boolean parameters
rg "[àâäéèêëîïôùûüç]" src/     # French characters
```
