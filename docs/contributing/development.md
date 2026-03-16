# Developer Experience (DX) Guide

> Everything you need to set up, contribute to, and maintain pypaginate.

---

## Prerequisites

- **Python 3.11+** (3.14 recommended for best performance)
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **Git** with conventional commits

---

## Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/pypaginate.git
cd pypaginate
git remote add upstream https://github.com/CybLow/pypaginate.git
```

### 2. Install Dependencies

```bash
# Install ALL dependencies (core + dev + all optional extras)
uv sync --all-extras --dev

# This installs:
# - pydantic (core)
# - sqlalchemy, rapidfuzz, fastapi, msgspec, google-re2 (optional extras)
# - pytest, mypy, ruff, hypothesis, pytest-benchmark (dev tools)
# - sphinx, myst-parser (docs)
```

### 3. Pre-commit Hooks (Optional)

```bash
uv run pre-commit install
```

### 4. Verify Setup

```bash
uv run ruff check src/                            # Lint → "All checks passed!"
uv run mypy src/                                   # Types → "no issues found"
uv run pytest tests/ --ignore=tests/perf -q        # Tests → "714 passed"
```

---

## Daily Workflow

### While Coding

```bash
# Format on save (configure IDE) or manually
uv run ruff format .

# Quick lint
uv run ruff check src/

# Type check what you changed
uv run mypy src/pypaginate/filtering/

# Run related tests
uv run pytest tests/unit/filtering/ -v
```

### Before Committing

```bash
# Full quality gate (MUST pass before any PR)
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest tests/ --ignore=tests/perf -q
```

### Before PR

```bash
# Run everything including integration + e2e
uv run pytest tests/ --ignore=tests/perf -v

# If touching hot paths, run benchmarks
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-only -q
```

---

## Project Structure

```
pypaginate/
├── src/pypaginate/          # Source code (51 files, ~4,400 lines)
│   ├── __init__.py          # Public API (23 exports)
│   ├── _dispatch.py         # Universal paginate() entry point
│   ├── domain/              # Pure models, specs, protocols, exceptions
│   ├── engine/              # Core orchestration (paginator, pipeline, cursor)
│   ├── filtering/           # Filter engine + 17 operators + LIKE + regex
│   ├── sorting/             # Sort engine + null-aware keys
│   ├── search/              # Search engine + fuzzy matching + tokenizer
│   ├── text/                # Text normalization (LRU cached, ASCII fast path)
│   └── adapters/            # Backend implementations
│       ├── memory/          # In-memory (list, tuple)
│       ├── sqlalchemy/      # SQLAlchemy ORM (sync + async)
│       └── fastapi/         # FastAPI dependency injection
│
├── tests/                   # Test suite (74 files, 714 tests + ~150 benchmarks)
│   ├── unit/                # Per-module unit tests (~694 tests)
│   ├── integration/         # Cross-module + database (8 tests)
│   ├── e2e/                 # Full workflows with FastAPI (6 tests)
│   ├── property/            # Hypothesis invariants (3 tests)
│   ├── architecture/        # Code quality enforcement (3 tests)
│   └── perf/                # Performance benchmarks (~150 functions)
│
├── docs/                    # Documentation
├── CLAUDE.md                # AI agent instructions
└── pyproject.toml           # Project config
```

---

## Key Conventions

### Code Standards (enforced by CI + architecture tests)

| Rule | Limit | How Enforced |
|---|---|---|
| File size | ≤ 200 lines of code | `tests/architecture/test_file_limits.py` |
| Function size | ≤ 12 lines | Code review |
| Nesting depth | ≤ 2 levels | Guard clauses pattern |
| `__slots__` | On ALL classes | Code review |
| Type hints | On ALL public APIs | `mypy --strict` |
| No boolean params | Use enums | Code review |
| No circular imports | `TYPE_CHECKING` guard | `tests/architecture/test_imports.py` |
| Protocol compliance | All backends | `tests/architecture/test_protocols.py` |

### Performance Standards

| Pattern | When to Use |
|---|---|
| **Compile-once, apply-N** | Specs, accessors, predicates — anything static per query |
| **LRU cache** | Pure functions called repeatedly with same args |
| **String methods over regex** | Simple patterns (`%value%`, `value%`, `%value`) |
| **`__slots__`** | Every class — prevents `__dict__`, faster attr access |
| **Partition strategy** | Null handling in sort — separate nulls, sort non-nulls directly |
| **Optional acceleration** | msgspec, rapidfuzz, re2 — try/except import pattern |

### Git Conventions

**Branch**: `<type>/<description>` (e.g., `perf/compile-filter-predicates`)

**Commit**: Conventional Commits
```
feat(search): add fuzzy matching with rapidfuzz
fix(sort): handle all-null columns correctly
perf(filter): replace fnmatch with string methods for LIKE
refactor(accessor): extract compile_accessor from get_value
test(search): add multi-token matching coverage
docs(arch): update architecture diagram for v0.2.0
```

---

## Common Tasks

### Adding a New Filter Operator

1. Add operator class in `src/pypaginate/filtering/operators.py` (≤ 6 lines)
2. Register in `_BUILTINS` dict in `src/pypaginate/filtering/registry.py`
3. Add SA mapping in `src/pypaginate/adapters/sqlalchemy/filters.py`
4. Add literal value to `FilterOperator` type in `src/pypaginate/domain/specs.py`
5. Add tests in `tests/unit/filtering/test_operators.py`
6. Verify: `uv run pytest tests/unit/filtering/ -v`

### Adding a New Backend Adapter

1. Create `src/pypaginate/adapters/mybackend/` with `backend.py`
2. Implement `PaginationBackend[T]` protocol (or `SyncPaginationBackend[T]`)
3. Add `__slots__` to all new classes
4. Optionally implement `FilterBackend`, `SortBackend`, `SearchBackend`
5. Add tests in `tests/unit/adapters/mybackend/`
6. Add integration test in `tests/integration/`

### Optimizing a Hot Path

1. **Benchmark first**: save baseline with `--benchmark-save=before`
2. **Profile**: identify actual bottleneck (don't guess)
3. **Apply**: compile-once patterns, LRU cache, string methods over regex
4. **Verify**: all 714 tests pass + benchmark improvement
5. **Document**: add entry to `docs/OPTIMIZATION_AUDIT.md`

---

## Optional Extras

| Extra | Package | Purpose |
|---|---|---|
| `pypaginate[sqlalchemy]` | SQLAlchemy + sqlakeyset | ORM pagination |
| `pypaginate[search]` | rapidfuzz | Fast fuzzy string matching |
| `pypaginate[fastapi]` | FastAPI | Dependency injection helpers |
| `pypaginate[fast]` | msgspec | Near-zero page construction |
| `pypaginate[security]` | google-re2 | ReDoS-safe regex filtering |
| `pypaginate[all]` | Everything | Full install |

```bash
uv add pypaginate[all]          # Install with everything
uv add pypaginate[sqlalchemy]   # Install with SQLAlchemy only
```

---

## IDE Setup

### PyCharm / IntelliJ

1. Set interpreter to `.venv/bin/python`
2. Install Ruff plugin for real-time linting
3. Set line length to 100 (Editor > Code Style > Python)
4. Enable mypy integration (Settings > Python > mypy)
5. Set pytest as test runner (Settings > Python > Testing)

### VS Code

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "python.analysis.typeCheckingMode": "strict",
    "editor.rulers": [100]
}
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ImportError` on tests | `uv sync --all-extras --dev` |
| mypy missing stubs | `uv run mypy src/ --install-types` |
| Flaky benchmarks | Close apps, use `--benchmark-min-rounds=10` |
| Architecture test fails | File > 200 lines — extract a helper module |
| Pre-commit hook fails | `uv run ruff format . && uv run ruff check --fix .` |

---

## Next Steps

- [Architecture Guide](architecture.md) — understand the codebase design
- [Testing Guide](testing.md) — write and run tests
- [Code Style](code-style.md) — coding standards and patterns
- [Optimization Audit](../OPTIMIZATION_AUDIT.md) — performance history
