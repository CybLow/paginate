---
name: test-standards
description: >
  Core testing standards and best practices for Python. Covers test naming conventions,
  AAA pattern (Arrange-Act-Assert), test categories with markers, file organization,
  coverage requirements, fixtures, factories, mocking strategies, property-based testing
  with Hypothesis, snapshot testing, async testing, and test anti-patterns.
version: "2.0"
source: pytest
related:
  - test-ops
  - test-data
  - test-advanced
  - guru-smells
---

## TESTING STANDARDS

Tests are documentation. They prove correctness and prevent regressions.

---

### Test Naming Convention

**Format:** `test_<unit>_<scenario>_<expected_result>`

```python
# GOOD: Descriptive names
def test_user_creation_with_valid_data_succeeds(): ...
def test_user_creation_with_duplicate_email_raises_error(): ...
def test_order_total_with_discount_applies_percentage(): ...
def test_search_with_empty_query_returns_empty_list(): ...

# BAD: Vague names
def test_user(): ...
def test_create(): ...
def test_error(): ...
def test_1(): ...
```

**Test class naming:**
```python
class TestUserService:
    """Tests for UserService class."""

    def test_create_user_with_valid_data_returns_user(self): ...
    def test_create_user_with_invalid_email_raises_validation_error(self): ...

class TestOrderCalculation:
    """Tests for order calculation functions."""

    def test_calculate_total_with_no_discount_returns_subtotal(self): ...
    def test_calculate_total_with_percentage_discount_applies_correctly(self): ...
```

---

### Test Structure (AAA Pattern)

Every test follows **Arrange-Act-Assert**:

```python
def test_order_discount_calculation():
    # Arrange - Set up test data and dependencies
    order = Order(
        items=[
            OrderItem(product_id=1, quantity=2, unit_price=Money(1000)),
            OrderItem(product_id=2, quantity=1, unit_price=Money(500)),
        ]
    )
    discount = PercentageDiscount(10)

    # Act - Execute the code under test
    discounted_total = order.apply_discount(discount)

    # Assert - Verify the result
    assert discounted_total == Money(2250)  # (2000 + 500) * 0.9


def test_user_repository_find_by_email(db_session: Session):
    # Arrange
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    repository = UserRepository(db_session)

    # Act
    found_user = repository.find_by_email("test@example.com")

    # Assert
    assert found_user is not None
    assert found_user.email == "test@example.com"
    assert found_user.name == "Test User"
```

**Keep sections clearly separated:**
```python
# BAD: Mixed arrange/act/assert
def test_confusing():
    user = User(name="test")
    assert user.name == "test"  # Assert during arrange?
    user.activate()
    user.deactivate()  # Multiple acts
    assert not user.is_active
    user.activate()  # More acts
    assert user.is_active  # More asserts

# GOOD: Clear separation, one logical assertion
def test_user_deactivation_sets_inactive_status():
    # Arrange
    user = User(name="test")
    user.activate()

    # Act
    user.deactivate()

    # Assert
    assert not user.is_active
```

---

### Test Categories

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_password_hashing():
    """Unit test - fast, no I/O."""
    hasher = PasswordHasher()
    hashed = hasher.hash("password123")
    assert hasher.verify("password123", hashed)


@pytest.mark.integration
async def test_user_creation_saves_to_database(db_session: AsyncSession):
    """Integration test - uses real database."""
    repository = UserRepository(db_session)
    user = User(email="test@example.com")
    
    saved_user = await repository.save(user)
    
    assert saved_user.id is not None


@pytest.mark.e2e
async def test_complete_checkout_flow(client: AsyncClient):
    """End-to-end test - full user scenario."""
    # Add item to cart
    await client.post("/cart/items", json={"product_id": 1, "quantity": 2})
    
    # Checkout
    response = await client.post("/checkout", json={"payment_method": "card"})
    
    assert response.status_code == 201
    assert response.json()["order_id"] is not None


@pytest.mark.property
@given(st.lists(st.integers(min_value=0, max_value=1000)))
def test_sort_preserves_elements(items: list[int]):
    """Property-based test - checks invariants."""
    sorted_items = custom_sort(items)
    assert sorted(sorted_items) == sorted(items)
    assert len(sorted_items) == len(items)


@pytest.mark.benchmark
def test_pagination_performance(benchmark):
    """Performance benchmark test."""
    items = list(range(10000))
    
    result = benchmark(paginate, items, page=50, per_page=20)
    
    assert len(result.items) == 20
```

**Running specific categories:**
```bash
uv run pytest -m unit           # Only unit tests
uv run pytest -m integration    # Only integration tests
uv run pytest -m "not slow"     # Exclude slow tests
uv run pytest -m "unit or integration"  # Multiple markers
```

---

### Test File Organization

**Mirror source structure:**
```
src/
+-- mypackage/
    +-- services/
    |   +-- user_service.py
    +-- repositories/
    |   +-- user_repository.py
    +-- models/
        +-- user.py

tests/
+-- conftest.py                    # Shared fixtures
+-- unit/                          # Unit tests (fast, isolated)
|   +-- services/
|   |   +-- test_user_service.py
|   +-- repositories/
|   |   +-- test_user_repository.py
|   +-- models/
|       +-- test_user.py
+-- integration/                   # Integration tests
|   +-- test_user_workflow.py
+-- e2e/                           # End-to-end tests
    +-- test_api_endpoints.py
```

**Alternative: flat structure for small projects:**
```
tests/
+-- conftest.py
+-- test_user_service.py
+-- test_user_repository.py
+-- test_user_model.py
```

---

### Coverage Requirements

| Level | Requirement | Notes |
|-------|-------------|-------|
| Minimum | **85%** | CI/CD gate |
| Target | 90%+ | Good coverage |
| Critical paths | 100% | Core business logic |

**Exclude from coverage:**
```python
# In pyproject.toml [tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

**Running with coverage:**
```bash
uv run pytest --cov=src/mypackage --cov-report=html
uv run pytest --cov=src/mypackage --cov-fail-under=85
```

---

### Fixtures and Test Data

**Use fixtures for shared setup:**
```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_user() -> User:
    """Provide a sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        name="Test User",
        status=UserStatus.ACTIVE,
    )


@pytest.fixture
def user_service(db_session: AsyncSession) -> UserService:
    """Provide UserService with mocked dependencies."""
    repository = UserRepository(db_session)
    email_service = Mock(spec=EmailService)
    return UserService(repository, email_service)
```

**Use factories for test data (factory_boy):**
```python
# tests/factories.py
import factory
from mypackage.models import User, Order, OrderItem

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    email = factory.LazyAttribute(lambda o: f"user{o.id}@example.com")
    name = factory.Faker("name")
    status = UserStatus.ACTIVE


class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    status = OrderStatus.PENDING
    created_at = factory.LazyFunction(datetime.now)


# Usage in tests
def test_order_processing():
    user = UserFactory(status=UserStatus.PREMIUM)
    order = OrderFactory(user=user, status=OrderStatus.PENDING)
    
    process_order(order)
    
    assert order.status == OrderStatus.PROCESSING
```

---

### Mocking Guidelines

**Mock at boundaries only:**
```python
# GOOD: Mock external services
def test_payment_processing(mocker):
    # Mock the external payment API
    mock_stripe = mocker.patch("mypackage.payments.stripe_client")
    mock_stripe.create_charge.return_value = {"id": "ch_123", "status": "succeeded"}

    service = PaymentService()
    result = service.process_payment(amount=1000)

    assert result.success
    mock_stripe.create_charge.assert_called_once()


# BAD: Mock internal implementation details
def test_order_total(mocker):
    # Don't mock internal methods
    mocker.patch.object(Order, "_calculate_subtotal", return_value=100)
    mocker.patch.object(Order, "_calculate_tax", return_value=10)
    
    order = Order(items=[...])
    total = order.get_total()
    
    assert total == 110  # What are we even testing?
```

**Prefer fakes over mocks:**
```python
# GOOD: Use a fake implementation
class FakeEmailService:
    def __init__(self) -> None:
        self.sent_emails: list[Email] = []

    def send(self, email: Email) -> None:
        self.sent_emails.append(email)


def test_welcome_email_sent_on_registration():
    email_service = FakeEmailService()
    user_service = UserService(repository, email_service)

    user_service.register(email="new@example.com", name="New User")

    assert len(email_service.sent_emails) == 1
    assert email_service.sent_emails[0].recipient == "new@example.com"
    assert "Welcome" in email_service.sent_emails[0].subject
```

**Don't mock what you don't own:**
```python
# BAD: Mocking library internals
def test_with_mocked_datetime(mocker):
    mocker.patch("datetime.datetime.now", return_value=datetime(2024, 1, 1))
    ...

# GOOD: Inject time provider
class TimeProvider(Protocol):
    def now(self) -> datetime: ...

class RealTimeProvider:
    def now(self) -> datetime:
        return datetime.now()

class FakeTimeProvider:
    def __init__(self, fixed_time: datetime) -> None:
        self._time = fixed_time

    def now(self) -> datetime:
        return self._time


def test_with_fake_time():
    time_provider = FakeTimeProvider(datetime(2024, 1, 1))
    service = MyService(time_provider=time_provider)
    ...
```

---

### Property-Based Testing (Hypothesis)

**Use for invariant testing:**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(items: list[int]):
    """Sorting twice gives same result as sorting once."""
    once = sorted(items)
    twice = sorted(sorted(items))
    assert once == twice


@given(st.integers(min_value=1, max_value=100))
def test_pagination_page_count_is_correct(total_items: int):
    """Page count calculation is always correct."""
    page_size = 10
    page_count = calculate_page_count(total_items, page_size)
    
    # Invariants
    assert page_count >= 1
    assert (page_count - 1) * page_size < total_items <= page_count * page_size


@given(
    st.text(min_size=1, max_size=100),
    st.text(min_size=0, max_size=50),
)
def test_search_results_contain_query(query: str, prefix: str):
    """Search results must contain the search query."""
    items = [f"{prefix}{query}suffix", "no match", f"another{query}"]
    
    results = search(items, query)
    
    for result in results:
        assert query in result
```

**Custom strategies:**
```python
from hypothesis import given, strategies as st
from hypothesis.strategies import composite

@composite
def valid_email(draw) -> str:
    """Generate valid email addresses."""
    local = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=20))
    domain = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=2, max_size=10))
    tld = draw(st.sampled_from(["com", "org", "net", "io"]))
    return f"{local}@{domain}.{tld}"


@composite
def valid_order(draw) -> Order:
    """Generate valid orders for testing."""
    items = draw(st.lists(
        st.builds(
            OrderItem,
            product_id=st.integers(min_value=1),
            quantity=st.integers(min_value=1, max_value=100),
            unit_price=st.integers(min_value=1, max_value=10000),
        ),
        min_size=1,
        max_size=10,
    ))
    return Order(items=items)


@given(valid_order())
def test_order_total_is_positive(order: Order):
    """Order total is always positive."""
    assert order.calculate_total() > 0
```

---

### Snapshot Testing (Syrupy)

**Use for complex output regression:**
```python
def test_api_response_format(snapshot):
    """Verify API response structure hasn't changed."""
    response = api.get_user_profile(user_id=1)
    
    assert response.json() == snapshot


def test_html_rendering(snapshot):
    """Verify HTML output matches expected."""
    html = render_template("invoice.html", order=sample_order)
    
    assert html == snapshot(extension_class=HTMLSnapshotExtension)


def test_error_messages(snapshot):
    """Verify error message format."""
    try:
        validate_user_data({"email": "invalid"})
    except ValidationError as e:
        assert str(e) == snapshot
```

**Update snapshots:**
```bash
uv run pytest --snapshot-update
```

---

### Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_user_creation(db_session: AsyncSession):
    """Test async database operations."""
    repository = UserRepository(db_session)
    user = User(email="test@example.com")
    
    saved_user = await repository.save(user)
    
    assert saved_user.id is not None


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent async operations."""
    async def fetch_user(user_id: int) -> User:
        return await user_service.get(user_id)
    
    # Run concurrently
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
    
    assert len(users) == 3
```

---

### Test Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Test interdependence | Tests pass/fail based on order | Each test sets up own data |
| Testing implementation | Breaks when refactoring | Test behavior, not internals |
| Flaky tests | Random pass/fail | Fix timing issues, use retries |
| Slow tests | CI takes too long | Mock I/O, parallelize |
| Excessive mocking | Tests don't catch real bugs | Use fakes, integration tests |
| No assertions | Test always passes | Always assert expected behavior |
| Assert on exception | Using try/except for assertions | Use pytest.raises |

```python
# BAD: Assert on exception
def test_invalid_email_raises():
    try:
        validate_email("invalid")
        assert False, "Should have raised"
    except ValidationError:
        pass

# GOOD: Use pytest.raises
def test_invalid_email_raises():
    with pytest.raises(ValidationError, match="Invalid email format"):
        validate_email("invalid")
```

---

## Quick Reference

### Test Markers

```bash
uv run pytest -m unit              # Unit tests only
uv run pytest -m integration       # Integration tests
uv run pytest -m "not slow"        # Exclude slow tests
uv run pytest -m "unit and db"     # Combine markers
```

### Coverage Commands

```bash
uv run pytest --cov=src/           # Basic coverage
uv run pytest --cov --cov-branch   # Branch coverage
uv run pytest --cov-fail-under=85  # Enforce threshold
uv run pytest --cov-report=html    # HTML report
```

### Test Categories

| Category | Purpose | Markers | Speed |
|----------|---------|---------|-------|
| Unit | Isolated logic | `@pytest.mark.unit` | Fast (<1ms) |
| Integration | Service interaction | `@pytest.mark.integration` | Medium (<1s) |
| E2E | Full workflows | `@pytest.mark.e2e` | Slow (>1s) |
| Property | Invariant checking | `@pytest.mark.property` | Variable |

---

## Related Skills

- `test-ops` - CI/CD integration, GitHub Actions, GitLab CI
- `test-advanced` - Mutation testing, contract testing
- `test-load` - Load testing with Locust
- `test-chaos` - Chaos engineering and resilience testing
- `test-data` - Test data management and factories
