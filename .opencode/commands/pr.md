---
description: Create a GitHub Pull Request with proper description
agent: build
---

Create a GitHub Pull Request for the current branch.

## Instructions

1. Check current branch: `git branch --show-current`
2. Check if branch is pushed: `git status`
3. Get commits since main: `git log main..HEAD --oneline`
4. Get full diff: `git diff main...HEAD`
5. Analyze all changes to write comprehensive PR description

## PR Title Format

Follow conventional commit format:
```
<type>(<scope>): <description>
```

## PR Description Template

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Change 1
- Change 2
- Change 3

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)

## How to Test
1. Step 1
2. Step 2
3. Expected result

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass
- [ ] I have updated the documentation accordingly
- [ ] Type hints are added for public APIs

## Related Issues
Closes #XXX
```

## Commands

```bash
# Push branch if needed
git push -u origin $(git branch --show-current)

# Create PR
gh pr create --title "type(scope): description" --body "..."
```

## Arguments

$ARGUMENTS

If arguments provided, use them to customize the PR.
Otherwise, analyze the changes and create an appropriate PR.
