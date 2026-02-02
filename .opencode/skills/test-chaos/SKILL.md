---
name: test-chaos
description: >
  Chaos engineering and resilience testing for Python applications. Covers chaos
  engineering principles, resilience testing with pytest, testing database failures,
  external service failures, network issues, circuit breakers, and Kubernetes
  chaos testing.
version: "2.0"
source: mixed
related:
  - test-load
  - arch-microservices
  - perf-apm
  - test-ops
---

## CHAOS ENGINEERING

Chaos engineering verifies system resilience by intentionally introducing failures.

---

### Principles of Chaos Engineering

| Principle | Description |
|-----------|-------------|
| **Build hypothesis** | Define steady state (normal behavior) |
| **Vary real-world events** | Simulate production failures |
| **Run in production** | Test where it matters most |
| **Automate continuously** | Regular chaos experiments |
| **Minimize blast radius** | Start small, expand gradually |

---

### Chaos Testing with pytest

```python
# tests/chaos/test_resilience.py
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
import random


@pytest.mark.chaos
class TestDatabaseResilience:
    """Test system behavior when database fails."""

    async def test_handles_database_timeout(self, client, db_session):
        """System returns cached data on database timeout."""
        # Seed cache
        await client.get("/users/1")
        
        # Simulate database timeout
        with patch.object(
            db_session, 
            "execute", 
            side_effect=asyncio.TimeoutError()
        ):
            response = await client.get("/users/1")
            
        assert response.status_code == 200
        assert response.headers.get("X-Cache") == "HIT"

    async def test_graceful_degradation_on_db_failure(self, client):
        """System degrades gracefully when database is down."""
        with patch(
            "mypackage.db.get_session",
            side_effect=ConnectionError("Database unavailable")
        ):
            response = await client.get("/health")
            
        # Should return degraded status, not 500
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "unavailable"


@pytest.mark.chaos
class TestExternalServiceResilience:
    """Test behavior when external services fail."""

    async def test_circuit_breaker_opens_on_failures(self, client):
        """Circuit breaker prevents cascade failures."""
        # Simulate 5 consecutive failures
        with patch(
            "mypackage.services.payment.process",
            side_effect=Exception("Payment service down")
        ):
            for _ in range(5):
                await client.post("/orders/1/pay")
        
        # Circuit should be open - fast fail without calling service
        response = await client.post("/orders/1/pay")
        
        assert response.status_code == 503
        assert "circuit open" in response.json()["detail"].lower()

    async def test_retry_with_backoff(self, client, mocker):
        """Transient failures are retried with backoff."""
        call_count = 0
        
        async def flaky_service():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return {"status": "success"}
        
        mocker.patch(
            "mypackage.services.external.call",
            side_effect=flaky_service
        )
        
        response = await client.post("/process")
        
        assert response.status_code == 200
        assert call_count == 3  # Retried twice


@pytest.mark.chaos
class TestNetworkChaos:
    """Test behavior under network issues."""

    async def test_handles_high_latency(self, client):
        """System handles high latency gracefully."""
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(2)  # 2 second delay
            return {"data": "delayed"}
        
        with patch(
            "mypackage.services.external.fetch",
            side_effect=slow_response
        ):
            response = await asyncio.wait_for(
                client.get("/data"),
                timeout=5.0
            )
            
        assert response.status_code == 200

    async def test_handles_packet_loss(self, client, mocker):
        """System handles intermittent connectivity."""
        call_count = 0
        
        async def lossy_connection(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if random.random() < 0.5:  # 50% packet loss
                raise ConnectionResetError("Connection reset")
            return {"data": "success"}
        
        mocker.patch(
            "mypackage.services.external.fetch",
            side_effect=lossy_connection
        )
        
        # Should eventually succeed despite losses
        response = await client.get("/data")
        assert response.status_code in [200, 503]
```

---

### Testing Circuit Breaker Patterns

```python
@pytest.mark.chaos
class TestCircuitBreaker:
    """Test circuit breaker behavior."""
    
    async def test_circuit_opens_after_threshold(self, circuit_breaker):
        """Circuit opens after failure threshold."""
        # Fail 5 times (threshold)
        for _ in range(5):
            with pytest.raises(ServiceError):
                await circuit_breaker.call(failing_service)
        
        # Circuit should be open
        assert circuit_breaker.state == "open"
        
        # Calls should fail fast
        with pytest.raises(CircuitOpenError):
            await circuit_breaker.call(failing_service)
    
    async def test_circuit_half_opens_after_timeout(self, circuit_breaker):
        """Circuit transitions to half-open after timeout."""
        # Open the circuit
        for _ in range(5):
            with pytest.raises(ServiceError):
                await circuit_breaker.call(failing_service)
        
        # Wait for reset timeout
        await asyncio.sleep(circuit_breaker.reset_timeout)
        
        # Circuit should be half-open
        assert circuit_breaker.state == "half-open"
    
    async def test_circuit_closes_on_success(self, circuit_breaker):
        """Circuit closes after successful call in half-open state."""
        # Get to half-open state
        for _ in range(5):
            with pytest.raises(ServiceError):
                await circuit_breaker.call(failing_service)
        await asyncio.sleep(circuit_breaker.reset_timeout)
        
        # Successful call should close circuit
        await circuit_breaker.call(working_service)
        
        assert circuit_breaker.state == "closed"
```

---

### Chaos Monkey for Kubernetes

```python
# tests/chaos/conftest.py
import pytest
from kubernetes import client, config


@pytest.fixture
def k8s_client():
    """Kubernetes client for chaos testing."""
    config.load_kube_config()
    return client.CoreV1Api()


@pytest.fixture
def pod_chaos(k8s_client):
    """Helper for pod-level chaos."""
    class PodChaos:
        def __init__(self, namespace: str = "default"):
            self.namespace = namespace
            self.k8s = k8s_client
            
        def kill_random_pod(self, label_selector: str) -> str:
            """Kill a random pod matching selector."""
            pods = self.k8s.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=label_selector,
            )
            if not pods.items:
                raise ValueError(f"No pods found for {label_selector}")
                
            victim = random.choice(pods.items)
            self.k8s.delete_namespaced_pod(
                name=victim.metadata.name,
                namespace=self.namespace,
            )
            return victim.metadata.name
            
        def add_network_delay(self, pod_name: str, delay_ms: int):
            """Add network delay to pod."""
            # Uses tc (traffic control) via exec
            self.k8s.connect_get_namespaced_pod_exec(
                name=pod_name,
                namespace=self.namespace,
                command=[
                    "tc", "qdisc", "add", "dev", "eth0",
                    "root", "netem", "delay", f"{delay_ms}ms"
                ],
            )
    
    return PodChaos()


@pytest.mark.chaos
@pytest.mark.kubernetes
async def test_survives_pod_failure(client, pod_chaos):
    """Application survives pod being killed."""
    # Verify initial health
    response = await client.get("/health")
    assert response.status_code == 200
    
    # Kill a pod
    killed = pod_chaos.kill_random_pod("app=myservice")
    print(f"Killed pod: {killed}")
    
    # Wait for recovery
    await asyncio.sleep(10)
    
    # Should still be healthy
    response = await client.get("/health")
    assert response.status_code == 200
```

---

### Failure Injection Patterns

```python
class FailureInjector:
    """Inject various failure modes for testing."""
    
    def __init__(self, failure_rate: float = 0.1):
        self.failure_rate = failure_rate
        self.enabled = False
    
    def maybe_fail(self, failure_type: str = "exception"):
        """Randomly inject failures."""
        if not self.enabled:
            return
            
        if random.random() < self.failure_rate:
            if failure_type == "exception":
                raise RuntimeError("Injected failure")
            elif failure_type == "timeout":
                time.sleep(30)
            elif failure_type == "corrupt":
                return {"corrupted": True}
    
    async def maybe_fail_async(self, failure_type: str = "exception"):
        """Async version of failure injection."""
        if not self.enabled:
            return
            
        if random.random() < self.failure_rate:
            if failure_type == "exception":
                raise RuntimeError("Injected failure")
            elif failure_type == "timeout":
                await asyncio.sleep(30)


# Usage in tests
@pytest.fixture
def failure_injector():
    injector = FailureInjector(failure_rate=0.3)
    injector.enabled = True
    yield injector
    injector.enabled = False


@pytest.mark.chaos
async def test_handles_random_failures(client, failure_injector):
    """System handles random failures gracefully."""
    successes = 0
    failures = 0
    
    for _ in range(100):
        try:
            response = await client.get("/data")
            if response.status_code == 200:
                successes += 1
            else:
                failures += 1
        except Exception:
            failures += 1
    
    # Should have some successes despite failures
    assert successes > 50
```

---

### Chaos Experiment Structure

```python
class ChaosExperiment:
    """Structure for chaos experiments."""
    
    def __init__(self, name: str, hypothesis: str):
        self.name = name
        self.hypothesis = hypothesis
        self.steady_state = None
        self.results = []
    
    async def define_steady_state(self, check_fn):
        """Define what normal looks like."""
        self.steady_state = await check_fn()
        return self.steady_state
    
    async def inject_chaos(self, chaos_fn):
        """Inject the chaos."""
        return await chaos_fn()
    
    async def verify_hypothesis(self, check_fn):
        """Verify system recovered."""
        current_state = await check_fn()
        return current_state == self.steady_state


# Example experiment
@pytest.mark.chaos
async def test_database_failure_experiment(client, db):
    """Chaos experiment: database failure."""
    experiment = ChaosExperiment(
        name="Database Failure",
        hypothesis="System returns cached data when DB fails"
    )
    
    # 1. Define steady state
    async def check_steady_state():
        response = await client.get("/users/1")
        return response.status_code == 200
    
    steady = await experiment.define_steady_state(check_steady_state)
    assert steady, "System not in steady state"
    
    # 2. Inject chaos
    async def kill_database():
        await db.disconnect()
        return True
    
    await experiment.inject_chaos(kill_database)
    
    # 3. Verify hypothesis
    verified = await experiment.verify_hypothesis(check_steady_state)
    assert verified, "System did not maintain steady state"
```

---

## Quick Reference

### Chaos Test Markers

```python
@pytest.mark.chaos           # Chaos engineering test
@pytest.mark.kubernetes      # Requires K8s
@pytest.mark.slow            # Long-running chaos test
```

### Common Failure Modes

| Failure Mode | Simulation | What It Tests |
|--------------|------------|---------------|
| Service down | `side_effect=ConnectionError` | Graceful degradation |
| Timeout | `asyncio.sleep(30)` | Timeout handling |
| Partial failure | Random `raise` | Retry logic |
| Slow response | `asyncio.sleep(2)` | Latency tolerance |
| Data corruption | Return invalid data | Validation |

### Resilience Patterns to Test

| Pattern | Test |
|---------|------|
| Circuit Breaker | Opens after failures, closes on success |
| Retry | Retries transient failures with backoff |
| Timeout | Fails fast on slow responses |
| Bulkhead | Isolates failures to prevent cascade |
| Fallback | Returns cached/default on failure |

---

## Related Skills

- `test-standards` - Testing fundamentals and patterns
- `test-ops` - CI/CD integration
- `test-advanced` - Mutation and contract testing
- `test-load` - Performance testing
- `test-data` - Test data management
- `arch-microservices` - Circuit breaker, saga patterns
