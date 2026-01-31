# Internal Development Notes

This document contains internal notes for core developers of pypaginate. It covers project audits, publishing procedures, and internal roadmap details.

## Publishing to PyPI

pypaginate uses automated publishing via GitHub Actions. Manual publishing should rarely be needed.

### Automated Publishing (Recommended)

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create and push a git tag:**
   ```bash
   git tag v0.x.x
   git push origin v0.x.x
   ```
4. **Create a GitHub Release** from the tag
5. The `.github/workflows/publish.yml` workflow will automatically:
   - Build the package
   - Publish to PyPI

### Manual Publishing (If Needed)

```bash
# Build the package
uv build

# Verify the distribution
uv run twine check dist/*

# Publish to Test PyPI first
uv publish --index testpypi

# Publish to PyPI
uv publish
```

### PyPI Credentials

- Store your PyPI API token in GitHub Secrets as `PYPI_API_TOKEN`
- For local publishing, configure `~/.pypirc` with your token

---

## Project Audit Summary

### Feature Coverage vs Competitors

| Feature | fastapi-pagination | fastapi-filters | pypaginate |
|---------|-------------------|-----------------|------------|
| Offset pagination | Yes | - | Yes |
| Cursor pagination | Yes | - | Partial |
| Multiple formats | Yes | - | Planned v0.3.0 |
| FilterDepends | - | Yes | Planned v0.2.0 |
| Declarative filters | - | Yes | Planned v0.2.0 |
| Auto Relations/JOINs | - | Yes | Planned v0.2.0 |
| Full-text search | - | Basic | Advanced |
| Fuzzy matching | - | No | Yes |
| JSON Logic | - | No | Yes |

### pypaginate Strengths

1. **Architecture** - Clean, modular design with separation of concerns
2. **Type Safety** - Full mypy --strict compatibility
3. **Advanced Search** - Fuzzy matching with RapidFuzz
4. **JSON Logic** - Powerful filter expressions

### Areas for Improvement (Roadmap)

1. **v0.2.0** - Declarative FastAPI integration
   - FilterModel and FilterDepends
   - OrderingDepends
   - Auto SQL WHERE generation
   - Relationship filters with auto-join

2. **v0.3.0** - Pagination formats
   - LimitOffsetPage, CursorPage
   - HATEOAS link generation
   - Custom response models

3. **v0.4.0** - Advanced features
   - Additional SQL operators
   - Count query caching
   - Django/Tortoise ORM support

---

## Code Quality Standards

### Required Checks

All PRs must pass:

```bash
# Format check
uv run ruff format --check src tests

# Lint check
uv run ruff check src tests

# Type check
uv run mypy src

# Tests
uv run pytest
```

### Coverage Requirements

- Minimum 80% code coverage (configured in `pyproject.toml`)
- All new features must include tests
- Integration tests for FastAPI endpoints

---

## Release Checklist

Before each release:

- [ ] All tests pass
- [ ] Code coverage meets threshold
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Documentation updated
- [ ] Git tag created
- [ ] GitHub Release created

---

## Dependencies

### Core Dependencies

The core package has no required dependencies. All features are optional:

| Extra | Packages | Purpose |
|-------|----------|---------|
| `sqlalchemy` | SQLAlchemy, sqlakeyset | Database pagination |
| `search` | RapidFuzz, pyparsing | Fuzzy text search |
| `filters` | json-logic-qubit, jmespath | Advanced filtering |
| `text` | text-unidecode | Text normalization |
| `fastapi` | FastAPI | Framework integration |
| `all` | All of the above | Full feature set |

### Development Dependencies

Managed via UV dependency groups in `pyproject.toml`:

- `dev` - All development tools
- `test` - pytest, coverage, etc.
- `lint` - ruff, pre-commit
- `type` - mypy
- `security` - bandit
- `build` - build, twine
- `docs` - mkdocs, mkdocstrings

---

## Maintainer Notes

### Branch Strategy

- `main` - Stable releases only
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `release/*` - Release preparation

### Review Guidelines

1. All PRs require at least one approval
2. CI must pass before merge
3. Squash commits on merge
4. Use conventional commit messages
