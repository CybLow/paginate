---
name: perf-slo
description: >
  Service Level Objectives (SLOs), Indicators (SLIs), and Agreements (SLAs).
  Covers definitions, measurement, error budget tracking, and alerting strategies.
related:
  - perf-apm
  - perf-ops
  - arch-principles
---

## SLOs, SLIs, AND SLAs

Define and measure service reliability.

---

### Definitions

| Term | Definition | Example |
|------|------------|---------|
| **SLI** (Service Level Indicator) | Measurable metric | 99.2% of requests < 200ms |
| **SLO** (Service Level Objective) | Target for SLI | 99% of requests should be < 200ms |
| **SLA** (Service Level Agreement) | Contract with consequences | 99.9% uptime or credit issued |

### Defining SLIs

```python
# src/observability/sli.py
from dataclasses import dataclass
from enum import Enum
from datetime import timedelta


class SLIType(Enum):
    AVAILABILITY = "availability"  # % of successful requests
    LATENCY = "latency"            # % of requests under threshold
    THROUGHPUT = "throughput"      # Requests per second
    ERROR_RATE = "error_rate"      # % of failed requests
    SATURATION = "saturation"      # Resource utilization


@dataclass
class SLI:
    """Service Level Indicator definition."""
    name: str
    type: SLIType
    description: str
    good_event_filter: str      # What counts as "good"
    valid_event_filter: str     # What counts as measurable
    
    def calculate(self, good_events: int, valid_events: int) -> float:
        """Calculate SLI as percentage."""
        if valid_events == 0:
            return 100.0
        return (good_events / valid_events) * 100


# Define SLIs for the service
SLIS = {
    "api_availability": SLI(
        name="API Availability",
        type=SLIType.AVAILABILITY,
        description="Percentage of successful API requests",
        good_event_filter="status_code < 500",
        valid_event_filter="all requests excluding health checks",
    ),
    "api_latency_p99": SLI(
        name="API Latency P99",
        type=SLIType.LATENCY,
        description="99th percentile response time under 500ms",
        good_event_filter="response_time_ms < 500",
        valid_event_filter="all requests excluding uploads",
    ),
    "checkout_success": SLI(
        name="Checkout Success Rate",
        type=SLIType.AVAILABILITY,
        description="Percentage of successful checkouts",
        good_event_filter="checkout completed without error",
        valid_event_filter="all checkout attempts",
    ),
}
```

### Defining SLOs

```python
# src/observability/slo.py
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class SLO:
    """Service Level Objective definition."""
    sli: SLI
    target: float              # Target percentage (e.g., 99.9)
    window: timedelta          # Measurement window (e.g., 30 days)
    error_budget: float = None # Calculated from target
    
    def __post_init__(self):
        # Error budget = 100% - target
        # E.g., 99.9% target = 0.1% error budget
        self.error_budget = 100.0 - self.target
    
    def remaining_budget(self, current_sli: float) -> float:
        """Calculate remaining error budget as percentage."""
        used = 100.0 - current_sli
        return max(0, self.error_budget - used)
    
    def is_met(self, current_sli: float) -> bool:
        """Check if SLO is currently met."""
        return current_sli >= self.target


# Define SLOs
SLOS = {
    "api_availability": SLO(
        sli=SLIS["api_availability"],
        target=99.9,  # 99.9% availability
        window=timedelta(days=30),
    ),
    "api_latency": SLO(
        sli=SLIS["api_latency_p99"],
        target=99.0,  # 99% of requests under 500ms
        window=timedelta(days=7),
    ),
    "checkout": SLO(
        sli=SLIS["checkout_success"],
        target=99.5,  # 99.5% checkout success
        window=timedelta(days=30),
    ),
}
```

### Error Budget Tracking

```python
# src/observability/error_budget.py
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class ErrorBudgetTracker:
    """Track error budget consumption."""
    
    def __init__(self, slo: SLO, metrics_client):
        self.slo = slo
        self.metrics = metrics_client
    
    async def get_current_status(self) -> dict:
        """Get current error budget status."""
        # Query metrics for SLI
        window_start = datetime.utcnow() - self.slo.window
        
        good_events = await self.metrics.count(
            self.slo.sli.good_event_filter,
            since=window_start,
        )
        valid_events = await self.metrics.count(
            self.slo.sli.valid_event_filter,
            since=window_start,
        )
        
        current_sli = self.slo.sli.calculate(good_events, valid_events)
        remaining_budget = self.slo.remaining_budget(current_sli)
        
        # Calculate burn rate
        elapsed_days = self.slo.window.days
        expected_budget_used = (elapsed_days / 30) * self.slo.error_budget
        actual_budget_used = self.slo.error_budget - remaining_budget
        burn_rate = actual_budget_used / expected_budget_used if expected_budget_used > 0 else 0
        
        return {
            "slo_name": self.slo.sli.name,
            "target": self.slo.target,
            "current_sli": current_sli,
            "is_met": self.slo.is_met(current_sli),
            "error_budget_total": self.slo.error_budget,
            "error_budget_remaining": remaining_budget,
            "error_budget_remaining_percent": (remaining_budget / self.slo.error_budget) * 100,
            "burn_rate": burn_rate,
            "window_days": self.slo.window.days,
        }
    
    async def check_and_alert(self) -> None:
        """Check error budget and alert if needed."""
        status = await self.get_current_status()
        
        if status["error_budget_remaining_percent"] < 10:
            logger.error(
                "error_budget_critical",
                slo=status["slo_name"],
                remaining_percent=status["error_budget_remaining_percent"],
            )
            await self.alert_service.send_critical(
                f"SLO {status['slo_name']} error budget nearly exhausted: "
                f"{status['error_budget_remaining_percent']:.1f}% remaining"
            )
        elif status["burn_rate"] > 2.0:
            logger.warning(
                "error_budget_burn_rate_high",
                slo=status["slo_name"],
                burn_rate=status["burn_rate"],
            )
```

---

## PERFORMANCE BUDGETS

Set and enforce performance limits.

---

### Defining Performance Budgets

```python
# src/config/performance_budgets.py
from dataclasses import dataclass
from enum import Enum


class BudgetType(Enum):
    RESPONSE_TIME = "response_time"
    BUNDLE_SIZE = "bundle_size"
    MEMORY_USAGE = "memory_usage"
    CPU_TIME = "cpu_time"


@dataclass
class PerformanceBudget:
    """Performance budget definition."""
    name: str
    type: BudgetType
    warning_threshold: float
    error_threshold: float
    unit: str


PERFORMANCE_BUDGETS = {
    # API response times
    "api_p50": PerformanceBudget(
        name="API P50 Response Time",
        type=BudgetType.RESPONSE_TIME,
        warning_threshold=50,   # 50ms warning
        error_threshold=100,    # 100ms error
        unit="ms",
    ),
    "api_p95": PerformanceBudget(
        name="API P95 Response Time",
        type=BudgetType.RESPONSE_TIME,
        warning_threshold=200,
        error_threshold=500,
        unit="ms",
    ),
    "api_p99": PerformanceBudget(
        name="API P99 Response Time",
        type=BudgetType.RESPONSE_TIME,
        warning_threshold=500,
        error_threshold=1000,
        unit="ms",
    ),
    
    # Memory usage
    "container_memory": PerformanceBudget(
        name="Container Memory Usage",
        type=BudgetType.MEMORY_USAGE,
        warning_threshold=512,   # 512 MB
        error_threshold=768,     # 768 MB
        unit="MB",
    ),
    
    # Database query time
    "db_query_p95": PerformanceBudget(
        name="Database Query P95",
        type=BudgetType.RESPONSE_TIME,
        warning_threshold=50,
        error_threshold=100,
        unit="ms",
    ),
}
```

### Enforcing Budgets in CI

```yaml
# .github/workflows/performance-budget.yml
performance-budget:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Run performance tests
      run: uv run pytest tests/performance --json-report
      
    - name: Check performance budgets
      run: |
        python scripts/check_budgets.py \
          --results performance-results.json \
          --budgets src/config/performance_budgets.py
```

---

## QUICK REFERENCE

### SLO Examples

| Service Type | SLI | Typical SLO |
|--------------|-----|-------------|
| API | Availability | 99.9% |
| API | P99 Latency < 500ms | 99% |
| Checkout | Success rate | 99.5% |
| Search | P95 Latency < 200ms | 99% |
| Background jobs | Completion rate | 99.9% |

### Error Budget Calculation

```
Error Budget = 100% - SLO Target

Example:
- SLO Target: 99.9%
- Error Budget: 0.1%
- Monthly minutes: 43,200
- Allowed downtime: 43.2 minutes/month
```

### Burn Rate Alerts

| Burn Rate | Meaning | Action |
|-----------|---------|--------|
| < 1.0 | Under budget | Monitor |
| 1.0-2.0 | On track | Watch |
| 2.0-5.0 | Fast burn | Investigate |
| > 5.0 | Critical | Immediate action |
