---
name: test-advanced
description: >
  Advanced testing techniques for Python. Covers mutation testing with mutmut
  to verify test quality, contract testing with Pact for API compatibility,
  Pact Broker integration, and consumer-driven contract workflows.
version: "2.0"
source: mixed
related:
  - test-standards
  - test-ops
  - api-rest
  - api-grpc
---

## MUTATION TESTING

Mutation testing verifies your tests actually catch bugs by introducing small changes (mutants) to your code.

---

### Using mutmut

**Installation and configuration:**
```toml
# pyproject.toml
[tool.mutmut]
paths_to_mutate = "src/mypackage/"
tests_dir = "tests/"
runner = "uv run pytest -x -q"
dict_synonyms = ["Enum", "IntEnum"]
```

**Running mutation tests:**
```bash
# Run mutation testing
uv run mutmut run

# View results
uv run mutmut results

# Show specific mutant
uv run mutmut show 42

# Generate HTML report
uv run mutmut html
```

---

### Interpreting Results

**Mutant survival indicates weak tests:**
```python
# Original code
def calculate_discount(price: int, percentage: int) -> int:
    return price * percentage // 100

# Mutant 1: Changed * to +
def calculate_discount(price: int, percentage: int) -> int:
    return price + percentage // 100  # SURVIVED = test didn't catch!

# Mutant 2: Changed // to /
def calculate_discount(price: int, percentage: int) -> int:
    return price * percentage / 100   # KILLED = test caught it!
```

**Improving tests based on mutants:**
```python
# WEAK: Only tests one case
def test_discount():
    assert calculate_discount(100, 10) == 10

# STRONG: Tests boundary conditions
def test_discount_calculation():
    assert calculate_discount(100, 10) == 10
    assert calculate_discount(100, 0) == 0    # Catches + mutation
    assert calculate_discount(0, 10) == 0     # Catches + mutation
    assert calculate_discount(100, 100) == 100
    assert calculate_discount(50, 50) == 25
```

---

### Mutation Score Targets

| Score | Quality Level | Action |
|-------|---------------|--------|
| < 60% | Poor | Tests need significant improvement |
| 60-80% | Acceptable | Good for non-critical code |
| 80-90% | Good | Suitable for most production code |
| > 90% | Excellent | Required for critical business logic |

---

### CI Integration

```yaml
# Run mutation tests on PRs touching critical code
mutation-test:
  runs-on: ubuntu-latest
  if: contains(github.event.pull_request.labels.*.name, 'critical')
  steps:
    - uses: actions/checkout@v4
    
    - name: Run mutation tests
      run: |
        uv run mutmut run --CI
        uv run mutmut results
        
    - name: Check mutation score
      run: |
        SCORE=$(uv run mutmut results | grep -oP 'Mutation score: \K\d+')
        if [ "$SCORE" -lt 80 ]; then
          echo "Mutation score too low: ${SCORE}%"
          exit 1
        fi
```

---

### Common Mutation Types

| Mutation | Example | What It Tests |
|----------|---------|---------------|
| Arithmetic | `+` to `-` | Mathematical operations |
| Comparison | `<` to `<=` | Boundary conditions |
| Boolean | `and` to `or` | Logic flow |
| Return | `return x` to `return None` | Return value handling |
| Constant | `0` to `1` | Magic number dependencies |

---

## CONTRACT TESTING

Contract testing ensures services communicate correctly without full integration tests.

---

### Consumer-Driven Contracts with Pact

**Consumer side (API client):**
```python
# tests/contract/test_user_api_consumer.py
import pytest
from pact import Consumer, Provider, Like, EachLike, Term

@pytest.fixture
def pact():
    """Set up Pact mock provider."""
    pact = Consumer("UserWebApp").has_pact_with(
        Provider("UserService"),
        pact_dir="./pacts",
    )
    pact.start_service()
    yield pact
    pact.stop_service()


def test_get_user(pact):
    """Test consumer expectation for GET /users/{id}."""
    # Define expected interaction
    (pact
        .given("a user with ID 1 exists")
        .upon_receiving("a request for user 1")
        .with_request("GET", "/users/1")
        .will_respond_with(
            200,
            headers={"Content-Type": "application/json"},
            body={
                "id": Like(1),
                "email": Term(r".+@.+\..+", "user@example.com"),
                "name": Like("John Doe"),
                "created_at": Term(
                    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                    "2024-01-15T10:30:00"
                ),
            }
        ))

    # Execute consumer code against mock
    with pact:
        client = UserApiClient(base_url=pact.uri)
        user = client.get_user(1)

        assert user.id == 1
        assert "@" in user.email
        assert user.name is not None


def test_get_users_list(pact):
    """Test consumer expectation for GET /users."""
    (pact
        .given("users exist in the system")
        .upon_receiving("a request for all users")
        .with_request("GET", "/users", query={"page": "1", "limit": "10"})
        .will_respond_with(
            200,
            body={
                "items": EachLike({
                    "id": Like(1),
                    "email": Like("user@example.com"),
                    "name": Like("John Doe"),
                }),
                "total": Like(100),
                "page": Like(1),
                "pages": Like(10),
            }
        ))

    with pact:
        client = UserApiClient(base_url=pact.uri)
        result = client.list_users(page=1, limit=10)

        assert len(result.items) > 0
        assert result.total >= 0
```

---

### Provider Side Verification

```python
# tests/contract/test_user_api_provider.py
import pytest
from pact import Verifier
from mypackage.api import create_app


@pytest.fixture
def provider_app():
    """Create provider application for testing."""
    app = create_app(testing=True)
    return app


def test_provider_honors_pact(provider_app):
    """Verify provider satisfies consumer contracts."""
    verifier = Verifier(
        provider="UserService",
        provider_base_url="http://localhost:8000",
    )

    # Set up provider states
    verifier.set_state(
        "http://localhost:8000/_pact/provider-states",
        teardown=True,
    )

    # Verify all pacts
    success, logs = verifier.verify_pacts(
        "./pacts/userweb_app-user_service.json",
        enable_pending=True,
        publish_verification_results=True,
        provider_version="1.0.0",
    )

    assert success == 0, f"Pact verification failed:\n{logs}"


# Provider state handler
@app.route("/_pact/provider-states", methods=["POST"])
def provider_states():
    """Handle provider state setup for Pact verification."""
    state = request.json.get("state")

    if state == "a user with ID 1 exists":
        # Set up test data
        db.session.add(User(id=1, email="user@example.com", name="John Doe"))
        db.session.commit()
    elif state == "users exist in the system":
        for i in range(10):
            db.session.add(User(id=i, email=f"user{i}@example.com"))
        db.session.commit()

    return {"result": state}
```

---

### Pact Broker Integration

```yaml
# CI: Publish and verify pacts
pact-tests:
  runs-on: ubuntu-latest
  steps:
    - name: Run consumer tests
      run: uv run pytest tests/contract/test_*_consumer.py

    - name: Publish pacts to broker
      run: |
        pact-broker publish ./pacts \
          --broker-base-url=$PACT_BROKER_URL \
          --consumer-app-version=$GITHUB_SHA \
          --tag=$GITHUB_REF_NAME

    - name: Verify provider against broker
      run: |
        uv run pytest tests/contract/test_*_provider.py \
          --pact-broker-url=$PACT_BROKER_URL \
          --pact-provider-version=$GITHUB_SHA

    - name: Can I Deploy?
      run: |
        pact-broker can-i-deploy \
          --pacticipant=UserService \
          --version=$GITHUB_SHA \
          --to-environment=production
```

---

### Pact Matchers

| Matcher | Purpose | Example |
|---------|---------|---------|
| `Like(value)` | Match type, not value | `Like(1)` matches any int |
| `EachLike(template)` | Array of matching items | `EachLike({"id": Like(1)})` |
| `Term(regex, sample)` | Regex match | `Term(r"\d+", "123")` |
| `Format` | Format matchers | UUID, ISO8601, etc. |

---

### Contract Testing Workflow

```
Consumer Team                    Provider Team
      |                               |
      |  1. Write consumer tests      |
      |  2. Generate pact file        |
      |                               |
      |  ------ Publish Pact ------>  |
      |                               |
      |                    3. Verify against pact
      |                    4. Fix any failures
      |                               |
      |  <---- Can I Deploy? -------  |
      |                               |
      |  5. Deploy consumer           |
      |                    6. Deploy provider
```

---

## Quick Reference

### mutmut Commands

```bash
uv run mutmut run              # Run all mutations
uv run mutmut run --paths-to-mutate src/core/  # Specific path
uv run mutmut results          # View results
uv run mutmut show <id>        # Show specific mutant
uv run mutmut html             # Generate report
uv run mutmut run --CI         # CI mode (fail on survivors)
```

### Pact Commands

```bash
# Consumer tests (generate pacts)
uv run pytest tests/contract/test_*_consumer.py

# Provider verification
uv run pytest tests/contract/test_*_provider.py

# Publish to broker
pact-broker publish ./pacts \
  --broker-base-url=$URL \
  --consumer-app-version=$VERSION

# Check deployment safety
pact-broker can-i-deploy \
  --pacticipant=MyService \
  --version=$VERSION \
  --to-environment=production
```

### Testing Tools

| Tool | Purpose | Command |
|------|---------|---------|
| mutmut | Mutation testing | `uv run mutmut run` |
| pact-python | Contract testing | Consumer/Provider tests |
| pact-broker | Contract storage | `pact-broker publish` |

---

## Related Skills

- `test-standards` - Testing fundamentals and patterns
- `test-ops` - CI/CD integration
- `test-load` - Performance testing
- `test-chaos` - Chaos engineering
- `test-data` - Test data management
