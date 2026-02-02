---
name: test-load
description: >
  Load and performance testing for Python applications. Covers load testing with
  Locust, performance test assertions, SLA verification, CI integration for
  performance testing, and distributed load testing.
version: "2.0"
source: locust
related:
  - test-ops
  - perf-ops
  - perf-slo
  - test-chaos
---

## LOAD AND PERFORMANCE TESTING

Performance testing ensures your application handles expected load.

---

### Load Testing with Locust

**Basic load test:**
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between, tag
from locust.contrib.fasthttp import FastHttpUser


class APIUser(FastHttpUser):
    """Simulate typical API user behavior."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login and get token on user start."""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(10)
    @tag("read")
    def list_items(self):
        """Most common operation - list items."""
        self.client.get("/items", headers=self.headers)

    @task(5)
    @tag("read")
    def get_item(self):
        """Get single item."""
        self.client.get("/items/1", headers=self.headers)

    @task(2)
    @tag("write")
    def create_item(self):
        """Create new item (less frequent)."""
        self.client.post(
            "/items",
            headers=self.headers,
            json={"name": "Test Item", "price": 100},
        )

    @task(1)
    @tag("search")
    def search_items(self):
        """Search operation (expensive)."""
        self.client.get(
            "/items/search",
            headers=self.headers,
            params={"q": "test"},
        )


class AdminUser(FastHttpUser):
    """Simulate admin operations (less frequent)."""
    
    wait_time = between(5, 10)
    weight = 1  # 1/10 of regular users
    
    def on_start(self):
        response = self.client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123",
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def view_dashboard(self):
        self.client.get("/admin/dashboard", headers=self.headers)

    @task
    def export_report(self):
        self.client.get("/admin/reports/export", headers=self.headers)
```

---

### Running Load Tests

```bash
# Local testing with web UI
uv run locust -f tests/load/locustfile.py --host=http://localhost:8000

# Headless CI mode
uv run locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --csv=results/load_test \
    --html=results/report.html

# Distributed mode (multiple workers)
uv run locust -f tests/load/locustfile.py --master
uv run locust -f tests/load/locustfile.py --worker --master-host=localhost
```

---

### Performance Test Assertions

```python
# tests/load/test_performance.py
import subprocess
import json
import pytest


def run_locust(users: int, duration: str) -> dict:
    """Run locust and return statistics."""
    result = subprocess.run([
        "uv", "run", "locust",
        "-f", "tests/load/locustfile.py",
        "--host=http://localhost:8000",
        "--headless",
        f"--users={users}",
        "--spawn-rate=10",
        f"--run-time={duration}",
        "--csv=results/perf",
        "--json",
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)


@pytest.mark.performance
def test_api_response_times():
    """Verify API meets response time SLAs."""
    stats = run_locust(users=50, duration="2m")
    
    # P50 < 100ms
    assert stats["percentile_50"] < 100, \
        f"P50 latency {stats['percentile_50']}ms exceeds 100ms"
    
    # P95 < 500ms
    assert stats["percentile_95"] < 500, \
        f"P95 latency {stats['percentile_95']}ms exceeds 500ms"
    
    # P99 < 1000ms
    assert stats["percentile_99"] < 1000, \
        f"P99 latency {stats['percentile_99']}ms exceeds 1000ms"
    
    # Error rate < 1%
    error_rate = stats["num_failures"] / stats["num_requests"] * 100
    assert error_rate < 1, f"Error rate {error_rate}% exceeds 1%"


@pytest.mark.performance
def test_throughput_under_load():
    """Verify system handles expected throughput."""
    stats = run_locust(users=100, duration="5m")
    
    # At least 500 requests per second
    assert stats["requests_per_second"] >= 500, \
        f"Throughput {stats['requests_per_second']} RPS below 500 RPS"
```

---

### Load Test CI Integration

```yaml
# .github/workflows/performance.yml
performance-tests:
  runs-on: ubuntu-latest
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4
    
    - name: Start application
      run: docker compose up -d
      
    - name: Wait for application
      run: |
        for i in {1..30}; do
          curl -sf http://localhost:8000/health && break
          sleep 2
        done
        
    - name: Run load tests
      run: |
        uv run locust -f tests/load/locustfile.py \
          --host=http://localhost:8000 \
          --headless \
          --users 50 \
          --spawn-rate 5 \
          --run-time 3m \
          --csv=results/load \
          --html=results/report.html
          
    - name: Check performance thresholds
      run: uv run pytest tests/load/test_performance.py -v
      
    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: performance-results
        path: results/
        
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const stats = fs.readFileSync('results/load_stats.csv', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## Performance Test Results\n\`\`\`\n${stats}\n\`\`\``
          });
```

---

### Advanced Locust Patterns

**Sequential task flow:**
```python
from locust import SequentialTaskSet

class CheckoutFlow(SequentialTaskSet):
    """Tasks that must run in order."""
    
    @task
    def add_to_cart(self):
        self.client.post("/cart/items", json={"product_id": 1})
    
    @task
    def view_cart(self):
        self.client.get("/cart")
    
    @task
    def checkout(self):
        self.client.post("/checkout")
    
    @task
    def confirm_order(self):
        self.client.post("/orders/confirm")
```

**Custom metrics:**
```python
from locust import events
import time

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    """Track custom metrics."""
    if name == "/search":
        # Track search-specific metrics
        custom_metrics["search_latency"].append(response_time)


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    """Report custom metrics at end."""
    avg_search = sum(custom_metrics["search_latency"]) / len(custom_metrics["search_latency"])
    print(f"Average search latency: {avg_search:.2f}ms")
```

**Ramping users:**
```python
from locust import LoadTestShape

class StagesShape(LoadTestShape):
    """Ramp up, hold, ramp down."""
    
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 1},   # Warm up
        {"duration": 120, "users": 50, "spawn_rate": 5},  # Ramp up
        {"duration": 300, "users": 100, "spawn_rate": 10}, # Peak load
        {"duration": 60, "users": 10, "spawn_rate": 5},   # Ramp down
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]
        
        return None  # Stop test
```

---

### Performance SLA Definitions

| Metric | Definition | Typical SLA |
|--------|------------|-------------|
| P50 (Median) | 50% of requests faster | < 100ms |
| P95 | 95% of requests faster | < 500ms |
| P99 | 99% of requests faster | < 1000ms |
| Error Rate | Failed requests / total | < 1% |
| Throughput | Requests per second | > 500 RPS |
| Availability | Uptime percentage | > 99.9% |

---

### Distributed Load Testing

```yaml
# docker-compose.locust.yml
version: "3.8"

services:
  master:
    image: locustio/locust
    ports:
      - "8089:8089"
    volumes:
      - ./tests/load:/mnt/locust
    command: -f /mnt/locust/locustfile.py --master -H http://target:8000
    
  worker:
    image: locustio/locust
    volumes:
      - ./tests/load:/mnt/locust
    command: -f /mnt/locust/locustfile.py --worker --master-host master
    deploy:
      replicas: 4  # 4 worker instances
```

---

## Quick Reference

### Locust Commands

```bash
# Web UI mode
uv run locust -f locustfile.py --host=http://localhost:8000

# Headless mode
uv run locust -f locustfile.py --headless \
  --users 100 --spawn-rate 10 --run-time 5m

# With reports
uv run locust -f locustfile.py --headless \
  --csv=results --html=report.html

# Distributed
uv run locust -f locustfile.py --master
uv run locust -f locustfile.py --worker --master-host=localhost

# Tag filtering
uv run locust -f locustfile.py --tags read  # Only read tasks
uv run locust -f locustfile.py --exclude-tags write  # Exclude writes
```

### Task Weights

```python
@task(10)  # 10x more likely than weight 1
def common_operation(self): ...

@task(1)   # Baseline weight
def rare_operation(self): ...
```

### Wait Time Patterns

```python
from locust import between, constant, constant_pacing

wait_time = between(1, 5)        # Random 1-5 seconds
wait_time = constant(2)          # Always 2 seconds
wait_time = constant_pacing(1)   # 1 request per second (adjusts for response time)
```

---

## Related Skills

- `test-standards` - Testing fundamentals and patterns
- `test-ops` - CI/CD integration
- `test-advanced` - Mutation and contract testing
- `test-chaos` - Chaos engineering
- `test-data` - Test data management
