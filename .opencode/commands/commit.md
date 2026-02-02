---
description: Create a conventional commit with proper formatting
agent: build
---

Create a git commit following Conventional Commits format.

## Instructions

1. First, run `git status` to see what files are staged/unstaged
2. Run `git diff --cached` to see staged changes (or `git diff` for unstaged)
3. Analyze the changes and determine:
   - **type**: feat, fix, docs, style, refactor, test, perf, chore, ci, build
   - **scope**: affected module (optional)
   - **subject**: imperative, lowercase, no period, max 50 chars
   - **body**: explain what and why (optional)

## Commit Types

| Type | When to Use |
|------|------------|
| `feat` | New feature for the user |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring, no behavior change |
| `test` | Adding or updating tests |
| `perf` | Performance improvement |
| `chore` | Maintenance, deps update |
| `ci` | CI/CD changes |
| `build` | Build system changes |

## Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer: Closes #123]
```

## Examples

```bash
git commit -m "feat(paginator): add keyset pagination support"
git commit -m "fix(filters): handle None values in comparison"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(sorting): extract comparison logic to separate function"
```

If there are changes to commit, stage appropriate files and create the commit.
If there are no changes, inform the user.

$ARGUMENTS
