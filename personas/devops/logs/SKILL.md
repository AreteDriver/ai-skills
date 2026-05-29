---
name: logs
description: Logging Setup & Analysis
---

# /logs - Logging Setup & Analysis

Configure logging and analyze log output.

## Usage
```
/logs                    # Analyze current logging setup
/logs --setup            # Set up logging from scratch
/logs --analyze file.log # Analyze log file
/logs --search "error"   # Search logs for pattern
```

## What This Skill Does

1. **Audit Logging** - Check current logging configuration
2. **Setup Logging** - Configure structured logging
3. **Analyze Logs** - Parse and summarize log files
4. **Find Issues** - Search for errors, patterns
5. **Add Context** - Request IDs, user context

## Python Logging Setup

### Basic Setup
```python
# logging_config.py
import logging
import sys
from datetime import datetime

def setup_logging(level: str = "INFO", json_format: bool = False):
    """Configure application logging."""

    if json_format:
        # JSON format for production
        import json

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)

        formatter = JsonFormatter()
    else:
        # Human-readable for development
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger
```

### Usage in Application
```python
import logging

logger = logging.getLogger(__name__)

def process_order(order_id: str):
    logger.info("Processing order", extra={"order_id": order_id})
    try:
        # ... process ...
        logger.info("Order completed", extra={"order_id": order_id})
    except Exception as e:
        logger.exception("Order failed", extra={"order_id": order_id})
        raise
```

### Request Context (Web Apps)
```python
import contextvars
import uuid

request_id_var = contextvars.ContextVar('request_id', default=None)

class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get() or "no-request"
        return True

# In middleware
@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

## Log Analysis

### Common Patterns
```bash
# Count errors by type
grep "ERROR" app.log | cut -d'|' -f4 | sort | uniq -c | sort -rn

# Find slowest requests
grep "request completed" app.log | \
  sed 's/.*duration=\([0-9.]*\).*/\1/' | \
  sort -rn | head -20

# Errors in last hour
grep "ERROR" app.log | \
  awk -v d="$(date -d '1 hour ago' '+%Y-%m-%d %H')" '$0 >= d'

# Group by user
grep "user_id=" app.log | \
  sed 's/.*user_id=\([^ ]*\).*/\1/' | \
  sort | uniq -c | sort -rn
```

### Log Analysis Report
```markdown
# Log Analysis: app.log

## Summary
| Metric | Value |
|--------|-------|
| Total Lines | 50,432 |
| Time Range | 2024-01-01 to 2024-01-07 |
| Error Rate | 0.5% |

## Log Levels
| Level | Count | % |
|-------|-------|---|
| INFO | 45,000 | 89% |
| WARNING | 5,000 | 10% |
| ERROR | 400 | 0.8% |
| CRITICAL | 32 | 0.06% |

## Top Errors
| Error | Count | First Seen |
|-------|-------|------------|
| ConnectionTimeout | 150 | 2024-01-02 |
| ValidationError | 120 | 2024-01-01 |
| DatabaseError | 80 | 2024-01-03 |

## Recommendations
1. Investigate ConnectionTimeout spike on Jan 2
2. Add retry logic for database connections
3. Improve input validation to reduce ValidationErrors
```

## Rust Logging (tracing)

```rust
use tracing::{info, warn, error, instrument};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

fn setup_logging() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .init();
}

#[instrument]
fn process_item(id: u64) -> Result<(), Error> {
    info!(id, "Processing item");
    // ...
    Ok(())
}
```

## Instructions for Claude

When /logs is invoked:

1. **Check current setup** - Existing logging configuration
2. **Identify gaps** - Missing context, poor format
3. **Set up logging** - Structured, with context
4. **Add request IDs** - For tracing requests
5. **Configure levels** - Appropriate per-logger levels
6. **Analyze logs** - If log file provided
7. **Find patterns** - Errors, slow operations
8. **Recommend fixes** - Based on analysis
