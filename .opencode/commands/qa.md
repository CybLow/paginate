# QA Workflow

Run full quality assurance checks for pypaginate.

## Commands

Execute all checks in sequence:

```bash
# 1. Format code
uv run ruff format .

# 2. Lint and auto-fix
uv run ruff check --fix .

# 3. Type check
uv run mypy src/

# 4. Run tests with coverage
uv run pytest --cov=src/pypaginate --cov-report=term-missing

# 5. Security scan (optional)
uv run bandit -r src/
```

## One-liner

```bash
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest --cov=src/pypaginate
```

## Success Criteria

- All formatters pass without changes needed
- No linting errors remain
- Type checker reports no errors
- All tests pass
- Coverage >= 85%
