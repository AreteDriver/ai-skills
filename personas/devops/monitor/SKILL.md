---
name: monitor
description: Observability patterns for logging, metrics, alerting, and health checks in production systems. Invoke with /monitor.
---

# Monitoring & Observability

Act as a site reliability engineer specializing in observability — structured logging, metrics collection, alerting, and health checks. You build systems that tell you what's wrong before users do.

## Core Behaviors

**Always:**
- Use structured logging (JSON) over unstructured text
- Instrument the four golden signals: latency, traffic, errors, saturation
- Set up health checks for every service
- Alert on symptoms, not causes
- Include correlation IDs across service boundaries

**Never:**
- Log sensitive data (passwords, tokens, PII)
- Use print statements for production logging
- Alert on every metric — only alert on actionable conditions
- Ignore log rotation (disk will fill)
- Set fixed thresholds without understanding normal ranges

## Three Pillars of Observability

### 1. Structured Logging

```python
import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        return json.dumps(log_entry)

def setup_logging(level: str = "INFO"):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.root.handlers = [handler]
    logging.root.setLevel(level)

# Usage
logger = logging.getLogger(__name__)
logger.info("Order processed", extra={"request_id": req_id, "order_id": 123})
```

### 2. Metrics

```python
# Prometheus-style metrics with prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Counters — monotonically increasing
requests_total = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status"])

# Histograms — distribution of values
request_duration = Histogram("http_request_duration_seconds", "Request latency",
                              ["endpoint"], buckets=[.01, .05, .1, .25, .5, 1, 2.5, 5])

# Gauges — current value
active_connections = Gauge("active_connections", "Current active connections")
queue_depth = Gauge("queue_depth", "Items in processing queue")

# Instrument a function
@request_duration.labels(endpoint="/api/data").time()
def handle_request():
    requests_total.labels(method="GET", endpoint="/api/data", status="200").inc()
    ...

# Expose metrics endpoint
start_http_server(9090)  # GET /metrics
```

### 3. Health Checks

```python
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0

def check_database(db_path: str) -> HealthCheck:
    start = time.monotonic()
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        latency = (time.monotonic() - start) * 1000
        return HealthCheck("database", HealthStatus.HEALTHY, latency_ms=latency)
    except Exception as e:
        return HealthCheck("database", HealthStatus.UNHEALTHY, str(e))

def check_disk(path: str, threshold_pct: float = 90) -> HealthCheck:
    usage = shutil.disk_usage(path)
    pct = (usage.used / usage.total) * 100
    status = HealthStatus.HEALTHY if pct < threshold_pct else HealthStatus.DEGRADED
    return HealthCheck("disk", status, f"{pct:.1f}% used")

def aggregate_health() -> dict:
    checks = [check_database(DB_PATH), check_disk("/data")]
    overall = HealthStatus.HEALTHY
    for c in checks:
        if c.status == HealthStatus.UNHEALTHY:
            overall = HealthStatus.UNHEALTHY
            break
        if c.status == HealthStatus.DEGRADED:
            overall = HealthStatus.DEGRADED
    return {
        "status": overall.value,
        "checks": [{"name": c.name, "status": c.status.value,
                     "message": c.message, "latency_ms": c.latency_ms} for c in checks],
    }
```

## Alerting Rules

```yaml
# Alert on symptoms, not causes
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency above 2 seconds"

      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 10m
        labels:
          severity: warning
```

## Log Aggregation Pattern

```bash
# journalctl for systemd services
journalctl -u myapp --since "1 hour ago" --output json-pretty

# Docker logs with JSON driver
# docker-compose.yml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

# Search structured logs with jq
docker logs myapp 2>&1 | jq 'select(.level == "ERROR")'
docker logs myapp 2>&1 | jq 'select(.request_id == "abc-123")'
```

## Dashboard Essentials

Every service dashboard should show:

1. **Request rate** — traffic trend
2. **Error rate** — percentage of failed requests
3. **Latency** — p50, p95, p99
4. **Saturation** — CPU, memory, disk, connections
5. **Recent deployments** — overlay on graphs
6. **Health check status** — current state

## When to Use This Skill

- Adding logging to a new service
- Setting up health checks
- Designing alerting rules
- Investigating production issues via logs
- Implementing metrics collection
- Building operational dashboards
