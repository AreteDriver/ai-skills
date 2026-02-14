# Golden Example: Architecture Decision with Trade-offs

Demonstrates the SSE architecture mode: present options, weigh trade-offs,
make a recommendation, and explain why.

## Input: Architecture Question

> We need to add real-time notifications to our Django app. Users should see
> notifications for comments, mentions, and status changes without refreshing.
> We have ~5,000 DAU and expect 10x growth. Team is 3 backend Python devs,
> 1 frontend React dev. Currently deployed on AWS ECS.

## Expected SSE Output

```markdown
## Architecture: Real-Time Notifications

### Requirements
- Push notifications to browser (comments, mentions, status changes)
- ~5K DAU now, planning for 50K
- Python/Django backend, React frontend
- AWS ECS deployment
- Team: 3 Python devs + 1 React dev

### Option A: Django Channels + WebSockets (Recommended)

```
Browser ──WebSocket──► Django Channels ──► Channel Layer (Redis)
                           │
                           ▼
                       Event handlers
                       (comment, mention, status)
```

**Pros:**
- Native Django integration — stays in the framework the team knows
- Battle-tested at this scale (5K–50K concurrent is well within range)
- Single deployment artifact — no new services to operate
- Redis channel layer handles pub/sub and is already likely in your stack
- Rich ecosystem: `channels`, `daphne`/`uvicorn`, `channels-redis`

**Cons:**
- Requires ASGI server (Daphne or Uvicorn) alongside or replacing Gunicorn
- WebSocket connections are stateful — need sticky sessions or proper
  channel layer routing on ECS
- Adds ~1 week of learning curve for the team

**Effort:** 2–3 weeks for core implementation + deployment changes

---

### Option B: Server-Sent Events (SSE) + Django

```
Browser ──SSE (GET)──► Django view (StreamingHttpResponse)
                           │
                           ▼
                       Redis pub/sub
```

**Pros:**
- Simpler than WebSockets — HTTP/1.1, no upgrade handshake
- Works through proxies and load balancers without sticky sessions
- Lighter server-side resource usage (half-duplex)

**Cons:**
- One-directional (server→client only) — fine for notifications but
  limits future use cases (chat, typing indicators)
- Max 6 concurrent SSE connections per domain in HTTP/1.1 (browser limit)
- Less Django ecosystem support than Channels
- Team would need to build more infrastructure from scratch

**Effort:** 2 weeks for core, but more custom plumbing

---

### Option C: Polling with SWR/React Query

```
Browser ──GET /notifications (every 5s)──► Django REST endpoint
```

**Pros:**
- Zero new infrastructure — just a REST endpoint
- Team already knows this pattern
- Simplest to deploy, monitor, and debug
- Can ship in days, not weeks

**Cons:**
- 5-second delay is noticeable for "real-time" features
- At 50K DAU polling every 5s = ~10K req/s to the notifications endpoint
  (likely needs caching layer or will stress the DB)
- Not truly real-time — users will notice the lag on mentions

**Effort:** 3–5 days

---

### Recommendation: Option A (Django Channels)

**Rationale:**
1. **Growth path** — at 50K DAU, polling becomes expensive. Channels handles
   this with persistent connections and Redis pub/sub, which scales horizontally.
2. **Team fit** — 3 Python devs learning Django Channels is lower risk than
   learning a separate real-time service. It's still Django.
3. **Future use cases** — WebSockets enable bidirectional communication. When
   the product team asks for typing indicators or live collaboration (and they
   will), you're already there.
4. **Operational simplicity** — one service to deploy, not two. This matters
   at a 4-person team.

**What I'd skip:**
- Don't start with a separate notification microservice (Option D). At your
  team size and scale, the operational overhead of a second service outweighs
  the architectural purity. Revisit at 200K+ DAU.
- Don't use a managed WebSocket service (Pusher, Ably) unless you need to ship
  in under a week. The monthly cost at 50K DAU will exceed the engineering cost
  of Channels within 6 months.

### ECS Deployment Notes
- Run Daphne/Uvicorn as the ASGI server instead of Gunicorn
- Add an ALB target group with WebSocket support (stickiness enabled)
- Redis ElastiCache for the channel layer — `t3.small` handles 50K easily
- Health check endpoint should be HTTP, not WebSocket
```

## Why This Is Good

1. **Three options, not one** — respects that the team might have constraints
   the SSE doesn't know about
2. **Effort estimates are realistic** — not aspirational, accounts for learning
3. **Recommendation is justified** — explains why, not just what
4. **Explicitly says what to skip** — the "boring technology" principle in action
5. **Operational details included** — ECS deployment notes show production thinking
6. **Sized to the team** — doesn't recommend microservices for a 4-person team
