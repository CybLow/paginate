---
name: test-ops
description: >
  TestOps and CI/CD integration for Python testing. Covers GitHub Actions workflows,
  GitLab CI pipelines, test parallelization with pytest-xdist, multi-stage test
  pipelines, coverage reporting, and CI test strategies.
version: "2.0"
source: mixed
related:
  - test-standards
  - perf-ops
  - sec-ops
  - test-load
---

## TESTOPS: CI/CD INTEGRATION

TestOps integrates testing into your development workflow. Automate testing at every stage.

---

### GitHub Actions Workflow

**Complete test pipeline:**
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"
  UV_CACHE_DIR: ~/.cache/uv

jobs:
  # Fast checks run first
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
        
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: Format check
        run: uv run ruff format --check .
        
      - name: Lint
        run: uv run ruff check .
        
      - name: Type check
        run: uv run mypy src/

  # Unit tests (fast, parallel)
  unit-tests:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}
        
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: Run unit tests
        run: |
          uv run pytest tests/unit \
            -m "unit" \
            --cov=src/mypackage \
            --cov-report=xml \
            --cov-fail-under=85 \
            --junitxml=junit-unit.xml \
            -n auto
            
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          flags: unit-${{ matrix.python-version }}
          
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: junit-unit.xml

  # Integration tests (slower, need services)
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
        
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: Run migrations
        run: uv run alembic upgrade head
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          
      - name: Run integration tests
        run: |
          uv run pytest tests/integration \
            -m "integration" \
            --junitxml=junit-integration.xml
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

  # E2E tests (slowest, full stack)
  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          
      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}
        
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: Start application
        run: |
          docker compose -f docker-compose.test.yml up -d
          sleep 10  # Wait for services
          
      - name: Run E2E tests
        run: |
          uv run pytest tests/e2e \
            -m "e2e" \
            --junitxml=junit-e2e.xml
            
      - name: Stop application
        if: always()
        run: docker compose -f docker-compose.test.yml down

  # Final quality gate
  quality-gate:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, e2e-tests]
    steps:
      - name: Quality gate passed
        run: echo "All tests passed!"
```

---

### GitLab CI Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - integration
  - e2e

variables:
  PYTHON_VERSION: "3.12"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

.python-template: &python-setup
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install uv
    - uv sync --frozen

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/pip
    - .venv

# Stage 1: Linting (fast feedback)
lint:
  stage: lint
  <<: *python-setup
  script:
    - uv run ruff format --check .
    - uv run ruff check .
    - uv run mypy src/

# Stage 2: Unit tests (parallel matrix)
unit-tests:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.11", "3.12", "3.13"]
  <<: *python-setup
  script:
    - uv run pytest tests/unit -m "unit" --cov --cov-report=xml --junitxml=junit.xml
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

# Stage 3: Integration tests
integration-tests:
  stage: integration
  <<: *python-setup
  services:
    - postgres:16
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    DATABASE_URL: postgresql://test:test@postgres:5432/test_db
    REDIS_URL: redis://redis:6379
  script:
    - uv run alembic upgrade head
    - uv run pytest tests/integration -m "integration" --junitxml=junit.xml
  artifacts:
    reports:
      junit: junit.xml

# Stage 4: E2E tests
e2e-tests:
  stage: e2e
  <<: *python-setup
  script:
    - docker compose -f docker-compose.test.yml up -d
    - sleep 10
    - uv run pytest tests/e2e -m "e2e" --junitxml=junit.xml
    - docker compose -f docker-compose.test.yml down
  artifacts:
    reports:
      junit: junit.xml
```

---

### Test Parallelization

**Parallel test execution with pytest-xdist:**
```python
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "-n", "auto",           # Parallel workers (auto = CPU count)
    "--dist", "loadgroup",  # Distribute by test groups
]

# Group tests that share fixtures
@pytest.mark.xdist_group("database")
class TestDatabaseOperations:
    def test_create_user(self, db_session): ...
    def test_update_user(self, db_session): ...

@pytest.mark.xdist_group("api")
class TestAPIEndpoints:
    def test_get_users(self, client): ...
    def test_create_user(self, client): ...
```

**Split tests across CI workers:**
```yaml
# GitHub Actions matrix split
jobs:
  test:
    strategy:
      matrix:
        group: [1, 2, 3, 4]
    steps:
      - name: Run tests (shard ${{ matrix.group }}/4)
        run: |
          uv run pytest tests/ \
            --splits 4 \
            --group ${{ matrix.group }}
```

---

### CI Test Strategy

```
+-------------------------------------------------------------+
|                         PR Created                          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|  Stage 1: Lint + Type Check (fast feedback, <1 min)        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|  Stage 2: Unit Tests (parallel, matrix, <3 min)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|  Stage 3: Integration Tests (with services, <5 min)        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|  Stage 4: E2E Tests (full stack, <10 min)                  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|  Optional: Performance/Chaos/Visual (scheduled or manual)  |
+-------------------------------------------------------------+
```

---

### Test Matrix Strategies

**Python version matrix:**
```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
    os: [ubuntu-latest, macos-latest, windows-latest]
    exclude:
      - os: windows-latest
        python-version: "3.11"
```

**Feature flag matrix:**
```yaml
strategy:
  matrix:
    include:
      - feature: "default"
        env: {}
      - feature: "experimental"
        env:
          ENABLE_EXPERIMENTAL: "true"
      - feature: "legacy"
        env:
          LEGACY_MODE: "true"
```

---

### Coverage Reporting

**Codecov integration:**
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: coverage.xml
    flags: unittests
    name: codecov-umbrella
    fail_ci_if_error: true
```

**Coverage configuration:**
```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true
parallel = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
fail_under = 85
show_missing = true
```

---

### Test Result Artifacts

**Store and compare test results:**
```yaml
- name: Upload test results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results-${{ github.sha }}
    path: |
      junit-*.xml
      reports/
    retention-days: 30

- name: Publish test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: junit-*.xml
    comment_mode: always
```

---

## Quick Reference

### pytest-xdist Commands

```bash
uv run pytest -n auto           # Auto-detect workers
uv run pytest -n 4              # 4 workers
uv run pytest --dist loadgroup  # Group by marker
uv run pytest --dist loadscope  # Group by module
```

### CI Test Commands

```bash
# All checks in CI
uv run ruff format --check .
uv run ruff check .
uv run mypy src/
uv run pytest --cov --cov-fail-under=85 --junitxml=junit.xml
```

### Test Stage Timing

| Stage | Max Duration | Tests |
|-------|--------------|-------|
| Lint + Types | 1 min | Format, lint, mypy |
| Unit | 3 min | Fast, isolated |
| Integration | 5 min | DB, Redis |
| E2E | 10 min | Full stack |

---

## Related Skills

- `test-standards` - Testing fundamentals and patterns
- `test-advanced` - Mutation testing, contract testing
- `test-load` - Performance testing CI integration
- `test-chaos` - Chaos testing automation
- `test-data` - Test data management
