# Lint Workflow

Lint code using ruff.

## Commands

```bash
# Lint and auto-fix
uv run ruff check --fix .

# Lint only (no fixes)
uv run ruff check .

# Lint specific file
uv run ruff check src/pypaginate/paginator.py

# Show all rule violations (including fixable)
uv run ruff check --show-fixes .

# Lint with specific rules only
uv run ruff check --select E,W,F .
```

## Enabled Rule Sets

| Code | Name | Purpose |
|------|------|---------|
| E/W | pycodestyle | Style errors/warnings |
| F | pyflakes | Logic errors |
| I | isort | Import sorting |
| N | pep8-naming | Naming conventions |
| UP | pyupgrade | Python version upgrades |
| B | flake8-bugbear | Bug detection |
| S | bandit | Security issues |
| RUF | ruff-specific | Ruff-only rules |
| PERF | performance | Performance lints |
| ASYNC | async | Async best practices |

## Common Fixes

```bash
# Fix import sorting
uv run ruff check --select I --fix .

# Fix security issues
uv run ruff check --select S --fix .

# Fix all auto-fixable issues
uv run ruff check --fix --unsafe-fixes .
```
