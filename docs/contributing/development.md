# Development Setup

Everything you need to set up, build, and maintain pypaginate locally.

## Prerequisites

- **Python 3.11+** (3.14 recommended for best performance)
- **[uv](https://docs.astral.sh/uv/)** -- fast Python package manager
- **Git** with conventional commits

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

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
uv sync --all-extras --dev
```

This installs:

- **Core:** pydantic
- **Optional extras:** sqlalchemy, rapidfuzz, fastapi, msgspec, google-re2
- **Dev tools:** pytest, mypy, ruff, hypothesis, pytest-benchmark
- **Docs:** sphinx, myst-parser

### 3. Pre-commit Hooks (Optional)

```bash
uv run pre-commit install
```

### 4. Verify Setup

```bash
uv run ruff check src/                            # Lint
uv run mypy src/                                   # Type check
uv run pytest tests/ --ignore=tests/perf -q        # Tests
```

---

## Project Structure

```
src/pypaginate/
├── __init__.py          # Public API exports
├── _dispatch.py         # Universal paginate() entry point
│
├── domain/              # Pure models, specs, protocols, exceptions
│   ├── enums.py         # SortDirection, FilterLogic, FuzzyMode, etc.
│   ├── exceptions.py    # PaginationError hierarchy
│   ├── pages.py         # OffsetPage, CursorPage
│   ├── params.py        # OffsetParams, CursorParams
│   ├── protocols.py     # Backend protocol definitions
│   └── specs.py         # FilterSpec, SortSpec, SearchSpec
│
├── engine/              # Core orchestration (backend-agnostic)
│   ├── paginator.py     # Paginator, AsyncPaginator
│   ├── pipeline.py      # SyncPipeline, AsyncPipeline
│   └── cursor.py        # AsyncCursorPaginator
│
├── filtering/           # Filter engine + operators
├── sorting/             # Sort engine + null-aware keys
├── search/              # Search engine + fuzzy matching
├── text/                # Text normalization (LRU cached)
│
└── adapters/            # Backend implementations
    ├── memory/          # In-memory (list, tuple)
    ├── sqlalchemy/      # SQLAlchemy ORM (sync + async)
    └── fastapi/         # FastAPI dependency injection

tests/
├── unit/                # Per-module unit tests
├── integration/         # Cross-module + database
├── e2e/                 # Full workflows with FastAPI
├── property/            # Hypothesis invariants
├── architecture/        # Code quality enforcement
└── perf/                # Performance benchmarks
```

---

## Daily Workflow

### While Coding

```bash
uv run ruff format .                # Format
uv run ruff check src/              # Lint
uv run mypy src/pypaginate/search/  # Type check what you changed
uv run pytest tests/unit/search/ -v # Run related tests
```

### Before Committing

```bash
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest tests/ --ignore=tests/perf -q
```

### Before PR

```bash
# Full test suite including integration and e2e
uv run pytest tests/ --ignore=tests/perf -v

# If touching hot paths, run benchmarks
uv run pytest tests/perf/test_comparison.py --benchmark-enable --benchmark-only -q
```

---

## Optional Extras

| Extra | Packages | Purpose |
|---|---|---|
| `pypaginate[sqlalchemy]` | SQLAlchemy | ORM pagination |
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
4. Enable mypy integration
5. Set pytest as test runner

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

## Common Tasks

### Adding a New Filter Operator

In-memory operators live in the native `paginate-core` Rust engine, so a new
operator spans both repos:

1. Add the operator to the engine crate (`crates/core/src/filter/`) in the
   `paginate-core` repo and rebuild (`maturin develop --release`)
2. Add SA mapping in `src/pypaginate/adapters/sqlalchemy/filters.py`
3. Add the literal value to the `FilterOperator` type in `src/pypaginate/domain/specs.py`
4. Add tests in `tests/unit/filtering/`

### Adding a New Backend Adapter

1. Create `src/pypaginate/adapters/mybackend/` with `backend.py`
2. Implement `PaginationBackend[T]` protocol (or `SyncPaginationBackend[T]`)
3. Add `__slots__` to all new classes
4. Optionally implement `FilterBackend`, `SortBackend`, `SearchBackend`
5. Add tests in `tests/unit/adapters/mybackend/`

### Optimizing a Hot Path

1. Benchmark first -- save baseline with `--benchmark-save=before`
2. Profile -- identify the actual bottleneck
3. Apply compile-once patterns, LRU cache, or string methods over regex
4. Verify all tests pass and benchmark shows improvement

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ImportError` on tests | `uv sync --all-extras --dev` |
| mypy missing stubs | `uv run mypy src/ --install-types` |
| Flaky benchmarks | Close background apps, use `--benchmark-min-rounds=10` |
| Architecture test fails | File exceeds 250 code lines -- extract a helper module |
| Pre-commit hook fails | `uv run ruff format . && uv run ruff check --fix .` |

---

## Next Steps

- [Architecture Guide](architecture.md) -- understand the codebase design
- [Testing Guide](testing.md) -- write and run tests
- [Code Style](code-style.md) -- coding standards and patterns
