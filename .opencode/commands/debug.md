---
description: Debug an error or investigate an issue
agent: debugger
subtask: true
---

Investigate and debug an issue.

## Problem

$ARGUMENTS

## Debugging Process

### 1. Understand the Issue
- What is the expected behavior?
- What is the actual behavior?
- Is it reproducible?
- When did it start?

### 2. Gather Information
```bash
# Recent changes
git log --oneline -10

# Changes to specific file
git log -p --follow -- path/to/file.py

# Who changed what
git blame path/to/file.py
```

### 3. Analyze Stack Trace
If an error/exception is provided:
- Identify the exception type
- Find the root frame (where it originated)
- Trace the call path
- Look for the actual cause vs. symptom

### 4. Form Hypotheses
Based on the error:
1. Most likely cause
2. Alternative causes
3. Tests to confirm/reject

### 5. Investigate Code
- Read the relevant code paths
- Check for common bug patterns:
  - Off-by-one errors
  - None/null handling
  - Type mismatches
  - Race conditions
  - Resource leaks

### 6. Suggest Fix
Provide:
- Root cause explanation
- Minimal fix with code
- Why the fix works
- Regression test suggestion

## Output Format

```markdown
## Bug Analysis

### Issue Summary
[Brief description]

### Root Cause
[The fundamental reason for the bug]

### Evidence
[Code references, logs, stack trace analysis]

### Suggested Fix
\`\`\`python
# Before
problematic_code()

# After  
fixed_code()
\`\`\`

### Regression Test
\`\`\`python
def test_<scenario>_<expected>():
    # Test that prevents this bug from recurring
    ...
\`\`\`
```

## If No Specific Error

If no error provided, analyze:
1. Recent test failures: `uv run pytest --lf`
2. Type errors: `uv run mypy src/`
3. Lint issues: `uv run ruff check .`
