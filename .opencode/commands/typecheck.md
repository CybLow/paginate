# Type Check Workflow

Type check code using mypy.

## Commands

```bash
# Type check source code
uv run mypy src/

# Type check with verbose output
uv run mypy src/ --verbose

# Type check specific file
uv run mypy src/pypaginate/paginator.py

# Type check tests too
uv run mypy src/ tests/

# Show error codes
uv run mypy src/ --show-error-codes

# Generate HTML report
uv run mypy src/ --html-report mypy-report
```

## Configuration

Strict mode enabled in `pyproject.toml`:
- `strict = true`
- `disallow_untyped_defs = true`
- `disallow_any_generics = true`
- `no_implicit_optional = true`

## Common Error Fixes

| Error Code | Meaning | Fix |
|------------|---------|-----|
| `[arg-type]` | Wrong argument type | Check parameter types |
| `[return-value]` | Wrong return type | Update return annotation |
| `[assignment]` | Incompatible assignment | Add proper typing |
| `[name-defined]` | Undefined name | Import or define |
| `[no-untyped-def]` | Missing type hints | Add annotations |

## Ignoring Errors

```python
# Ignore specific line
result = some_call()  # type: ignore[return-value]

# Ignore in pyproject.toml for specific modules
[[tool.mypy.overrides]]
module = ["problematic_module.*"]
ignore_errors = true
```
