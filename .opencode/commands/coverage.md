---
description: Analyze test coverage and suggest improvements
agent: test-writer
subtask: true
---

Analyze test coverage and suggest improvements.

## Target

$ARGUMENTS

## Coverage Analysis

### 1. Get Current Coverage
```bash
uv run pytest --cov=src/pypaginate --cov-report=term-missing
```

### 2. Identify Gaps
Look for:
- Uncovered lines
- Uncovered branches
- Missing edge cases
- Untested error paths

### 3. Coverage Requirements
| Level | Threshold | Description |
|-------|-----------|-------------|
| Minimum | 85% | CI gate, must pass |
| Target | 90% | Good coverage |
| Critical | 100% | Core functionality |

## Coverage Report Format

```markdown
## Coverage Analysis

### Current Status
- **Overall**: XX%
- **Core modules**: XX%
- **Integrations**: XX%

### Uncovered Areas

#### High Priority (Core functionality)
| File | Lines | Missing | Priority |
|------|-------|---------|----------|
| paginator.py | 45-52 | Error handling | High |

#### Medium Priority
[...]

#### Low Priority
[...]

### Suggested Tests

#### 1. [Test Name]
```python
def test_<scenario>():
    # Covers lines X-Y in file.py
    ...
```

#### 2. [Test Name]
[...]

### Coverage Improvement Plan
1. Add X tests → +5% coverage
2. Add Y tests → +3% coverage
3. Total expected: XX%
```

## Options

### `--generate`
Generate the missing tests automatically:
1. Analyze uncovered code
2. Create test file if needed
3. Write test functions
4. Run to verify

### `--report`
Just analyze and report, don't generate tests.

## Skills

Load `testing` skill for testing patterns and best practices.
