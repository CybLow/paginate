# Contributing to pypaginate

Thank you for your interest in contributing. This guide covers everything you need
to get started -- from setting up your environment to submitting a pull request.

## Quick Links

| Guide | Description |
|---|---|
| [Development Setup](development.md) | Environment setup with uv |
| [Code Style](code-style.md) | Coding standards and hard limits |
| [Testing Guide](testing.md) | Test categories, running tests, coverage |
| [Architecture](architecture.md) | Hexagonal architecture and layer rules |

## Ways to Contribute

### Report Bugs

[Open an issue](https://github.com/CybLow/paginate/issues) with:

- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and pypaginate version

### Suggest Features

Open an issue with:

- Description of the feature and its use case
- Example code showing the desired API
- How it fits into the existing architecture

### Submit Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make changes following our [code style](code-style.md)
4. Run quality checks: `uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest`
5. Commit using [Conventional Commits](#commit-message-convention)
6. Push and open a pull request

## Prerequisites

- **Python 3.11+** (3.14 recommended)
- **[uv](https://docs.astral.sh/uv/)** -- fast Python package manager
- **Git** with conventional commit tooling

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Setup

```bash
git clone https://github.com/YOUR_USERNAME/pypaginate.git
cd pypaginate
git remote add upstream https://github.com/CybLow/paginate.git
uv sync --all-extras --dev
uv run pytest tests/ --ignore=tests/perf -q
```

## Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout main && git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** -- keep functions <=15 lines, files <=250 lines (code only), add type hints

3. **Run quality checks** before every commit:
   ```bash
   uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest
   ```

4. **Commit atomically** -- one logical change per commit:
   ```bash
   git commit -m "feat(search): add weighted field scoring"
   ```

5. **Push and create PR**:
   ```bash
   git push -u origin feature/your-feature-name
   ```

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

| Type | Purpose | Example |
|---|---|---|
| `feat` | New feature | `feat(filters): add regex operator` |
| `fix` | Bug fix | `fix(sort): handle all-null columns` |
| `docs` | Documentation | `docs(api): update filter examples` |
| `refactor` | Code restructuring | `refactor(engine): extract pipeline class` |
| `test` | Test changes | `test(search): add fuzzy matching coverage` |
| `perf` | Performance | `perf(filter): compile predicates once` |
| `chore` | Maintenance | `chore: update dependencies` |
| `style` | Formatting | `style: apply ruff formatting` |

**Rules:**

- Imperative mood: "add" not "added" or "adds"
- Lowercase first letter, no period at end
- Max 50 characters for the subject line

## Pull Request Checklist

- [ ] Code follows project [code style](code-style.md)
- [ ] All quality checks pass
- [ ] New code has tests
- [ ] Type hints on all public APIs
- [ ] Documentation updated if applicable
- [ ] Commit messages follow convention

## Code of Conduct

Be respectful and inclusive. We follow the
[Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## Getting Help

- **Questions** -- Open a GitHub Discussion
- **Bugs** -- Open a GitHub Issue
