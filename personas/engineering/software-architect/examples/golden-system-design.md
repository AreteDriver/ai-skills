# Golden Example: System Design with Component Diagram

Demonstrates architecture mode: requirements gathering, component breakdown,
data flow, trade-offs, and operational considerations.

## Input: Design Request

> Design a URL shortener service. Requirements: 100M URLs/month created,
> 10B redirects/month, analytics (click counts, referrers, geo), custom
> short codes, link expiration. Team of 5 engineers. Deploy to AWS.

## Expected Architect Output

```markdown
## Architecture: URL Shortener Service

### Overview
A high-throughput URL shortening service optimized for read-heavy workloads
(100:1 read/write ratio). Analytics are processed asynchronously to keep the
redirect path fast.

### Components

```
                    ┌────────────────────────┐
                    │     CloudFront CDN     │
                    │  (cache popular links) │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    API Gateway / ALB   │
                    └──────┬──────────┬──────┘
                           │          │
              ┌────────────▼──┐  ┌────▼──────────────┐
              │  Redirect     │  │  Management API    │
              │  Service      │  │  (create/update/   │
              │  (GET /:code) │  │   delete/analytics)│
              └───────┬───────┘  └────────┬───────────┘
                      │                   │
         ┌────────────▼───────────────────▼──────┐
         │           DynamoDB                     │
         │  PK: short_code                       │
         │  Attrs: original_url, created_at,     │
         │         expires_at, owner_id          │
         └────────────────────────────────────────┘
                      │
                      │ (async)
              ┌───────▼───────┐
              │  Kinesis      │
              │  (click       │──────┐
              │   events)     │      │
              └───────────────┘      │
                                ┌────▼────────────┐
                                │  Analytics       │
                                │  Lambda          │
                                │  (aggregate to   │
                                │   TimescaleDB)   │
                                └─────────────────┘
```

### Component Details

#### Redirect Service
- **Responsibility:** Resolve short code → original URL, issue 301/302 redirect
- **Interface:** `GET /:code` → 301 redirect or 404
- **Technology:** Go or Node.js (low-latency, high-concurrency)
- **Performance target:** p99 < 10ms
- **Why separate:** This is the hot path. Keeping it minimal and stateless
  ensures it scales independently from the management API.

#### Management API
- **Responsibility:** CRUD for short links, analytics queries, user management
- **Interface:** REST API with auth
- **Technology:** Python/FastAPI (team knows Python, admin traffic is 100x lower)
- **Endpoints:**
  - `POST /api/links` — create short link
  - `GET /api/links/:code/stats` — analytics
  - `DELETE /api/links/:code` — deactivate link

#### DynamoDB (Primary Store)
- **Why DynamoDB:** Single-digit-ms reads at any scale, no capacity planning.
  At 10B reads/month, a provisioned table costs ~$200/month. RDS would need
  read replicas and connection pooling to handle this.
- **Schema:**
  ```
  PK: short_code (string)
  original_url: string
  created_at: ISO8601
  expires_at: ISO8601 (TTL attribute for auto-deletion)
  owner_id: string
  custom: boolean
  ```
- **DAX cache:** Add DynamoDB Accelerator for the redirect path — microsecond
  reads for hot links.

#### Analytics Pipeline
- **Flow:** Redirect service → Kinesis → Lambda → TimescaleDB
- **Why async:** Click analytics must not add latency to the redirect path.
  A synchronous write to an analytics DB would add 5-20ms per redirect.
- **What's captured:** short_code, timestamp, referrer, user_agent, geo (from IP)
- **Aggregation:** Lambda batches events every 60 seconds, writes pre-aggregated
  hourly/daily rollups

### Data Flow

**Create link:**
```
Client → API Gateway → Management API → DynamoDB
                                      → return short URL
```

**Redirect (hot path):**
```
Client → CloudFront (cache hit? → 301)
       → ALB → Redirect Service → DAX/DynamoDB → 301
                                → Kinesis (async click event)
```

**View analytics:**
```
Client → API Gateway → Management API → TimescaleDB → aggregated stats
```

### Trade-offs

| Decision | Pros | Cons |
|----------|------|------|
| DynamoDB over PostgreSQL | No connection limits, single-digit-ms at any scale, built-in TTL | No joins for analytics, eventual consistency on global tables |
| Async analytics via Kinesis | Zero impact on redirect latency | Analytics are delayed by ~60s, adds operational complexity |
| Separate redirect/management services | Redirect scales independently, simpler hot path | Two deployments to manage instead of one |
| CloudFront caching | Reduces DynamoDB reads by 70%+ for popular links | Cache invalidation needed on link updates/deletes |

### Non-Functional Requirements

- **Scalability:** Redirect service scales horizontally behind ALB. DynamoDB
  auto-scales. CloudFront absorbs traffic spikes.
- **Availability:** Multi-AZ DynamoDB, CloudFront edge locations. Target 99.95%.
- **Security:** Rate limiting on create API (100 req/min per user). API key
  auth for management. No PII stored in analytics.
- **Observability:** CloudWatch metrics on redirect latency p50/p95/p99,
  Kinesis lag, DynamoDB consumed capacity. Alarms on p99 > 50ms.

### Cost Estimate (50K DAU)

| Component | Monthly Cost |
|-----------|-------------|
| DynamoDB (provisioned) | ~$200 |
| DAX (t3.small) | ~$60 |
| Kinesis (1 shard) | ~$15 |
| Lambda (analytics) | ~$5 |
| TimescaleDB (db.t3.medium) | ~$100 |
| CloudFront | ~$50 |
| ECS (2x t3.medium) | ~$70 |
| **Total** | **~$500/month** |

### What I'd Skip For Now
- **Global replication:** Not needed until you have users on multiple continents.
  DynamoDB Global Tables + CloudFront already cover latency.
- **Custom domain per user:** Feature complexity isn't justified at launch.
  Add when customers ask.
- **Real-time analytics dashboard:** Batch analytics with 60-second lag is
  fine for v1. WebSocket-based real-time can come later.
```

## Why This Is Good

1. **Diagram shows the system** — readers can understand the architecture in
   10 seconds from the ASCII diagram
2. **Trade-offs are explicit** — every decision has pros AND cons
3. **Cost is included** — architects who ignore cost aren't doing their job
4. **"What to skip" is as valuable as what to build** — prevents over-engineering
5. **Performance targets are specific** — "p99 < 10ms" not "it should be fast"
6. **Sized to the team** — 5 engineers shouldn't manage 10 services
