## Summary

<!-- Provide a brief description of the changes in 1-2 sentences -->

## Motivation

<!-- Why is this change needed? What problem does it solve? -->

## Changes

<!-- List the main changes made in this PR -->

- 
- 
- 

## Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to change)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Tests (adding or updating tests)
- [ ] 🏗️ CI/CD (changes to build or CI configuration)
- [ ] 📦 Dependencies (updating dependencies)

## Testing

<!-- Describe how you tested your changes -->

### Test Commands Run

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src/
uv run pytest
```

### Manual Testing

<!-- Describe any manual testing performed -->

## Checklist

<!-- Ensure all items are checked before requesting review -->

- [ ] I have read the [CONTRIBUTING](../CONTRIBUTING.md) guidelines
- [ ] My code follows the project's coding standards (see [AGENTS.md](../AGENTS.md))
- [ ] I have run the quality checks (`uv run ruff format . && uv run ruff check . && uv run mypy src/`)
- [ ] I have added/updated tests for my changes
- [ ] All tests pass locally (`uv run pytest`)
- [ ] I have updated documentation if needed
- [ ] My changes generate no new warnings
- [ ] I have added type hints to new code

## Breaking Changes

<!-- If this is a breaking change, describe the impact and migration path -->

N/A

## Related Issues

<!-- Link related issues: Fixes #123, Closes #456, Related to #789 -->

## Screenshots

<!-- If applicable, add screenshots to help explain your changes -->

## Additional Notes

<!-- Any additional information for reviewers -->
