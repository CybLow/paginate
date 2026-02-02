---
name: perf-apm
description: >
  Application Performance Monitoring with OpenTelemetry. Covers tracing setup,
  custom metrics, distributed tracing, and instrumentation for FastAPI, SQLAlchemy, and more.
related:
  - perf-core
  - perf-slo
  - perf-profiling
  - arch-microservices
---

## APM AND OBSERVABILITY

Application Performance Monitoring with OpenTelemetry.

---

### OpenTelemetry Setup

```python
# src/observability/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor


def setup_tracing(app, service_name: str, otlp_endpoint: str) -> None:
    """Configure OpenTelemetry tracing."""
    # Create resource with service info
    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("APP_VERSION", "unknown"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })
    
    # Configure tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter (Jaeger, Tempo, etc.)
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    trace.set_tracer_provider(provider)
    
    # Auto-instrument frameworks
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()


# Get tracer for manual instrumentation
tracer = trace.get_tracer(__name__)


# Manual span creation
async def process_order(order_id: int) -> Order:
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        
        # Nested span for sub-operation
        with tracer.start_as_current_span("validate_order"):
            order = await validate_order(order_id)
        
        with tracer.start_as_current_span("charge_payment"):
            await charge_payment(order)
        
        with tracer.start_as_current_span("send_confirmation"):
            await send_confirmation(order)
        
        span.set_attribute("order.total", float(order.total))
        return order
```

### Custom Metrics

```python
# src/observability/metrics.py
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


def setup_metrics(service_name: str, otlp_endpoint: str) -> None:
    """Configure OpenTelemetry metrics."""
    exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=60000)
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)


# Create meter
meter = metrics.get_meter(__name__)

# Define metrics
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
    unit="requests",
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration",
    unit="seconds",
)

active_connections = meter.create_up_down_counter(
    name="active_connections",
    description="Number of active connections",
    unit="connections",
)

cache_hit_ratio = meter.create_observable_gauge(
    name="cache_hit_ratio",
    description="Cache hit ratio",
    callbacks=[lambda: get_cache_hit_ratio()],
)


# Middleware for automatic metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        duration = time.perf_counter() - start_time
        
        attributes = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        }
        
        request_counter.add(1, attributes)
        request_duration.record(duration, attributes)
        
        return response
```

### Distributed Tracing

```python
# Propagate trace context across services
from opentelemetry import trace
from opentelemetry.propagate import inject, extract


async def call_external_service(order_id: int) -> dict:
    """Call external service with trace propagation."""
    headers = {}
    
    # Inject current trace context into headers
    inject(headers)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://payment-service.internal/charge",
            json={"order_id": order_id},
            headers=headers,  # Trace context propagated
        )
        return response.json()


# Receive trace context from upstream
@app.post("/charge")
async def charge(request: Request, body: ChargeRequest):
    # Extract trace context from incoming request
    context = extract(request.headers)
    
    with tracer.start_as_current_span("charge", context=context) as span:
        span.set_attribute("order.id", body.order_id)
        # Process with same trace ID as caller
        return await process_charge(body)
```

---

## STRUCTURED LOGGING

### Integration with Tracing

```python
import structlog
from opentelemetry import trace


def add_trace_context(logger, method_name, event_dict):
    """Add trace context to log entries."""
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        add_trace_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()

# Logs will include trace context
logger.info("order_processed", order_id=123, total=99.99)
# Output: {"event": "order_processed", "order_id": 123, "total": 99.99,
#          "trace_id": "abc123...", "span_id": "def456...", "timestamp": "..."}
```

---

## HEALTH CHECKS

### Liveness and Readiness

```python
from fastapi import APIRouter, Response

health_router = APIRouter(tags=["health"])


@health_router.get("/health/live")
async def liveness():
    """Liveness probe - is the process running?"""
    return {"status": "alive"}


@health_router.get("/health/ready")
async def readiness(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_cache),
):
    """Readiness probe - can the service handle traffic?"""
    checks = {}
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
    
    # Check cache
    try:
        await cache.ping()
        checks["cache"] = "ok"
    except Exception as e:
        checks["cache"] = f"error: {e}"
    
    # Aggregate status
    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503
    
    return Response(
        content=json.dumps({"status": "ready" if all_ok else "not_ready", "checks": checks}),
        status_code=status_code,
        media_type="application/json",
    )
```

---

## QUICK REFERENCE

### OpenTelemetry Instrumentation Libraries

```bash
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-httpx
pip install opentelemetry-instrumentation-redis
pip install opentelemetry-instrumentation-celery
```

### Metric Types

| Type | Use Case | Example |
|------|----------|---------|
| Counter | Monotonically increasing | Request count |
| Histogram | Distribution | Response time |
| Gauge | Point-in-time value | Memory usage |
| UpDownCounter | Increase/decrease | Active connections |

### Span Attributes

```python
# Common semantic conventions
span.set_attribute("http.method", "GET")
span.set_attribute("http.url", "/users/123")
span.set_attribute("http.status_code", 200)
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.statement", "SELECT * FROM users")
span.set_attribute("user.id", user_id)
span.set_attribute("error", True)
span.set_attribute("exception.message", str(e))
```

### Exporters

| Exporter | Backend |
|----------|---------|
| OTLPSpanExporter | Jaeger, Tempo, Honeycomb |
| ZipkinExporter | Zipkin |
| ConsoleSpanExporter | Development/debugging |
| JaegerExporter | Jaeger (legacy) |
