---
name: arch-microservices
description: >
  Microservices architecture patterns for distributed systems. Covers Saga pattern
  for distributed transactions, Circuit Breaker for resilience, and 12-Factor App
  principles for cloud-native applications.
version: "2.0"
source: mixed
related:
  - arch-cqrs-es
  - api-grpc
  - api-gateway
  - perf-apm
---

## MICROSERVICES PATTERNS

Patterns for building and operating distributed systems.

---

### Saga Pattern

Manage distributed transactions across services without two-phase commit.

```python
from enum import Enum
from dataclasses import dataclass


class SagaStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"


@dataclass
class SagaStep:
    name: str
    execute: Callable
    compensate: Callable
    status: SagaStatus = SagaStatus.PENDING


class OrderSaga:
    """Saga for order creation across multiple services."""
    
    def __init__(
        self,
        inventory_service: InventoryService,
        payment_service: PaymentService,
        shipping_service: ShippingService,
    ):
        self._steps = [
            SagaStep(
                name="reserve_inventory",
                execute=inventory_service.reserve,
                compensate=inventory_service.release,
            ),
            SagaStep(
                name="process_payment",
                execute=payment_service.charge,
                compensate=payment_service.refund,
            ),
            SagaStep(
                name="create_shipment",
                execute=shipping_service.create,
                compensate=shipping_service.cancel,
            ),
        ]
    
    async def execute(self, order: Order) -> SagaResult:
        """Execute saga steps, compensate on failure."""
        completed_steps = []
        
        try:
            for step in self._steps:
                await step.execute(order)
                step.status = SagaStatus.COMPLETED
                completed_steps.append(step)
            
            return SagaResult.success()
            
        except Exception as e:
            # Compensate in reverse order
            for step in reversed(completed_steps):
                try:
                    step.status = SagaStatus.COMPENSATING
                    await step.compensate(order)
                except Exception as comp_error:
                    logger.error(f"Compensation failed for {step.name}: {comp_error}")
            
            return SagaResult.failure(str(e))
```

**Saga Types:**

| Type | Description | Use When |
|------|-------------|----------|
| **Choreography** | Services react to events | Simple flows, loose coupling |
| **Orchestration** | Central coordinator | Complex flows, visibility needed |

---

### Circuit Breaker

Prevent cascade failures in distributed systems.

```python
import asyncio
from datetime import datetime, timedelta
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: timedelta = timedelta(seconds=30),
        half_open_max_calls: int = 3,
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: datetime | None = None
        self._half_open_calls = 0
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self._state == CircuitState.OPEN:
            if self._should_try_recovery():
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
            else:
                raise CircuitOpenError("Circuit breaker is open")
        
        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self._half_open_max_calls:
                raise CircuitOpenError("Circuit breaker half-open limit reached")
            self._half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
        self._failure_count = 0
    
    def _on_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()
        
        if self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN
    
    def _should_try_recovery(self) -> bool:
        if self._last_failure_time is None:
            return True
        return datetime.utcnow() - self._last_failure_time > self._recovery_timeout


# Usage with decorator
def circuit_breaker(name: str):
    breaker = get_circuit_breaker(name)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


@circuit_breaker("payment-service")
async def process_payment(order: Order) -> PaymentResult:
    return await payment_client.charge(order)
```

**Circuit Breaker States:**

```
     success                    failure threshold
        │                             │
        ▼                             ▼
┌──────────────┐  failures   ┌──────────────┐
│    CLOSED    │ ─────────►  │     OPEN     │
│ (normal op)  │             │ (reject all) │
└──────────────┘             └──────────────┘
        ▲                             │
        │   success          timeout  │
        │                             ▼
        │                    ┌──────────────┐
        └─────────────────── │  HALF_OPEN   │
                             │ (test calls) │
                             └──────────────┘
```

---

## 12-FACTOR APP

Principles for building cloud-native applications.

---

### Quick Reference

| Factor | Principle | Python Implementation |
|--------|-----------|----------------------|
| **1. Codebase** | One codebase, many deploys | Git repo, branch per env |
| **2. Dependencies** | Explicitly declare dependencies | `pyproject.toml`, `uv.lock` |
| **3. Config** | Store config in environment | `os.environ`, `pydantic-settings` |
| **4. Backing Services** | Treat as attached resources | Connection URLs in config |
| **5. Build, Release, Run** | Strictly separate stages | CI/CD pipeline |
| **6. Processes** | Execute app as stateless processes | No local file storage |
| **7. Port Binding** | Export services via port binding | `uvicorn --host 0.0.0.0` |
| **8. Concurrency** | Scale out via process model | Multiple workers/containers |
| **9. Disposability** | Fast startup, graceful shutdown | Signal handlers |
| **10. Dev/Prod Parity** | Keep environments similar | Docker, same deps |
| **11. Logs** | Treat logs as event streams | stdout, log aggregation |
| **12. Admin Processes** | Run admin tasks as one-off | Management commands |

---

### Implementation Examples

```python
# Factor 3: Config from environment
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    
    model_config = {"env_prefix": "APP_"}


# Factor 9: Graceful shutdown
import signal
import asyncio


class GracefulShutdown:
    def __init__(self):
        self._shutdown = asyncio.Event()
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        self._shutdown.set()
    
    async def wait(self):
        await self._shutdown.wait()


async def main():
    shutdown = GracefulShutdown()
    server = await start_server()
    
    await shutdown.wait()
    
    # Graceful shutdown
    await server.stop(grace_period=10)
    await close_connections()


# Factor 11: Structured logging to stdout
import structlog


structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # JSON for log aggregation
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),  # stdout
)

logger = structlog.get_logger()
logger.info("order_created", order_id=order.id, total=float(order.total))
```

---

### 12-Factor Summary

```
1. Codebase      -> One repo, many deploys
2. Dependencies  -> Explicit in pyproject.toml
3. Config        -> Environment variables
4. Backing       -> URLs in config
5. Build/Run     -> Separate stages
6. Processes     -> Stateless
7. Port Binding  -> Self-contained
8. Concurrency   -> Process scaling
9. Disposability -> Fast start/stop
10. Dev/Prod     -> Keep similar
11. Logs         -> Stdout, JSON
12. Admin        -> One-off processes
```

---

## Quick Reference

### Microservices Patterns

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| **Saga** | Distributed transactions | Cross-service workflows |
| **Circuit Breaker** | Fault tolerance | External service calls |
| **Retry** | Transient failures | Network errors |
| **Bulkhead** | Isolation | Resource protection |
| **Sidecar** | Cross-cutting concerns | Logging, auth, metrics |

### Service Communication

| Style | Protocol | Use When |
|-------|----------|----------|
| Synchronous | HTTP/gRPC | Request-response needed |
| Asynchronous | Message Queue | Fire-and-forget, events |
| Event-driven | Kafka/RabbitMQ | Loose coupling, audit |

### Resilience Checklist

- [ ] Circuit breakers on external calls
- [ ] Timeouts on all network calls
- [ ] Retry with exponential backoff
- [ ] Graceful degradation
- [ ] Health checks (liveness + readiness)
- [ ] Structured logging
- [ ] Distributed tracing

---

## Related Skills

- `arch-principles` - Core principles, observability, feature flags
- `arch-hexagonal` - Ports & Adapters for service boundaries
- `arch-cqrs-es` - Event-driven patterns with CQRS
