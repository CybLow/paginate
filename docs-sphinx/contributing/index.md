# Contributing to pypaginate

Thank you for your interest in contributing to pypaginate! This guide will help you get started.

## Quick Links

| Guide | Description |
|-------|-------------|
| [Development Setup](development.md) | Set up your development environment |
| [Testing Guide](testing.md) | Write and run tests |
| [Code Style](code-style.md) | Coding standards and conventions |
| [Architecture](architecture.md) | Understanding the codebase |
| [Roadmap](roadmap.md) | Future plans and priorities |

## Ways to Contribute

### Report Bugs

Found a bug? Please [open an issue](https://github.com/CybLow/pypaginate/issues) with:

- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and pypaginate version

### Suggest Features

Have an idea? Open an issue with:

- Description of the feature
- Use case and benefits
- Example code if applicable

### Submit Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks
5. Submit a pull request

## Getting Started

### Prerequisites

- **Python 3.11+**
- **[UV](https://docs.astral.sh/uv/)** - Fast Python package manager

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pypaginate.git
cd pypaginate

# Install dependencies
uv sync

# Run tests
uv run pytest
```

### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write clean, typed Python code
   - Follow existing patterns
   - Add tests for new features

3. **Run quality checks**
   ```bash
   uv run pypaginate qa
   ```

4. **Commit with conventional message**
   ```bash
   git commit -m "feat: add new feature"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Description |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `style:` | Code style (formatting) |
| `refactor:` | Code refactor |
| `test:` | Adding/updating tests |
| `chore:` | Maintenance tasks |

## Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Quality checks pass (`uv run pypaginate qa`)
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages follow convention

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: Join our community discussions

---

Thank you for contributing to pypaginate!
