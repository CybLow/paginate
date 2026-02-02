---
name: test-data
description: >
  Test data management for Python applications. Covers test data strategies,
  factory pattern with factory_boy, database seeding, test data isolation,
  visual regression testing with Playwright, test reporting and metrics,
  and test quality dashboards.
version: "2.0"
source: mixed
related:
  - test-standards
  - test-ops
  - perf-database
  - guru-patterns-creational
---

## TEST DATA MANAGEMENT

Effective test data strategies ensure reproducible, maintainable tests.

---

### Test Data Strategies

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Factories** | Unit tests, isolated data | factory_boy, Faker |
| **Fixtures** | Shared setup, common objects | pytest fixtures |
| **Snapshots** | Complex objects, API responses | syrupy |
| **Seeds** | Integration tests, known state | Database seeds |
| **Anonymized** | Production-like data | Data masking |

---

### Factory Pattern with factory_boy

```python
# tests/factories.py
from __future__ import annotations
import factory
from factory import fuzzy
from datetime import datetime, timedelta
from mypackage.models import User, Order, Product, OrderItem


class UserFactory(factory.Factory):
    """Generate test users."""
    
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda o: f"user{o.id}@example.com")
    name = factory.Faker("name")
    created_at = factory.LazyFunction(datetime.utcnow)
    status = "active"

    class Params:
        # Traits for common variations
        premium = factory.Trait(
            subscription_tier="premium",
            credits=1000,
        )
        inactive = factory.Trait(
            status="inactive",
            deactivated_at=factory.LazyFunction(datetime.utcnow),
        )


class ProductFactory(factory.Factory):
    """Generate test products."""
    
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("catch_phrase")
    price = fuzzy.FuzzyInteger(100, 10000)
    stock = fuzzy.FuzzyInteger(0, 100)
    category = fuzzy.FuzzyChoice(["electronics", "clothing", "books"])


class OrderItemFactory(factory.Factory):
    """Generate order items."""
    
    class Meta:
        model = OrderItem

    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    unit_price = factory.LazyAttribute(lambda o: o.product.price)


class OrderFactory(factory.Factory):
    """Generate test orders."""
    
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n + 1)
    user = factory.SubFactory(UserFactory)
    status = "pending"
    created_at = factory.LazyFunction(datetime.utcnow)
    
    @factory.lazy_attribute
    def items(self):
        return [OrderItemFactory() for _ in range(3)]

    class Params:
        completed = factory.Trait(
            status="completed",
            completed_at=factory.LazyFunction(datetime.utcnow),
        )
        with_discount = factory.Trait(
            discount_code="SAVE10",
            discount_percent=10,
        )


# Usage in tests
class TestOrderProcessing:
    def test_order_total_calculation(self):
        order = OrderFactory(
            items=[
                OrderItemFactory(unit_price=1000, quantity=2),
                OrderItemFactory(unit_price=500, quantity=1),
            ]
        )
        
        assert order.calculate_total() == 2500

    def test_premium_user_gets_discount(self):
        user = UserFactory(premium=True)
        order = OrderFactory(user=user)
        
        discount = order.calculate_premium_discount()
        
        assert discount > 0
```

---

### Database Seeding

```python
# tests/seeds.py
from mypackage.models import User, Product, Category


class DatabaseSeeder:
    """Seed database with test data."""
    
    def __init__(self, session):
        self.session = session

    def seed_all(self):
        """Seed all test data."""
        self.seed_categories()
        self.seed_products()
        self.seed_users()

    def seed_categories(self):
        """Seed product categories."""
        categories = [
            Category(id=1, name="Electronics", slug="electronics"),
            Category(id=2, name="Clothing", slug="clothing"),
            Category(id=3, name="Books", slug="books"),
        ]
        self.session.add_all(categories)
        self.session.commit()

    def seed_products(self):
        """Seed products."""
        products = [
            Product(
                id=1,
                name="Laptop",
                price=99900,
                category_id=1,
                stock=50,
            ),
            Product(
                id=2,
                name="T-Shirt",
                price=2500,
                category_id=2,
                stock=200,
            ),
        ]
        self.session.add_all(products)
        self.session.commit()

    def seed_users(self):
        """Seed test users."""
        users = [
            User(
                id=1,
                email="admin@example.com",
                name="Admin User",
                role="admin",
            ),
            User(
                id=2,
                email="user@example.com",
                name="Regular User",
                role="user",
            ),
        ]
        self.session.add_all(users)
        self.session.commit()


# conftest.py
@pytest.fixture
def seeded_db(db_session):
    """Database with seed data."""
    seeder = DatabaseSeeder(db_session)
    seeder.seed_all()
    yield db_session
```

---

### Test Data Isolation

```python
# conftest.py
import pytest
from sqlalchemy import event


@pytest.fixture
def db_session(engine):
    """Isolated database session with automatic rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create session bound to transaction
    session = Session(bind=connection)
    
    # Begin nested transaction (savepoint)
    nested = connection.begin_nested()
    
    # Restart savepoint after each commit
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        nonlocal nested
        if transaction.nested and not transaction._parent.nested:
            nested = connection.begin_nested()
    
    yield session
    
    # Rollback everything
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def isolated_redis(redis_client):
    """Isolated Redis with automatic cleanup."""
    # Use unique prefix for this test
    prefix = f"test:{uuid.uuid4().hex}:"
    
    class IsolatedRedis:
        def __init__(self, client, prefix):
            self._client = client
            self._prefix = prefix
            self._keys = set()
        
        def set(self, key, value):
            full_key = f"{self._prefix}{key}"
            self._keys.add(full_key)
            return self._client.set(full_key, value)
        
        def get(self, key):
            return self._client.get(f"{self._prefix}{key}")
    
    isolated = IsolatedRedis(redis_client, prefix)
    yield isolated
    
    # Cleanup all keys created during test
    if isolated._keys:
        redis_client.delete(*isolated._keys)
```

---

## VISUAL REGRESSION TESTING

Visual regression testing catches unintended UI changes.

---

### Screenshot Comparison with pytest-playwright

```python
# tests/visual/test_ui.py
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.visual
class TestVisualRegression:
    """Visual regression tests for UI components."""

    def test_login_page_appearance(self, page: Page):
        """Login page matches expected design."""
        page.goto("/login")
        
        # Wait for page to stabilize
        page.wait_for_load_state("networkidle")
        
        # Compare screenshot
        expect(page).to_have_screenshot("login-page.png")

    def test_dashboard_layout(self, page: Page, auth_user):
        """Dashboard layout matches expected design."""
        page.goto("/dashboard")
        page.wait_for_selector("[data-testid='dashboard-loaded']")
        
        # Full page screenshot
        expect(page).to_have_screenshot(
            "dashboard.png",
            full_page=True,
            mask=[page.locator("[data-testid='dynamic-content']")],
        )

    def test_mobile_navigation(self, page: Page):
        """Mobile nav menu renders correctly."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("/")
        
        # Open mobile menu
        page.click("[data-testid='mobile-menu-toggle']")
        page.wait_for_selector("[data-testid='mobile-menu']")
        
        expect(page).to_have_screenshot("mobile-nav-open.png")

    def test_component_states(self, page: Page):
        """Test button states visually."""
        page.goto("/components/buttons")
        
        # Default state
        expect(page.locator(".btn-primary")).to_have_screenshot(
            "button-default.png"
        )
        
        # Hover state
        page.hover(".btn-primary")
        expect(page.locator(".btn-primary")).to_have_screenshot(
            "button-hover.png"
        )
        
        # Disabled state
        expect(page.locator(".btn-disabled")).to_have_screenshot(
            "button-disabled.png"
        )
```

---

### Visual Test Configuration

```python
# conftest.py
import pytest
from playwright.sync_api import Browser


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser for consistent screenshots."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "device_scale_factor": 1,
        "color_scheme": "light",
        "reduced_motion": "reduce",  # Disable animations
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }


@pytest.fixture
def page(browser: Browser, browser_context_args):
    """Page with consistent settings."""
    context = browser.new_context(**browser_context_args)
    
    # Disable animations for consistent screenshots
    context.add_init_script("""
        document.addEventListener('DOMContentLoaded', () => {
            const style = document.createElement('style');
            style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0s !important;
                    transition-duration: 0s !important;
                }
            `;
            document.head.appendChild(style);
        });
    """)
    
    page = context.new_page()
    yield page
    context.close()
```

---

### CI Visual Testing

```yaml
# .github/workflows/visual.yml
visual-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Install dependencies
      run: |
        uv sync --frozen
        uv run playwright install chromium
        
    - name: Run visual tests
      run: uv run pytest tests/visual --update-snapshots=none
      
    - name: Upload diff images
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: visual-diffs
        path: tests/visual/__screenshots__/*-diff.png
```

---

## TEST REPORTING AND METRICS

Track test quality and trends over time.

---

### pytest Reporting Plugins

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--junitxml=reports/junit.xml",     # CI integration
    "--html=reports/report.html",        # Human-readable
    "--cov-report=html:reports/coverage", # Coverage
    "--cov-report=xml:reports/coverage.xml",
]
```

---

### Custom Test Metrics

```python
# conftest.py
import pytest
import time
import json
from pathlib import Path


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect detailed test metrics."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        metrics = getattr(item.config, "_test_metrics", {})
        
        test_id = f"{item.module.__name__}::{item.name}"
        metrics[test_id] = {
            "name": item.name,
            "module": item.module.__name__,
            "duration": report.duration,
            "outcome": report.outcome,
            "markers": [m.name for m in item.iter_markers()],
        }
        
        item.config._test_metrics = metrics


def pytest_sessionfinish(session, exitstatus):
    """Save metrics at end of session."""
    metrics = getattr(session.config, "_test_metrics", {})
    
    summary = {
        "total": len(metrics),
        "passed": sum(1 for m in metrics.values() if m["outcome"] == "passed"),
        "failed": sum(1 for m in metrics.values() if m["outcome"] == "failed"),
        "skipped": sum(1 for m in metrics.values() if m["outcome"] == "skipped"),
        "total_duration": sum(m["duration"] for m in metrics.values()),
        "slowest_tests": sorted(
            metrics.items(),
            key=lambda x: x[1]["duration"],
            reverse=True
        )[:10],
        "tests": metrics,
    }
    
    Path("reports").mkdir(exist_ok=True)
    Path("reports/metrics.json").write_text(json.dumps(summary, indent=2))
```

---

### Test Quality Dashboard

```python
# scripts/test_dashboard.py
"""Generate test quality dashboard."""
import json
from pathlib import Path
from datetime import datetime


def generate_dashboard():
    """Generate HTML dashboard from test metrics."""
    metrics = json.loads(Path("reports/metrics.json").read_text())
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Quality Dashboard</title>
        <style>
            body {{ font-family: sans-serif; margin: 2rem; }}
            .metric {{ display: inline-block; padding: 1rem; margin: 0.5rem; 
                       background: #f0f0f0; border-radius: 8px; }}
            .metric.passed {{ background: #d4edda; }}
            .metric.failed {{ background: #f8d7da; }}
            .slow-test {{ padding: 0.5rem; margin: 0.25rem 0; background: #fff3cd; }}
        </style>
    </head>
    <body>
        <h1>Test Quality Dashboard</h1>
        <p>Generated: {datetime.now().isoformat()}</p>
        
        <h2>Summary</h2>
        <div class="metric passed">Passed: {metrics['passed']}</div>
        <div class="metric failed">Failed: {metrics['failed']}</div>
        <div class="metric">Skipped: {metrics['skipped']}</div>
        <div class="metric">Duration: {metrics['total_duration']:.2f}s</div>
        
        <h2>Slowest Tests</h2>
        {"".join(f'''
        <div class="slow-test">
            <strong>{name}</strong>: {data['duration']:.3f}s
        </div>
        ''' for name, data in metrics['slowest_tests'])}
    </body>
    </html>
    """
    
    Path("reports/dashboard.html").write_text(html)


if __name__ == "__main__":
    generate_dashboard()
```

---

### Tracking Test Trends

```yaml
# Store metrics for trend analysis
- name: Store test metrics
  uses: actions/upload-artifact@v4
  with:
    name: test-metrics-${{ github.sha }}
    path: reports/metrics.json
    retention-days: 90

# Compare with baseline
- name: Compare test metrics
  run: |
    python scripts/compare_metrics.py \
      --baseline reports/baseline-metrics.json \
      --current reports/metrics.json \
      --threshold-duration 1.1  # 10% slower
      --threshold-coverage 0.85  # 85% minimum
```

---

## Quick Reference

### Factory Patterns

```python
# Basic factory
user = UserFactory()

# With overrides
user = UserFactory(email="custom@example.com")

# With traits
user = UserFactory(premium=True)

# Batch create
users = UserFactory.build_batch(10)

# Create in database (SQLAlchemy)
user = UserFactory.create()
```

### Test Data Commands

```bash
# Update visual snapshots
uv run pytest tests/visual --update-snapshots

# Generate test report
uv run pytest --html=report.html

# Run with coverage
uv run pytest --cov --cov-report=html
```

### Factory Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `Sequence` | Auto-increment | `id = Sequence(lambda n: n)` |
| `LazyAttribute` | Computed value | `email = LazyAttribute(...)` |
| `Faker` | Random data | `name = Faker("name")` |
| `SubFactory` | Nested factory | `user = SubFactory(UserFactory)` |
| `FuzzyChoice` | Random choice | `status = FuzzyChoice([...])` |
| `Trait` | Named variations | `premium = Trait(...)` |

---

## Related Skills

- `test-standards` - Testing fundamentals and patterns
- `test-ops` - CI/CD integration
- `test-advanced` - Mutation and contract testing
- `test-load` - Performance testing
- `test-chaos` - Chaos engineering
