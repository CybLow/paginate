---
description: Clean up codebase - remove dead code, unused imports, fix formatting
agent: refactorer
subtask: true
---

Clean up the codebase by removing dead code, fixing imports, and applying formatting.

## Cleanup Tasks

### 1. Unused Imports
```bash
uv run ruff check --select F401 --fix .
```

### 2. Dead Code Detection
```bash
uv run vulture src/
```

### 3. Code Formatting
```bash
uv run ruff format .
```

### 4. Linting Fixes
```bash
uv run ruff check --fix .
```

### 5. Sort Imports
```bash
uv run ruff check --select I --fix .
```

## Analysis

### Dead Code Categories

| Type | Example | Action |
|------|---------|--------|
| Unused functions | `def old_helper():` never called | Remove |
| Unused classes | `class LegacyHandler:` never instantiated | Remove |
| Unused variables | `x = compute()` but x never used | Remove |
| Unreachable code | Code after `return` | Remove |
| Commented code | `# old_implementation()` | Remove |

### Import Issues

| Issue | Example | Fix |
|-------|---------|-----|
| Unused import | `import os` (not used) | Remove |
| Duplicate import | Same import twice | Remove duplicate |
| Wrong order | stdlib after third-party | Sort |
| Star import | `from x import *` | Explicit imports |

## Cleanup Report

```markdown
## Cleanup Report

### Summary
- Unused imports removed: X
- Dead code lines removed: X
- Files formatted: X
- Lint issues fixed: X

### Changes Made

#### Removed Dead Code
- `src/old_module.py`: Removed `unused_function()`
- `src/utils.py`: Removed lines 45-52 (unreachable)

#### Fixed Imports
- `src/main.py`: Removed unused `import os`
- `src/api.py`: Sorted imports

#### Formatting
- X files reformatted

### Remaining Issues
[Any issues that need manual review]
```

## Arguments

$ARGUMENTS

Options:
- `--dry-run`: Show what would be cleaned without making changes
- `--imports`: Only clean up imports
- `--dead-code`: Only remove dead code
- `--format`: Only format code

## Safety

1. Run tests before cleanup: `uv run pytest`
2. Make changes
3. Run tests after cleanup: `uv run pytest`
4. If tests fail, revert: `git checkout .`
