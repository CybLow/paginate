# AGENTS.md - Development Guide

> **For AI Agents, Contributors, and Developers**
>
> This document defines the coding standards and best practices for **pypaginate**.

---

## Quick Start

**For AI Agents**: Start with [AI Agent Guidance](#ai-agent-guidance), then [Quick Reference](#quick-reference).

**Commands available**:

| Command | Description | Agent |
|---------|-------------|-------|
| `/qa` | Full quality assurance workflow | build |
| `/test` | Test commands and markers | build |
| `/format` | Code formatting with ruff | build |
| `/lint` | Linting with ruff | build |
| `/typecheck` | Type checking with mypy | build |
| `/benchmark` | Performance benchmarks | build |
| `/docs` | Documentation with MkDocs | build |
| `/security` | Security scanning with bandit | build |
| `/commit` | Create conventional commit | build |
| `/pr` | Create GitHub Pull Request | build |
| `/review` | Code review (quality check) | code-reviewer |
| `/refactor` | Suggest refactoring improvements | refactorer |
| `/debug <error>` | Debug an issue or error | debugger |
| `/coverage` | Analyze test coverage | test-writer |
| `/audit` | Security audit | security-auditor |
| `/deps` | Check dependencies | build |
| `/clean` | Clean up codebase | refactorer |
| `/architect` | Architecture decisions and design | architect |
| `/e2e` | End-to-end testing with Playwright | e2e-tester |
| `/profile` | Performance profiling and analysis | performance-profiler |

**Agents available** (use @agent-name or via commands):

| Agent | Mode | Purpose |
|-------|------|---------|
| `build` | primary | Full development work (default) |
| `plan` | primary | Analysis without changes (Tab to switch) |
| `code-reviewer` | subagent | Code quality review |
| `docs-writer` | subagent | Documentation writing |
| `debugger` | subagent | Bug investigation |
| `refactorer` | subagent | Code refactoring |
| `test-writer` | subagent | Test generation |
| `security-auditor` | subagent | Security analysis |
| `architect` | subagent | Architecture decisions and design |
| `e2e-tester` | subagent | End-to-end testing with Playwright |
| `performance-profiler` | subagent | Performance analysis and profiling |

**Tools available** (custom project tools):

| Tool | Description |
|------|-------------|
| `complexity` | Calculate cyclomatic complexity (radon) |
| `coverage-report` | Get test coverage for file |
| `deps-check` | Check outdated/vulnerable dependencies |
| `imports-check` | Find unused imports (ruff) |
| `dead-code` | Find unreachable code (vulture) |
| `benchmark` | Run performance benchmarks (pytest-benchmark) |
| `profile_cpu` | CPU profiling with py-spy flame graphs |
| `profile_memory` | Memory profiling with memray |
| `profile_scalene` | Full profiling with Scalene (CPU+memory+GPU) |

**MCP Servers** (external tools):

| Server | Purpose |
|--------|---------|
| `context7` | Search documentation (use context7) |
| `gh_grep` | Search GitHub code examples (use gh_grep) |
| `supermemory` | Long-term memory across sessions |
| `github` | GitHub issues, PRs, CI status |
| `postgres` | Database schema inspection and queries |
| `playwright` | Browser automation for E2E testing |
| `docker` | Sandboxed code execution |

**Skills available** (use when detailed guidance needed):

| Category | Skills |
|----------|--------|
| Patterns | `guru-patterns-creational`, `guru-patterns-structural`, `guru-patterns-behavioral`, `guru-smells` |
| Refactoring | `guru-refactor-methods`, `guru-refactor-moving`, `guru-refactor-data`, `guru-refactor-conditionals`, `guru-refactor-calls`, `guru-refactor-generalization` |
| Architecture | `arch-principles`, `arch-ddd`, `arch-cqrs-es`, `arch-hexagonal`, `arch-microservices` |
| Security | `sec-basics`, `sec-owasp`, `sec-ops`, `sec-api` |
| Testing | `test-standards`, `test-ops`, `test-advanced`, `test-load`, `test-chaos`, `test-data` |
| API Design | `api-rest`, `api-graphql`, `api-grpc`, `api-gateway`, `api-auth`, `api-lifecycle` |
| Performance | `perf-core`, `perf-ops`, `perf-slo`, `perf-apm`, `perf-profiling`, `perf-database` |
| Other | `type-hints` |

---

## Table of Contents

- [Core Principles](#core-principles)
- [Size Limits](#size-limits)
- [Naming Conventions](#naming-conventions)
- [Type Hints](#type-hints)
- [Git Conventions](#git-conventions)
- [Architecture](#architecture)
- [AI Agent Guidance](#ai-agent-guidance)
- [Quick Reference](#quick-reference)

---

## Core Principles

### Target Python Version

**Python 3.11+** required. Use modern syntax:

```python
from __future__ import annotations  # Required in all files

X | None          # Instead of Optional[X]
list[str]         # Instead of List[str]
dict[str, int]    # Instead of Dict[str, int]
Self              # For return type of self
```

### Tooling

```bash
uv run ruff format .           # Format code
uv run ruff check --fix .      # Lint and auto-fix
uv run mypy src/               # Type check
uv run pytest                  # Run tests
uv run pytest --cov            # Run with coverage
```

---

### SOLID Principles

| Principle | Rule | Violation Sign |
|-----------|------|----------------|
| **S**ingle Responsibility | One class = one reason to change | Class name has "And" or "Manager" |
| **O**pen/Closed | Open for extension, closed for modification | Adding feature requires changing existing switch |
| **L**iskov Substitution | Subtypes substitutable for base types | Subclass raises NotImplementedError |
| **I**nterface Segregation | Many small interfaces > one large | Classes implement unused methods |
| **D**ependency Inversion | Depend on abstractions, not concretions | High-level imports low-level directly |

### Other Principles

| Principle | Rule |
|-----------|------|
| **KISS** | Simplest solution that works |
| **DRY** | Single authoritative representation |
| **YAGNI** | Don't build until needed |
| **Fail Fast** | Validate early, raise immediately |
| **Composition over Inheritance** | Prefer object composition |
| **Law of Demeter** | Only talk to immediate friends |

> **For detailed patterns and examples, use skill: design-patterns**

---

## Size Limits

### Hard Limits

| Metric | Hard Limit | Preferred |
|--------|------------|-----------|
| Lines per file | **200** | 150 |
| Lines per function | **12** | 10 |
| Lines per class | **200** | 100-150 |
| Parameters per function | **4** | 3 |
| Indentation levels | **2** | 1 |
| Public methods per class | 10 | 5-7 |
| Instance attributes | 5 | 3-4 |
| Cyclomatic complexity | 10 | 5 |

### Boolean Parameters

**Boolean parameters are forbidden.** Use separate methods or enums:

```python
# BAD
def find_users(include_deleted: bool = False): ...

# GOOD
def find_active_users(): ...
def find_all_users(): ...
```

### Nesting

Use guard clauses to avoid deep nesting:

```python
# BAD: Deep nesting
def process(data):
    if data:
        if data.get("valid"):
            if data.get("type") == "order":
                return Result(...)
    return None

# GOOD: Guard clauses
def process(data):
    if not data:
        return None
    if not data.get("valid"):
        return None
    if data.get("type") != "order":
        return None
    return Result(...)
```

---

## Naming Conventions

### Files & Modules

| Rule | Example | Bad |
|------|---------|-----|
| `snake_case.py` | `user_repository.py` | `UserRepository.py` |
| Descriptive, singular | `order.py` | `orders.py` |
| No abbreviations | `configuration.py` | `cfg.py` |

### Classes

| Rule | Example | Bad |
|------|---------|-----|
| `PascalCase` | `UserRepository` | `user_repository` |
| Nouns | `Order`, `Customer` | `ProcessOrder` |

**Common suffixes**: `Error`, `Factory`, `Builder`, `Handler`, `Service`, `Repository`, `Adapter`, `Strategy`, `Validator`, `Protocol`

### Functions & Methods

| Rule | Example | Bad |
|------|---------|-----|
| `snake_case` | `get_user_by_id` | `getUserById` |
| Verb prefix | `calculate_total` | `total` |

**Verb prefixes**:

| Prefix | Returns | Example |
|--------|---------|---------|
| `get_*` | Value or raises | `get_user(id)` |
| `find_*` | Value or None | `find_user_by_email(email)` |
| `create_*` | New object | `create_order(items)` |
| `update_*` | Updated object | `update_user(id, data)` |
| `delete_*` | None or bool | `delete_order(id)` |
| `validate_*` | None (raises) or bool | `validate_email(email)` |
| `is_*` / `has_*` / `can_*` | bool | `is_active()`, `has_items()` |

### Variables

| Rule | Example | Bad |
|------|---------|-----|
| `snake_case` | `user_count` | `userCount` |
| Descriptive | `total_price` | `tp`, `x` |
| Plurals for collections | `users` | `user_list` |

### Constants

| Rule | Example |
|------|---------|
| `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE = 100` |
| Module-level only | After imports, at top |

### Private Members

| Convention | Meaning | Example |
|------------|---------|---------|
| `_single` | Internal (convention) | `self._cache` |
| `__double` | Name mangling (rare) | `self.__secret` |

---

## Type Hints

### Required

```python
from __future__ import annotations  # Required in all files
```

Annotate all public APIs. Use modern syntax:

```python
# Modern (use these)
X | None                  # Optional
list[str]                 # List
dict[str, int]            # Dict
tuple[int, str]           # Fixed tuple

# Return self
from typing import Self
def with_name(self, name: str) -> Self: ...
```

### Common Patterns

```python
from collections.abc import Sequence, Mapping, Callable
from typing import TypeVar, Generic, Protocol

# Abstract types for parameters
def process(items: Sequence[Item]) -> None: ...

# Concrete types for return values
def get_items() -> list[Item]: ...

# Callable
Handler = Callable[[Request], Response]

# Protocol (interface)
class Readable(Protocol):
    def read(self) -> bytes: ...

# Generic
T = TypeVar("T")
class Repository(Generic[T]):
    def get(self, id: int) -> T | None: ...
```

### Docstrings (Google Style)

```python
def search_users(query: str, *, limit: int = 20) -> list[User]:
    """Search users by name or email.

    Args:
        query: Search query string. Minimum 2 characters.
        limit: Maximum results. Defaults to 20.

    Returns:
        List of matching users, ordered by relevance.

    Raises:
        ValueError: If query is shorter than 2 characters.
    """
```

> **For testing patterns, use skill: testing**
> **For security guidelines, use skill: security**

---

## Git Conventions

### Branch Naming

`<type>/<short-description>`

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New features | `feature/user-authentication` |
| `fix/` | Bug fixes | `fix/login-validation-error` |
| `hotfix/` | Urgent production fixes | `hotfix/payment-timeout` |
| `refactor/` | Code improvements | `refactor/extract-user-service` |
| `docs/` | Documentation only | `docs/api-reference` |
| `test/` | Test improvements | `test/add-integration-tests` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |
| `release/` | Release candidates | `release/v1.2.0` |

**Rules:**
- Use lowercase with hyphens: `feature/add-user-search`
- Be descriptive but concise: max 50 characters
- Include issue number if applicable: `fix/123-login-error`

### Commit Messages (Conventional Commits)

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types**:

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 login` |
| `fix` | Bug fix | `fix(cart): correct quantity calculation` |
| `docs` | Documentation | `docs(readme): update installation steps` |
| `style` | Formatting | `style: apply ruff formatting` |
| `refactor` | Code restructuring | `refactor(user): extract validation logic` |
| `test` | Test changes | `test(order): add integration tests` |
| `perf` | Performance | `perf(query): add database index` |
| `chore` | Maintenance | `chore: update dependencies` |
| `ci` | CI/CD changes | `ci: add coverage reporting` |
| `build` | Build changes | `build: update Python to 3.12` |

**Subject rules:**
- Imperative mood: "add" not "added" or "adds"
- Lowercase first letter
- No period at end
- Max 50 characters

**Body:**
- Explain what and why (not how)
- Wrap at 72 characters
- Separate from subject with blank line

**Example:**
```
feat(search): add fuzzy matching for user search

Implement Levenshtein distance-based fuzzy matching to improve
search results when users make typos. Uses rapidfuzz library
for performance.

- Add FuzzyMatcher class with configurable threshold
- Integrate with existing SearchService
- Add configuration option to enable/disable

Closes #234
```

### Commit Best Practices

| Do | Don't |
|----|-------|
| Atomic commits (one logical change) | Mix unrelated changes |
| Write in imperative mood | Use past tense ("added", "fixed") |
| Explain why, not what | State the obvious |
| Reference issues | Leave commits orphaned |
| Commit early and often | Create massive commits |
| Test before committing | Commit broken code |
| Review diff before committing | Commit blindly |

**Atomic commits:**
```bash
# GOOD: Separate logical changes
git commit -m "refactor(user): extract validation to separate class"
git commit -m "feat(user): add email uniqueness check"
git commit -m "test(user): add validation test cases"

# BAD: Everything in one commit
git commit -m "refactor user and add validation and tests"
```

**When to commit:**
- Feature or sub-feature complete
- Meaningful checkpoint (code works)
- Before switching context
- Before risky changes (can revert)

### PR Guidelines

**Title:** Follow commit message format
```
feat(filters): add JSONLogic filter support
```

**Description Template:**
```markdown
## Summary
Brief description of changes and motivation.

## Changes
- Added JSONLogic parser for complex filter expressions
- Integrated with existing FilterEngine
- Added validation for filter syntax

## How to Test
1. Create a filter with JSONLogic syntax
2. Apply to a query
3. Verify results match expected output

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Linting passes
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
Related to #456
```

**PR Best Practices:**
- Keep PRs small and focused (< 400 lines ideal)
- One feature/fix per PR
- Request review from relevant owners
- Respond to feedback promptly
- Squash commits when merging (if many small commits)

### Git Workflow

**Feature development:**
```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/add-user-search

# 2. Make changes with atomic commits
git add src/search.py
git commit -m "feat(search): add basic user search"

git add tests/test_search.py
git commit -m "test(search): add search test cases"

# 3. Keep branch updated
git fetch origin main
git rebase origin/main

# 4. Push and create PR
git push -u origin feature/add-user-search
```

**Fixing a bug:**
```bash
# 1. Create fix branch
git checkout -b fix/123-login-error

# 2. Write failing test first
git add tests/test_login.py
git commit -m "test(auth): add test for login edge case"

# 3. Fix the bug
git add src/auth.py
git commit -m "fix(auth): handle empty password correctly

Fixes #123"

# 4. Push and create PR
git push -u origin fix/123-login-error
```

**Hotfix for production:**
```bash
# 1. Branch from production tag
git checkout v1.2.0
git checkout -b hotfix/payment-timeout

# 2. Fix with minimal changes
git commit -m "hotfix(payment): increase timeout to 60s

Critical fix for payment failures in production.

Fixes #789"

# 3. Create PR to main and release branch
git push -u origin hotfix/payment-timeout
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]

      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]

      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        types: [python]
        pass_filenames: false
```

---

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│           Presentation Layer                │  API, CLI
├─────────────────────────────────────────────┤
│              Application Layer              │  Use cases
├─────────────────────────────────────────────┤
│                Domain Layer                 │  Business logic
├─────────────────────────────────────────────┤
│             Infrastructure Layer            │  Database, APIs
└─────────────────────────────────────────────┘
```

**Rules**:
1. Each layer only depends on layers **below** it
2. Domain layer has **no external dependencies**
3. Never import from upper layers

### Project Structure

```
src/
└── mypackage/
    ├── __init__.py         # Public API exports
    ├── py.typed            # PEP 561 marker
    ├── exceptions.py       # Exception hierarchy
    ├── types.py            # Shared types
    ├── core/               # Domain (no deps)
    ├── application/        # Use cases
    ├── adapters/           # Infrastructure
    └── integrations/       # Framework support

tests/
├── conftest.py             # Shared fixtures
├── unit/
├── integration/
└── e2e/
```

### Dependency Injection

```python
# GOOD: Constructor injection
class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

# BAD: Hidden dependency
class OrderService:
    def process(self):
        repository = ServiceLocator.get(OrderRepository)  # Hidden!
```

### Exception Hierarchy

```python
class AppError(Exception):
    """Base exception."""

class DomainError(AppError):
    """Domain rule violations."""

class ValidationError(DomainError):
    """Invalid input."""

class NotFoundError(AppError):
    """Resource not found."""

class InfrastructureError(AppError):
    """Infrastructure failures."""
```

> **For refactoring techniques, use skill: refactoring**
> **For performance optimization, use skill: performance**
> **For API design, use skill: api-design**

---

## AI Agent Guidance

### Before Making Changes

1. **Read** the file(s) you plan to modify
2. **Look** at similar implementations in codebase
3. **Check** existing tests for the module
4. **Understand** existing patterns before adding code

### Decision Tree: Create vs Edit

```
Need new functionality?
├── YES → Is there a file for this concern?
│         ├── YES → Will it exceed 200 lines?
│         │         ├── YES → CREATE new file
│         │         └── NO  → EDIT existing
│         └── NO  → Is this a new concern?
│                   ├── YES → CREATE new file
│                   └── NO  → EDIT nearest related
└── NO  → EDIT existing file
```

**Prefer editing over creating new files.**

### Decision Tree: Refactor vs Extend

```
Is the code clean?
├── YES → Add feature following pattern
└── NO  → Does refactoring help the task?
          ├── YES → Is it small refactoring?
          │         ├── YES → Refactor then add
          │         └── NO  → Ask user first
          └── NO  → Add with minimal changes
```

**Small refactoring** (do immediately): Rename, extract 1-2 methods, add type hints
**Large refactoring** (ask first): Restructure files, change API, modify abstractions

### Workflow: Adding a Feature

```
1. UNDERSTAND
   ├── Read user's request
   ├── Identify affected modules
   └── Check similar implementations

2. PLAN
   ├── List files to create/modify
   ├── Check size limits
   └── Identify tests needed

3. IMPLEMENT
   ├── Start with core logic
   ├── Add type hints
   ├── Keep functions ≤12 lines
   └── Follow existing patterns

4. VERIFY
   ├── uv run ruff format .
   ├── uv run ruff check --fix .
   ├── uv run mypy src/
   └── uv run pytest
```

### Workflow: Fixing a Bug

```
1. REPRODUCE → Write failing test
2. LOCATE   → Find root cause
3. FIX      → Minimal change
4. VERIFY   → All tests pass
```

### Workflow: Refactoring

```
1. ENSURE   → All tests pass before starting
2. SMALL    → One change at a time
3. TEST     → Run tests after each change
4. COMMIT   → Commit after each success
```

### Common Mistakes to Avoid

| Mistake | Do Instead |
|---------|------------|
| Writing without reading first | Read related files first |
| Creating files unnecessarily | Edit existing files |
| Large functions | Keep ≤12 lines |
| Missing type hints | Add types as you write |
| Mixing refactoring and features | Separate commits |
| Not running tests | Test after every change |
| Deep nesting | Use guard clauses |

### When to Ask the User

- Request is ambiguous
- Multiple valid approaches exist
- Change might break existing behavior
- Large refactoring needed
- Unsure about requirements

### Verification Commands

**Run before completing any work:**

```bash
uv run ruff format .
uv run ruff check --fix .
uv run mypy src/
uv run pytest
```

### Self-Review Checklist

- [ ] Code does what was requested
- [ ] Functions ≤12 lines
- [ ] No deep nesting (max 2 levels)
- [ ] Type hints on public APIs
- [ ] Tests cover happy path and errors
- [ ] All checks pass

---

## Quick Reference

### Size Limits

| Metric | Limit |
|--------|-------|
| Lines per file | 200 |
| Lines per function | 12 |
| Parameters per function | 4 |
| Nesting levels | 2 |
| Public methods per class | 10 |

### Naming

| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `user_repository.py` |
| Classes | PascalCase | `UserRepository` |
| Functions | snake_case + verb | `get_user()` |
| Variables | snake_case | `user_count` |
| Constants | UPPER_SNAKE | `MAX_SIZE` |
| Private | Leading underscore | `_internal` |

### Commit Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code restructuring |
| `test` | Test changes |
| `chore` | Maintenance |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Failed |
| 500 | Server Error |

### Type Hints Cheat Sheet

```python
# Basic
x: int
y: str | None
z: list[str]

# Collections
items: list[Item]
mapping: dict[str, int]

# Callable
Handler = Callable[[Request], Response]

# Protocol
class Readable(Protocol):
    def read(self) -> bytes: ...

# Generic
T = TypeVar("T")
def first(items: list[T]) -> T | None: ...
```

### Command Reference

```bash
# All checks
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest

# Individual
uv run ruff format .           # Format
uv run ruff check --fix .      # Lint
uv run mypy src/               # Type check
uv run pytest                  # Test
uv run pytest --cov            # Coverage
```

---

## Skills Reference

For detailed guidance on specific topics, request these skills:

### Design Patterns (RefactoringGuru)

| Skill | Use When |
|-------|----------|
| `guru-patterns-creational` | Need Factory, Builder, Singleton, Prototype patterns |
| `guru-patterns-structural` | Need Adapter, Decorator, Facade, Proxy patterns |
| `guru-patterns-behavioral` | Need Strategy, Observer, Command, State patterns |
| `guru-smells` | Detecting and fixing code smells |

### Refactoring (RefactoringGuru)

| Skill | Use When |
|-------|----------|
| `guru-refactor-methods` | Extract Method, Inline Method, Extract Variable |
| `guru-refactor-moving` | Move Method, Extract Class, Hide Delegate |
| `guru-refactor-data` | Encapsulate Collection, Replace Primitive with Object |
| `guru-refactor-conditionals` | Decompose Conditional, Guard Clauses, Polymorphism |
| `guru-refactor-calls` | Rename Method, Add/Remove Parameter, Parameter Object |
| `guru-refactor-generalization` | Pull Up/Push Down, Extract Superclass, Template Method |

### Architecture

| Skill | Use When |
|-------|----------|
| `arch-principles` | Core principles, DI, observability, feature flags |
| `arch-ddd` | Domain-Driven Design (entities, aggregates, value objects) |
| `arch-cqrs-es` | Event Sourcing + CQRS patterns |
| `arch-hexagonal` | Hexagonal/Ports & Adapters architecture |
| `arch-microservices` | Saga, Circuit Breaker, 12-Factor App |

### Security

| Skill | Use When |
|-------|----------|
| `sec-basics` | Input validation, SQL injection, secrets, auth |
| `sec-owasp` | Complete OWASP Top 10 with Python examples |
| `sec-ops` | SecOps CI/CD, SAST/DAST, threat modeling (STRIDE) |
| `sec-api` | Security headers, CORS, rate limiting, JWT, API keys |

### Testing

| Skill | Use When |
|-------|----------|
| `test-standards` | Naming, AAA pattern, fixtures, mocking, property-based |
| `test-ops` | CI/CD integration, GitHub Actions, GitLab CI, parallelization |
| `test-advanced` | Mutation testing (mutmut), Contract testing (Pact) |
| `test-load` | Load/Performance testing with Locust |
| `test-chaos` | Chaos engineering, resilience testing |
| `test-data` | Test data management, factories, visual regression |

### API Design

| Skill | Use When |
|-------|----------|
| `api-rest` | RESTful conventions, response formats, pagination, versioning |
| `api-graphql` | GraphQL with Strawberry, DataLoaders, N+1 prevention |
| `api-grpc` | gRPC for microservices, Protocol Buffers, streaming |
| `api-gateway` | API Gateway patterns, BFF, HTTP caching |
| `api-auth` | API keys, JWT, OAuth2 scopes, rate limiting |
| `api-lifecycle` | Deprecation, versioning changes, HATEOAS |

### Performance

| Skill | Use When |
|-------|----------|
| `perf-core` | Core optimization: caching, async, memory, N+1 prevention |
| `perf-ops` | Performance testing in CI/CD, benchmarking, regression detection |
| `perf-slo` | SLOs, SLIs, SLAs, error budgets |
| `perf-apm` | OpenTelemetry, distributed tracing, metrics |
| `perf-profiling` | py-spy, Scalene, memray, flame graphs |
| `perf-database` | Query analysis, connection pooling, EXPLAIN |

### Other

| Skill | Use When |
|-------|----------|
| `type-hints` | Type annotations, generics, protocols |

---

*This document provides essential rules. For detailed examples and advanced techniques, use the appropriate skill.*
