---
description: Suggest and apply code refactoring improvements
agent: refactorer
subtask: true
---

Analyze code and suggest refactoring improvements.

## Target

$ARGUMENTS

If no specific target:
1. Analyze recently modified files
2. Look for code that exceeds size limits
3. Find code smells and violations

## Refactoring Priorities

### 1. Size Violations (Fix First)
- Functions >12 lines → Extract Method
- Files >200 lines → Extract Class/Module
- Nesting >2 levels → Guard Clauses
- Parameters >4 → Parameter Object

### 2. Code Smells
- Long Method
- Large Class
- Feature Envy
- Data Clumps
- Primitive Obsession
- Duplicate Code

### 3. SOLID Violations
- God Class → Single Responsibility
- Rigid Design → Open/Closed
- Broken Hierarchy → Liskov Substitution
- Fat Interface → Interface Segregation
- Concrete Dependencies → Dependency Inversion

## Workflow

1. **Analyze**: Identify issues
2. **Prioritize**: Most impactful first
3. **Plan**: List refactorings
4. **Test**: Ensure tests pass before starting
5. **Refactor**: One change at a time
6. **Verify**: Run tests after each change
7. **Format**: Run ruff format
8. **Check**: Run mypy

## Output Options

### Analysis Only (default for `subtask: true`)
Provide a report with:
- Issues found
- Suggested refactorings
- Priority order
- Estimated effort

### Apply Refactorings
If the user says "apply" or "fix", make the changes:
1. Run tests first
2. Make changes
3. Run tests again
4. Format code
5. Report what was done

## Skills

Load `refactoring` skill for the full catalog of techniques.
Load `code-smells` skill to identify what needs fixing.
