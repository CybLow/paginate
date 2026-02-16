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

### Problem 3: Missing Layered Structure

Current structure mixes all layers. Per `arch-principles` skill:

```
CURRENT (problematic):              TARGET (clean layered):
pypaginate/                         pypaginate/
├── types.py (protocols)            ├── domain/           # Contracts + models (pure, zero deps)
├── core/ (domain?)                 │   ├── models/       # Page, PageParams, context, enums
├── engines/ (infra?)               │   ├── protocols/    # PaginationBackend, FilterBackend, etc.
├── filters/ (mixed)                │   └── snapshots.py  # PaginationSnapshot (pure)
├── query/ (application?)           ├── services/         # Backend-agnostic business logic
├── database/ (infra)               │   ├── pagination.py # Orchestration (paginate_*)
├── sorting/ (domain?)              │   ├── search/       # Parser, fuzzy, strategies
├── text/ (utility)                 │   └── filtering/    # Predicate engine, JSON Logic
├── integrations/ (infra)           ├── adapters/         # All implementations
└── dependencies.py (infra)         │   ├── sqlalchemy/   # SQL backends (10 files)
                                    │   ├── memory/       # In-memory backends (4 files)
                                    │   └── fastapi/      # FastAPI integration
                                    ├── text/             # Utility (normalizers, UTF-8)
                                    └── _cli/             # CLI commands
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
| **Phase 1.5** | **Directory Restructure** | Reorganize to layered architecture | Phase 1 |
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
> coherent directory structure that reflects proper architectural layers. Moving files
> AFTER adding protocols would require updating many more imports. Per `arch-principles`
> skill.

### Task 1.5.1: Design Target Directory Structure

**Skill reference:** `arch-principles`

**Objective:** Define the target layered architecture: `domain/` → `services/` → `adapters/`.

**Architecture style:** Clean layered — three layers with strict dependency flow:

```
text/ ← (utility, used by anyone)
domain/ ← (pure, depends on nothing)
   ↑
services/ ← (depends on domain + text only)
   ↑
adapters/ ← (depends on domain + services + external libs)
```

**Target structure:**

```
src/pypaginate/
├── __init__.py              # Public API (re-exports from all layers)
├── py.typed                 # PEP 561 marker
├── exceptions.py            # Exception hierarchy (stays at root)
├── factories.py             # Convenience wiring (creates configured services/adapters)
│
├── domain/                  # CONTRACTS + MODELS (pure, zero external deps)
│   ├── __init__.py
│   ├── snapshots.py         # PaginationSnapshot (pure — no sqlakeyset)
│   ├── models/              # Pure data types
│   │   ├── __init__.py
│   │   ├── pages.py         # Page, PageParams, KeysetPageParams
│   │   ├── enums.py         # NEW: OverflowStrategy, ResultMode, SortDirection, etc.
│   │   └── context.py       # PaginationContext
│   └── protocols/           # All Protocol definitions
│       ├── __init__.py
│       ├── pagination.py    # PaginationBackend, KeysetBackend, PageProtocol
│       ├── filtering.py     # FilterBackend
│       └── sorting.py       # SortBackend, SupportsTotalOrdering
│
├── services/                # BUSINESS LOGIC (backend-agnostic, reusable by adapters)
│   ├── __init__.py
│   ├── pagination.py        # paginate_entities, paginate_scalars, paginate_keyset
│   ├── search/              # Search has real shared logic (parser, fuzzy, strategies)
│   │   ├── __init__.py
│   │   ├── parser.py        # TokenParser (used by both memory + SQL search)
│   │   ├── options.py       # SearchOptions
│   │   ├── strategies.py    # Strategy protocols (SQL impls → adapters in Phase 2)
│   │   └── fuzzy.py         # Fuzzy matching (used by memory search adapter)
│   └── filtering/           # Predicate engine (pure Python, used by memory filter adapter)
│       ├── __init__.py
│       ├── engine.py        # PredicateEngine
│       ├── builder.py       # Expression tree builder
│       ├── registry.py      # Operator registry
│       ├── accessor.py      # Field accessor (was field_accessor.py)
│       ├── arguments.py     # Operator arguments (was operator_arguments.py)
│       ├── jsonlogic.py     # JSON Logic evaluator (was jsonlogic_evaluator.py)
│       └── operators/       # Individual operator implementations
│           ├── __init__.py
│           ├── comparison.py
│           ├── patterns.py
│           ├── range.py
│           ├── simple.py
│           └── text.py
│
├── adapters/                # IMPLEMENTATIONS (each implements domain protocols)
│   ├── __init__.py
│   ├── memory/              # In-memory implementations (no external deps)
│   │   ├── __init__.py
│   │   ├── pagination.py    # MemoryPaginator → implements PaginationBackend
│   │   ├── filtering.py     # MemoryFilterBackend → uses predicate engine from services/
│   │   ├── search.py        # MemorySearchBackend → uses parser + fuzzy from services/
│   │   └── sorting.py       # MemorySortBackend → implements SortBackend (logic lives here)
│   ├── sqlalchemy/          # SQLAlchemy implementations
│   │   ├── __init__.py
│   │   ├── pagination.py    # SqlPaginator (was engines/sql.py)
│   │   ├── keyset.py        # SqlKeysetBackend (was engines/keyset.py, sqlakeyset dep)
│   │   ├── snapshots.py     # KeysetPaginationSnapshot (sqlakeyset-dependent parts)
│   │   ├── filtering.py     # SqlFilterBackend (was filters/sql_adapter.py)
│   │   ├── search.py        # SqlSearchBackend (was filters/search/sql_search.py)
│   │   ├── sorting.py       # SqlSortBackend (was sorting/sql_adapter.py)
│   │   ├── types.py         # SQLAlchemy type aliases (was database/types.py)
│   │   ├── collations.py    # Collation provisioning (was database/collations.py)
│   │   ├── executor.py      # AsyncExecutor (was query/execution/async_executor.py)
│   │   └── count.py         # CountBuilder (was query/builders/count_builder.py)
│   └── fastapi/             # FastAPI integration
│       ├── __init__.py
│       └── dependencies.py  # Single source of truth (eliminates PagedResponse duplicate)
│
├── text/                    # UTILITY (not a service — used by services and adapters)
│   ├── __init__.py
│   ├── normalizers.py       # Renamed from pipelines.py
│   ├── utf8.py
│   └── patterns.py
│
└── _cli/                    # CLI (internal, split from _cli.py)
    ├── __init__.py
    └── commands.py
```

**Design rationale:**

| Decision | Reason |
|----------|--------|
| Three layers: `domain/` → `services/` → `adapters/` | Clear dependency flow, each layer has a single purpose |
| `domain/` has `models/` + `protocols/` sub-packages | Groups related concerns; models and protocols are distinct |
| `domain/snapshots.py` at domain root (not in `models/`) | Split between domain (pure) and adapters (sqlakeyset) — root makes split clearer |
| `services/` not `application/` | Contains real shared business logic (predicates, search parsing), not just orchestration |
| `services/filtering/` is flat (no `predicates/` wrapper) | Predicates IS filtering — the wrapper added nothing |
| `services/filtering/operators/` stays as sub-package | 752 lines across 6 files — too large to merge into one file |
| Sorting has NO service layer | Simple enough: just adapter implementations (memory + SQL), no shared logic |
| Memory implementations ARE adapters | They implement the same domain protocols as SQL adapters |
| `adapters/memory/` has 4 files | pagination, filtering (uses predicate engine), search (uses parser+fuzzy), sorting |
| `adapters/sqlalchemy/` is flat (no sub-packages) | `builders/` and `execution/` had 1 file each — unnecessary nesting |
| `text/` stays at root level as utility | Used by services and adapters alike — not a service, not an adapter |
| `factories.py` at root (not in `services/`) | Creates configured instances by wiring adapters + services — imports from all layers |
| `strategies.py` temporarily in `services/search/` | Has SQL-specific implementations alongside Protocol — Phase 2 extracts Protocol to services, moves SQL impls to adapters |
| `_cli/` stays as internal package | Split from single `_cli.py` for size limits |

**Complete move table (old file → new file):**

| # | Source | Target | Notes |
|---|--------|--------|-------|
| 1 | `core/pages.py` | `domain/models/pages.py` | Domain model |
| 2 | `core/context.py` | `domain/models/context.py` | Domain model |
| 3 | `core/snapshots.py` (pure parts) | `domain/snapshots.py` | Split: pure `PaginationSnapshot` |
| 4 | `core/snapshots.py` (sqlakeyset parts) | `adapters/sqlalchemy/snapshots.py` | Split: `KeysetPaginationSnapshot` + `coerce_bookmark` |
| 5 | `types.py` (root) | `domain/protocols/` | Split into `pagination.py`, `filtering.py`, `sorting.py` |
| 6 | `query/async_api.py` | `services/pagination.py` | Orchestration layer |
| 7 | `filters/search/parser.py` | `services/search/parser.py` | Shared search logic |
| 8 | `filters/search/options.py` | `services/search/options.py` | Shared search logic |
| 9 | `filters/search/strategies.py` | `services/search/strategies.py` | Shared search logic |
| 10 | `filters/search/fuzzy.py` | `services/search/fuzzy.py` | Shared search logic |
| 11 | `filters/search/factories.py` | `factories.py` (root) | Convenience wiring — imports from all layers |
| 12 | `filters/predicates/engine.py` | `services/filtering/engine.py` | Flat — no predicates/ wrapper |
| 13 | `filters/predicates/builder.py` | `services/filtering/builder.py` | |
| 14 | `filters/predicates/registry.py` | `services/filtering/registry.py` | |
| 15 | `filters/predicates/field_accessor.py` | `services/filtering/accessor.py` | Renamed |
| 16 | `filters/predicates/operator_arguments.py` | `services/filtering/arguments.py` | Renamed |
| 17 | `filters/predicates/jsonlogic_evaluator.py` | `services/filtering/jsonlogic.py` | Renamed |
| 18 | `filters/predicates/operators/*.py` | `services/filtering/operators/*.py` | 6 files (init + 5 categories) |
| 19 | `engines/sql.py` | `adapters/sqlalchemy/pagination.py` | SQL pagination |
| 20 | `engines/keyset.py` | `adapters/sqlalchemy/keyset.py` | Keyset pagination (sqlakeyset) |
| 21 | `filters/sql_adapter.py` | `adapters/sqlalchemy/filtering.py` | SQL filtering |
| 22 | `filters/search/sql_search.py` | `adapters/sqlalchemy/search.py` | SQL search |
| 23 | `sorting/sql_adapter.py` | `adapters/sqlalchemy/sorting.py` | SQL sorting |
| 24 | `database/types.py` | `adapters/sqlalchemy/types.py` | SQLAlchemy type aliases |
| 25 | `database/collations.py` | `adapters/sqlalchemy/collations.py` | Collation provisioning |
| 26 | `query/builders/count_builder.py` | `adapters/sqlalchemy/count.py` | Flattened from sub-package |
| 27 | `query/execution/async_executor.py` | `adapters/sqlalchemy/executor.py` | Flattened from sub-package |
| 28 | `engines/memory.py` | `adapters/memory/pagination.py` | Memory pagination |
| 29 | `filters/search/memory_search.py` | `adapters/memory/search.py` | Memory search (uses services/) |
| 30 | `sorting/engine.py` | `adapters/memory/sorting.py` | Memory sorting (logic lives here) |
| 31 | NEW | `adapters/memory/filtering.py` | Memory filtering (uses predicate engine) |
| 32 | `dependencies.py` (root) | **DELETE** | Duplicate — replaced by #33 |
| 33 | `integrations/fastapi.py` | `adapters/fastapi/dependencies.py` | Single source of truth |
| 34 | `text/pipelines.py` | `text/normalizers.py` | Renamed for clarity |
| 35 | `text/utf8.py` | `text/utf8.py` | Stays |
| 36 | `text/patterns.py` | `text/patterns.py` | Stays |
| 37 | `_cli.py` | `_cli/commands.py` | Split in Phase 4 |

**No-duplication table:**

| Concern | Protocol (domain/) | Service (shared logic) | Adapter (implementation) |
|---------|-------------------|----------------------|--------------------------|
| Pagination | `PaginationBackend` | `services/pagination.py` (orchestration) | `memory/pagination.py`, `sqlalchemy/pagination.py` |
| Filtering | `FilterBackend` | `services/filtering/` (predicate engine) | `memory/filtering.py` (uses engine), `sqlalchemy/filtering.py` (SQL) |
| Search | `SearchBackend` | `services/search/` (parser, fuzzy) | `memory/search.py`, `sqlalchemy/search.py` |
| Sorting | `SortBackend` | **None** (too simple) | `memory/sorting.py`, `sqlalchemy/sorting.py` |
| Keyset | `KeysetBackend` | — | `sqlalchemy/keyset.py` |

**Verification:**
- Directory structure matches target
- Document created for team review

---

### Task 1.5.2: Create New Directory Structure

**Objective:** Create the new directories (empty `__init__.py` files).

```bash
# Create domain layer
mkdir -p src/pypaginate/domain/{models,protocols}

# Create services layer
mkdir -p src/pypaginate/services/search
mkdir -p src/pypaginate/services/filtering/operators

# Create adapters layer
mkdir -p src/pypaginate/adapters/{sqlalchemy,memory,fastapi}

# Create CLI package
mkdir -p src/pypaginate/_cli

# Create __init__.py in each new directory
find src/pypaginate/domain src/pypaginate/services src/pypaginate/adapters src/pypaginate/_cli \
  -type d -exec touch {}/__init__.py \;
```

**Verification:**
- All directories exist
- Each has `__init__.py`

---

### Task 1.5.3: Move Domain Layer (Models, Protocols, Snapshots)

**Technique:** Move Method/Class (`guru-refactor-moving`)

**Files to move:**

| Source | Target | Notes |
|--------|--------|-------|
| `core/pages.py` | `domain/models/pages.py` | Page, PageParams, KeysetPageParams |
| `core/context.py` | `domain/models/context.py` | PaginationContext |
| `core/snapshots.py` (pure parts) | `domain/snapshots.py` | `PaginationSnapshot` only |
| `core/snapshots.py` (sqlakeyset parts) | `adapters/sqlalchemy/snapshots.py` | `KeysetPaginationSnapshot` + `coerce_bookmark()` |
| `types.py` (root, protocols) | `domain/protocols/pagination.py` | `PaginationBackend`, `KeysetBackend`, `PageProtocol` |
| `types.py` (root, filtering) | `domain/protocols/filtering.py` | `FilterBackend` |
| `types.py` (root, sorting) | `domain/protocols/sorting.py` | `SortBackend`, `SupportsTotalOrdering` |

**Splitting `core/snapshots.py`:**

`core/snapshots.py` currently contains both:
- `PaginationSnapshot` — pure dataclass (no external deps) → `domain/snapshots.py`
- `KeysetPaginationSnapshot` + `coerce_bookmark()` — depend on `sqlakeyset` → `adapters/sqlalchemy/snapshots.py`

This split decouples the snapshot *concept* (domain) from the keyset *SQL implementation* (adapter).

**Splitting `types.py`:**

`types.py` currently mixes protocols for different concerns. Split into:
- `domain/protocols/pagination.py` — `PageParamsProtocol`, `PageProtocol`, `PaginationBackend`, `KeysetBackend`
- `domain/protocols/filtering.py` — `FilterBackend`, predicate protocols
- `domain/protocols/sorting.py` — `SortBackend`, `SupportsTotalOrdering`

**Process:**
1. Copy pure `PaginationSnapshot` to `domain/snapshots.py`
2. Copy `KeysetPaginationSnapshot` + `coerce_bookmark` to `adapters/sqlalchemy/snapshots.py`
3. Split `types.py` protocols into 3 files under `domain/protocols/`
4. Update internal imports
5. Add re-export in old location for backward compatibility
6. Run tests

**Backward compatibility stub (temporary):**
```python
# core/pages.py (after move)
"""Deprecated: Import from pypaginate.domain.models.pages instead."""
from pypaginate.domain.models.pages import Page, PageParams, KeysetPageParams

__all__ = ["Page", "PageParams", "KeysetPageParams"]
```

**Verification:**
- Tests pass after each move
- `from pypaginate import Page` still works
- `domain/` has zero external dependencies (no sqlalchemy, no sqlakeyset)

---

### Task 1.5.4: Move Services Layer (Pagination, Search, Filtering)

**Technique:** Move Method/Class (`guru-refactor-moving`)

**Objective:** Move all backend-agnostic business logic into `services/`.

**Files to move:**

| Source | Target | Notes |
|--------|--------|-------|
| `query/async_api.py` | `services/pagination.py` | Orchestration: `paginate_entities`, `paginate_scalars`, `paginate_keyset` |
| `filters/search/parser.py` | `services/search/parser.py` | Shared search parsing (pure Python) |
| `filters/search/options.py` | `services/search/options.py` | Search configuration |
| `filters/search/strategies.py` | `services/search/strategies.py` | Search strategies |
| `filters/search/fuzzy.py` | `services/search/fuzzy.py` | Fuzzy matching |
| `filters/predicates/engine.py` | `services/filtering/engine.py` | Predicate engine |
| `filters/predicates/builder.py` | `services/filtering/builder.py` | Filter builder |
| `filters/predicates/registry.py` | `services/filtering/registry.py` | Operator registry |
| `filters/predicates/field_accessor.py` | `services/filtering/accessor.py` | Renamed |
| `filters/predicates/operator_arguments.py` | `services/filtering/arguments.py` | Renamed |
| `filters/predicates/jsonlogic_evaluator.py` | `services/filtering/jsonlogic.py` | Renamed |
| `filters/predicates/operators/__init__.py` | `services/filtering/operators/__init__.py` | Operator package |
| `filters/predicates/operators/comparison.py` | `services/filtering/operators/comparison.py` | |
| `filters/predicates/operators/patterns.py` | `services/filtering/operators/patterns.py` | |
| `filters/predicates/operators/range.py` | `services/filtering/operators/range.py` | |
| `filters/predicates/operators/simple.py` | `services/filtering/operators/simple.py` | |
| `filters/predicates/operators/text.py` | `services/filtering/operators/text.py` | |

**Key decisions:**
- `services/filtering/` is **flat** — no `predicates/` wrapper (predicates IS filtering)
- `services/filtering/operators/` stays as sub-package (752 lines across 6 files)
- File renames: `field_accessor` → `accessor`, `operator_arguments` → `arguments`, `jsonlogic_evaluator` → `jsonlogic`
- Sorting has **NO** service — simple enough to live only in adapters

**Known temporary violations** (resolved in Phase 2):
- `services/search/strategies.py` imports SQL helpers — kept in services because the `ConditionStrategy` Protocol is genuinely shared. Phase 2 extracts the Protocol (stays in services) and moves SQL-specific implementations (`IdConditionStrategy`, `PhraseConditionStrategy`, `TermConditionStrategy`) to `adapters/sqlalchemy/`.
- `services/pagination.py` (was `async_api.py`) runtime-imports `execution/async_executor` (→ `adapters/sqlalchemy/executor.py`) — Phase 2 injects executor via the `PaginationBackend` protocol.
- `factories.py` moved to root level (not in `services/`) because it wires adapters + services together — see Task 1.5.8.

**Process:**
1. Move `query/async_api.py` → `services/pagination.py`
2. Move 4 shared search files → `services/search/`
3. Move 6 predicate files (flat) → `services/filtering/`
4. Move `operators/` sub-package → `services/filtering/operators/`
5. Update all internal imports within moved files
6. Add re-export stubs in old locations
7. Run tests after each group of moves

**Backward compatibility stub (temporary):**
```python
# filters/predicates/engine.py (after move)
"""Deprecated: Import from pypaginate.services.filtering.engine instead."""
from pypaginate.services.filtering.engine import *  # noqa: F401,F403
```

**Verification:**
- `services/` contains `pagination.py`, `search/` (4 files), `filtering/` (6+6 files)
- `services/` has **zero direct** SQLAlchemy/sqlakeyset imports (known temporary violations: `strategies.py` → `helpers`, `pagination.py` → `executor` — resolved in Phase 2)
- Tests pass after each group of moves

---

### Task 1.5.5: Move SQLAlchemy Adapters

**Technique:** Move Method/Class (`guru-refactor-moving`)

**Files to move:**

| Source | Target | Notes |
|--------|--------|-------|
| `engines/sql.py` | `adapters/sqlalchemy/pagination.py` | SQL offset pagination |
| `engines/keyset.py` | `adapters/sqlalchemy/keyset.py` | Keyset pagination (sqlakeyset) |
| `filters/sql_adapter.py` | `adapters/sqlalchemy/filtering.py` | SQL filter adapter |
| `sorting/sql_adapter.py` | `adapters/sqlalchemy/sorting.py` | SQL sort adapter |
| `filters/search/sql_search.py` | `adapters/sqlalchemy/search.py` | SQL search backend |
| `filters/search/conditions.py` | `adapters/sqlalchemy/search.py` | Merged into search (SQL clauses) |
| `filters/search/helpers.py` | `adapters/sqlalchemy/search.py` | Merged into search (SQL helpers) |
| `database/types.py` | `adapters/sqlalchemy/types.py` | SQLAlchemy type aliases |
| `database/collations.py` | `adapters/sqlalchemy/collations.py` | Collation provisioning |
| `query/builders/count_builder.py` | `adapters/sqlalchemy/count.py` | Flattened from sub-package |
| `query/execution/async_executor.py` | `adapters/sqlalchemy/executor.py` | Flattened from sub-package |

**Notes:**
- `builders/` and `execution/` are flattened — each had only 1 file, sub-packages
  were unnecessary nesting.
- `core/snapshots.py` (sqlakeyset parts) was already moved in Task 1.5.3.
- `conditions.py` and `helpers.py` are SQL-specific — they merge into
  `adapters/sqlalchemy/search.py` alongside `sql_search.py`.
- File naming uses `-ing` suffix: `filtering.py`, `sorting.py` (not `filters.py`, `sort.py`).

**Verification:**
- All SQLAlchemy code is under `adapters/sqlalchemy/`
- `rg "from sqlalchemy|from sqlakeyset" src/ --files-with-matches` shows only `adapters/sqlalchemy/`
- Tests pass

---

### Task 1.5.6: Move Memory Adapters

**Technique:** Move Method/Class (`guru-refactor-moving`)

**Files to move/create:**

| Source | Target | Notes |
|--------|--------|-------|
| `engines/memory.py` | `adapters/memory/pagination.py` | Memory pagination backend |
| `filters/search/memory_search.py` | `adapters/memory/search.py` | Memory search (uses `services/search/`) |
| `sorting/engine.py` | `adapters/memory/sorting.py` | Memory sorting (logic lives here, no service needed) |
| NEW | `adapters/memory/filtering.py` | Memory filtering (thin adapter that uses `services/filtering/` engine) |

**Notes:**
- Memory implementations ARE adapters — they implement domain protocols.
- `memory_search.py` uses the shared parser/fuzzy from `services/search/` — it's an
  adapter that calls service logic, not a service itself.
- `sorting/engine.py` moves entirely to `adapters/memory/sorting.py` — sorting has
  no service layer (too simple).
- `adapters/memory/filtering.py` is NEW — a thin adapter wrapping the predicate engine
  from `services/filtering/` to implement `FilterBackend`.

**Verification:**
- `adapters/memory/` has 4 files: `pagination.py`, `filtering.py`, `search.py`, `sorting.py`
- `MemoryPaginator` (now in `adapters/memory/pagination.py`) works as before
- Tests pass

---

### Task 1.5.7: Consolidate FastAPI Integration

**Technique:** Inline Class (`guru-refactor-moving`) — merge duplicates
**Smell:** Duplicate Code (`PagedResponse` in two files)

**Problem:** `PagedResponse` is defined in both:
- `dependencies.py:24-48`
- `integrations/fastapi.py:31+`

**Solution:**
1. Create `adapters/fastapi/dependencies.py` as single source of truth
   (merge best parts of both files)
2. Delete `dependencies.py` (root level duplicate)
3. Delete `integrations/fastapi.py` (old location)
4. Update `adapters/fastapi/__init__.py` to export public API

**Verification:**
- Single `PagedResponse` definition in `adapters/fastapi/dependencies.py`
- All FastAPI tests pass
- `from pypaginate.adapters.fastapi import PagedResponse` works

---

### Task 1.5.8: Move Text Utility, CLI + Root Factories

**Technique:** Rename Method (`guru-refactor-calls`), Move Method (`guru-refactor-moving`)

**Text utility rename:**

| Source | Target | Notes |
|--------|--------|-------|
| `text/pipelines.py` | `text/normalizers.py` | Renamed for clarity |
| `text/utf8.py` | `text/utf8.py` | Stays (no change) |
| `text/patterns.py` | `text/patterns.py` | Stays (no change) |

**Root-level convenience module:**

| Source | Target | Notes |
|--------|--------|-------|
| `filters/search/factories.py` | `factories.py` (root) | Wires adapters + services — imports from all layers |

**CLI split** (deferred to Phase 4, Task 4.1 — `_cli.py` is 390 lines):

| Source | Target | Notes |
|--------|--------|-------|
| `_cli.py` | `_cli/commands.py` | Full split happens in Phase 4 |

**Notes:**
- `text/` stays at root level as utility — used by services and adapters alike.
- Only `pipelines.py` → `normalizers.py` rename happens here.
- `factories.py` moves to root because it wires together both `services/` and `adapters/` — it can't belong to either layer.
- The `_cli/` directory was created in Task 1.5.2; the actual split into
  `commands.py`, `runner.py`, `output.py` happens in Phase 4, Task 4.1.

**Verification:**
- `text/normalizers.py` exists (not `pipelines.py`)
- `from pypaginate.text.normalizers import ...` works
- `factories.py` exists at root level (not in `services/search/`)
- `from pypaginate.factories import ...` works
- Tests pass

---

### Task 1.5.9: Create Domain Enums Stub

**Technique:** Extract Class (`guru-refactor-data`)

**Objective:** Create `domain/models/enums.py` as an empty placeholder for Phase 3.

Phase 3 (Task 3.1) will populate this file with enums that replace boolean
parameters (`OverflowStrategy`, `ResultMode`, `SortDirection`, etc.). Creating
the file now ensures the directory structure is complete.

```python
# domain/models/enums.py
"""Enum types for pypaginate domain models.

Populated in Phase 3 (Task 3.1) to replace boolean parameters.
"""

from __future__ import annotations

__all__: list[str] = []
```

**Verification:**
- `domain/models/enums.py` exists
- Importable: `from pypaginate.domain.models.enums import *`

---

### Task 1.5.10: Update All Imports

**Technique:** Rename Method (`guru-refactor-calls`) — applied to imports

**Process:**
1. Use IDE/tooling to find all imports of moved modules
2. Update to new locations following the move table from Task 1.5.1
3. Remove backward compatibility stubs
4. Run full test suite

**Verification — all must return 0 results:**
```bash
rg "from pypaginate\.engines" src/             # → adapters/sqlalchemy/ + adapters/memory/
rg "from pypaginate\.database" src/            # → adapters/sqlalchemy/types.py + collations.py
rg "from pypaginate\.query" src/               # → adapters/sqlalchemy/ + services/
rg "from pypaginate\.core\." src/              # → domain/models/
rg "from pypaginate\.integrations" src/        # → adapters/fastapi/
rg "from pypaginate\.filters\.search" src/     # → services/search/ + adapters/sqlalchemy/search.py
rg "from pypaginate\.filters\.predicates" src/ # → services/filtering/
rg "from pypaginate\.filters\.sql_adapter" src/  # → adapters/sqlalchemy/filtering.py
rg "from pypaginate\.sorting\.sql_adapter" src/  # → adapters/sqlalchemy/sorting.py
rg "from pypaginate\.sorting\.engine" src/     # → adapters/memory/sorting.py
rg "from pypaginate\.types" src/               # → domain/protocols/
rg "from pypaginate\.dependencies" src/        # → adapters/fastapi/dependencies.py
rg "from pypaginate\.text\.pipelines" src/     # → text/normalizers.py
```
- All tests pass

---

### Task 1.5.11: Clean Up Empty Directories

**After all moves complete:**

```bash
# Remove old directories (now empty after moves)
rm -rf src/pypaginate/engines/           # → adapters/sqlalchemy/ + adapters/memory/
rm -rf src/pypaginate/database/          # → adapters/sqlalchemy/types.py + collations.py
rm -rf src/pypaginate/integrations/      # → adapters/fastapi/
rm -rf src/pypaginate/query/             # → adapters/sqlalchemy/ + services/
rm -rf src/pypaginate/core/              # → domain/models/
rm -rf src/pypaginate/filters/           # → services/filtering/ + services/search/ + adapters/
rm -rf src/pypaginate/sorting/           # → adapters/memory/sorting.py + adapters/sqlalchemy/sorting.py

# Remove old files (replaced or duplicated)
rm src/pypaginate/dependencies.py        # Duplicate of integrations/fastapi.py
rm src/pypaginate/types.py               # → domain/protocols/

# These directories STAY (not empty — still contain code):
# src/pypaginate/text/                   # Utility (normalizers.py, utf8.py, patterns.py)
# src/pypaginate/_cli/                   # CLI (commands.py, split further in Phase 4)
```

**Verification:**
- No orphan directories
- `text/` still contains `normalizers.py`, `utf8.py`, `patterns.py`
- Clean structure matches target from Task 1.5.1
- All tests pass

---

### Task 1.5.12: Update Public API Exports

**File:** `src/pypaginate/__init__.py`

**Update exports to use new locations:**

```python
# Domain models
from pypaginate.domain.models.pages import Page, PageParams, KeysetPageParams
from pypaginate.domain.models.context import PaginationContext
from pypaginate.domain.models.enums import OverflowStrategy  # Added in Phase 3
from pypaginate.domain.snapshots import PaginationSnapshot

# Domain protocols
from pypaginate.domain.protocols.pagination import (
    PageParamsProtocol,
    PageProtocol,
    PaginationBackend,
    KeysetBackend,
)
from pypaginate.domain.protocols.filtering import FilterBackend
from pypaginate.domain.protocols.sorting import SortBackend

# Services layer
from pypaginate.services.pagination import (
    paginate_entities,
    paginate_scalars,
    paginate_keyset,
)

# Adapters (concrete implementations)
from pypaginate.adapters.sqlalchemy.pagination import SqlPaginator
from pypaginate.adapters.memory.pagination import MemoryPaginator

# Exceptions
from pypaginate.exceptions import (
    PaginationError,
    PageOutOfRangeError,
    InvalidFilterOperatorError,
    # ... all exceptions
)

__all__ = [
    # Models
    "Page",
    "PageParams",
    "KeysetPageParams",
    "PaginationContext",
    "PaginationSnapshot",
    # Protocols
    "PageParamsProtocol",
    "PageProtocol",
    "PaginationBackend",
    "KeysetBackend",
    "FilterBackend",
    "SortBackend",
    # Functions
    "paginate_entities",
    "paginate_scalars",
    "paginate_keyset",
    # Classes
    "SqlPaginator",
    "MemoryPaginator",
    # Exceptions
    "PaginationError",
    "PageOutOfRangeError",
    "InvalidFilterOperatorError",
    # ...
]
```

**Verification:**
- `from pypaginate import Page, paginate_entities` works
- `from pypaginate import KeysetBackend` works (new protocol)
- Public API unchanged for existing users (no breaking changes)
- `python -c "from pypaginate import *; print(dir())"` shows expected names

---

## Phase 2: Architecture (Protocols & DIP)

> **Rationale:** With clean directory structure in place, we can now add protocol
> interfaces and apply Dependency Inversion properly.

### Task 2.1: Add Backend Protocol Interfaces

**File:** `src/pypaginate/domain/protocols/pagination.py`
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
- `uv run mypy src/pypaginate/domain/protocols/` passes
- Protocols are exported in `domain/protocols/__init__.py.__all__`

---

### Task 2.2: Implement PaginationBackend for SqlPaginator

**File:** `src/pypaginate/adapters/sqlalchemy/pagination.py`
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

**File:** `src/pypaginate/adapters/memory/pagination.py`
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure `MemoryPaginator` implements `PaginationBackend` protocol
2. Add async wrappers if needed (memory operations are sync but API is async)

**Verification:**
- `isinstance(MemoryPaginator(), PaginationBackend)` returns `True`
- Existing tests still pass

---

### Task 2.4: Implement FilterBackend for SqlFilterAdapter

**File:** `src/pypaginate/adapters/sqlalchemy/filtering.py`
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure `SqlFilterAdapter` implements `FilterBackend` protocol
2. Rename or add `apply_filters()` method

**Verification:**
- Protocol conformance verified
- Existing filter tests still pass

---

### Task 2.5: Implement SortBackend for SqlSortingAdapter

**File:** `src/pypaginate/adapters/sqlalchemy/sorting.py`
**Technique:** Adapt existing class to Protocol

**Action:**
1. Ensure sorting adapter implements `SortBackend` protocol
2. Add `apply_sorting()` method

**Verification:**
- Protocol conformance verified
- Existing sorting tests still pass

---

### Task 2.6: Refactor Page to Pydantic Model

**File:** `src/pypaginate/domain/models/pages.py`
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
1. Remove `PagedResponse` from `adapters/fastapi/` (now redundant)
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

**New file:** `src/pypaginate/domain/models/enums.py`
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
- `adapters/sqlalchemy/search.py`
- `services/search/fuzzy.py`
- `services/search/strategies.py`
- `adapters/memory/search.py`

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
- `adapters/sqlalchemy/keyset.py`
- `adapters/sqlalchemy/pagination.py`
- `adapters/sqlalchemy/count.py`
- `adapters/sqlalchemy/executor.py`

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
- `domain/snapshots.py`
- `adapters/sqlalchemy/pagination.py`
- `services/pagination.py`
- `adapters/sqlalchemy/executor.py`

**Technique:** Replace Parameter with Explicit Methods (`guru-refactor-calls`)

**Verification:**
- `rg "scalars\s*=" src/` returns 0 results for parameter usage
- All tests pass

---

### Task 3.5: Replace Boolean Parameters — Batch 4 (reverse, 5 occurrences)

**File:** `adapters/memory/sorting.py`
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

**File:** `src/pypaginate/adapters/sqlalchemy/filtering.py`
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

**File:** `src/pypaginate/adapters/sqlalchemy/filtering.py`
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

### Task 4.2: Split `adapters/memory/search.py` (448 lines → 3 files)

**Smell:** Large Class
**Technique:** Extract Class (`guru-refactor-moving`)

**Target structure:**
```
src/pypaginate/adapters/memory/
├── search.py            # Core MemorySearchService (~150 lines)
├── search_scoring.py    # Scoring/ranking logic (~150 lines)
├── search_matching.py   # Pattern matching (~150 lines)
```

**Verification:**
- Each file under 200 lines
- All search tests pass
- Public API unchanged

---

### Task 4.3: Split `adapters/sqlalchemy/search.py` (if >200 lines after merge)

**File:** `src/pypaginate/adapters/sqlalchemy/search.py`
**Technique:** Extract Class (`guru-refactor-moving`)

After merging `sql_search.py`, `conditions.py`, and `helpers.py` (Task 1.5.5),
this file may exceed 200 lines.

**Target structure (if needed):**
```
src/pypaginate/adapters/sqlalchemy/
├── search.py           # SQL search backend (~150 lines)
├── search_clauses.py   # SQL clause building (~150 lines)
```

**Verification:**
- Each file under 200 lines
- All tests pass

---

### Task 4.4: Split Remaining Large Files

**Files to split:**

| File | Lines | Target Structure |
|------|-------|-----------------|
| `services/search/options.py` | 298 | `config.py` + `validation.py` |
| `services/pagination.py` | 289 | Extract `options.py` |
| `adapters/sqlalchemy/pagination.py` | 287 | `sql_count.py` + `sql_fetch.py` |
| `services/search/parser.py` | 245 | Extract `tokens.py` |
| `adapters/sqlalchemy/snapshots.py` | 228 | Extract `serialization.py` |
| `adapters/memory/sorting.py` | 217 | Extract `null_handling.py` |
| `services/filtering/accessor.py` | 206 | Extract `path_resolver.py` |

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

**File:** `src/pypaginate/services/filtering/jsonlogic.py`
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

**File:** `src/pypaginate/services/search/options.py` (or `validation.py` after split)
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
| `adapters/memory/sorting.py` | 27, 174, 175, 185, 214 | Delete (changelog-style comments) |
| `services/filtering/jsonlogic.py` | 3–4, 99, 131, 150 | Translate docstrings to English |
| `services/search/__init__.py` | 21, 27, 29, 33 | Translate to English |
| `services/filtering/__init__.py` | 24, 36, 54, 65 | Translate to English |
| `adapters/sqlalchemy/search.py` | 85 | Translate to English |

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
- `types.py:121` — `other` in Protocol method (ignore)
- `types.py:132` — `other` in Protocol method (ignore)

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

**Current:** `services/filtering/operators/` has multi-level nesting

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
- Only known low-severity subprocess issues in `_cli.py`
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

- Reorganize into clean layered architecture (domain/, services/, adapters/)
- Move search logic to services/search/ (from filters/search/)
- Move predicate engine to services/filtering/ (from filters/predicates/)
- Decouple keyset pagination (protocol in domain, SQL impl in adapters)
- Eliminate 52 boolean parameters with enums
- Split 11 large files to under 200 lines each
- Reduce 11 long functions to under 12 lines each
- Add 3+ Protocol interfaces (PaginationBackend, FilterBackend, SortBackend, KeysetBackend)
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
- [ ] New directories created (`domain/`, `services/`, `adapters/`)
- [ ] Domain models moved (`pages.py`, `context.py` → `domain/models/`)
- [ ] Snapshots split (pure `PaginationSnapshot` → `domain/snapshots.py`, sqlakeyset-dependent → `adapters/sqlalchemy/snapshots.py`)
- [ ] Protocols extracted from `types.py` to `domain/protocols/` (3 files: `pagination.py`, `filtering.py`, `sorting.py`)
- [ ] Services layer moved (`services/pagination.py`, `services/search/`, `services/filtering/`)
- [ ] `factories.py` moved to root level (convenience wiring — imports from all layers)
- [ ] Known temporary violations documented (`strategies.py` → helpers, `pagination.py` → executor)
- [ ] SQLAlchemy adapters consolidated in `adapters/sqlalchemy/` (flat — no sub-packages)
- [ ] Memory adapters created in `adapters/memory/` (4 files: `pagination.py`, `filtering.py`, `search.py`, `sorting.py`)
- [ ] FastAPI integration consolidated (duplicate `PagedResponse` eliminated)
- [ ] `text/pipelines.py` renamed to `text/normalizers.py`
- [ ] Domain enums stub created (`domain/models/enums.py`)
- [ ] All imports updated to new locations
- [ ] Old directories cleaned up (`engines/`, `database/`, `query/`, `core/`, `integrations/`, `filters/`, `sorting/`)
- [ ] Public API exports updated in `__init__.py`
- [ ] `text/` stays (pure Python utility — NOT moved)

### Phase 2: Architecture
- [ ] `PaginationBackend` protocol added
- [ ] `FilterBackend` protocol added
- [ ] `SortBackend` protocol added
- [ ] `SqlPaginator` implements `PaginationBackend`
- [ ] `MemoryPaginator` implements `PaginationBackend`
- [ ] `Page[T]` is a Pydantic model
- [ ] `PagedResponse` removed

### Phase 3: SOLID & Patterns
- [ ] All enums created in `domain/models/enums.py`
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
