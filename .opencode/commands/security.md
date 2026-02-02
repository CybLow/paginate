# Security Scan Workflow

Scan for security vulnerabilities using bandit and pip-audit.

## Commands

### Code Analysis (bandit)

```bash
# Scan source code
uv run bandit -r src/

# Scan with all tests
uv run bandit -r src/ -ll

# Generate JSON report
uv run bandit -r src/ -f json -o bandit-report.json

# Generate HTML report
uv run bandit -r src/ -f html -o bandit-report.html

# Skip specific checks
uv run bandit -r src/ --skip B101,B102

# Show only high severity
uv run bandit -r src/ -ll --severity-level high

# Scan specific file
uv run bandit src/pypaginate/auth.py
```

### Dependency Vulnerabilities (pip-audit)

```bash
# Scan all dependencies
uv run pip-audit

# Output as JSON
uv run pip-audit --format json

# Strict mode (fail on any vulnerability)
uv run pip-audit --strict

# Show fix versions
uv run pip-audit --fix --dry-run
```

## Common Issues

| Code | Issue | Severity |
|------|-------|----------|
| B101 | assert_used | Low |
| B105 | hardcoded_password_string | Medium |
| B106 | hardcoded_password_funcarg | Medium |
| B107 | hardcoded_password_default | Medium |
| B301 | pickle | Medium |
| B303 | md5 | Medium |
| B307 | eval | High |
| B602 | subprocess_popen_with_shell | High |
| B608 | sql_injection | High |

## Configuration

Configured in `pyproject.toml`:

```toml
[tool.bandit]
targets = ["src"]
exclude_dirs = ["tests", "docs", "examples"]
skips = ["B101"]  # Skip assert_used
```

## Inline Ignores

```python
# nosec B105 - This is a test constant, not a real password
TEST_TOKEN = "test-token-value"  # nosec
```

## CI Integration

Security scans run in CI. Failed scans block merge for high-severity issues.
