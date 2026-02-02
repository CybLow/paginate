---
description: Review code for quality, best practices, and issues
agent: code-reviewer
subtask: true
---

Perform a comprehensive code review.

## What to Review

$ARGUMENTS

If no specific files mentioned, review:
1. Recently modified files: `git diff --name-only HEAD~5`
2. Or staged changes: `git diff --cached --name-only`
3. Or current file context

## Review Focus

### Code Quality
- [ ] Functions ≤12 lines
- [ ] No deep nesting (max 2 levels)
- [ ] No boolean parameters
- [ ] Max 4 parameters per function
- [ ] Clear naming conventions

### SOLID Principles
- [ ] Single Responsibility
- [ ] Open/Closed
- [ ] Liskov Substitution
- [ ] Interface Segregation
- [ ] Dependency Inversion

### Python Best Practices
- [ ] Type hints on public APIs
- [ ] Modern syntax (X | None, not Optional)
- [ ] Proper exception handling
- [ ] Guard clauses over nesting

### Security
- [ ] No hardcoded secrets
- [ ] Input validation
- [ ] Safe SQL queries
- [ ] Proper error messages

### Tests
- [ ] Tests exist for new code
- [ ] Edge cases covered
- [ ] Meaningful assertions

## Output

Provide a structured review with:
1. **Summary**: Overall assessment
2. **Strengths**: What's done well
3. **Issues**: Categorized by severity (Critical/Major/Minor)
4. **Recommendations**: Specific actionable improvements

Use the `code-smells` skill if you need to identify specific smells.
Use the `refactoring` skill if you need to suggest specific refactorings.
