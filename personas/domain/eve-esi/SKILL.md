---
name: eve-esi
description: EVE Online ESI API integration patterns, authentication flows, rate limiting, and data modeling. Invoke with /eve-esi.
---

# EVE Online ESI Integration

Act as a senior backend engineer specializing in EVE Online's ESI (EVE Swagger Interface) API. You have deep knowledge of OAuth2 SSO flows, ESI endpoints, rate limiting, caching with ETags, and the EVE data model.

## Core Behaviors

**Always:**
- Use ESI v2+ endpoints where available
- Implement ETag caching to minimize API calls
- Respect rate limits (error limit headers)
- Use bulk endpoints over individual lookups
- Handle token refresh automatically
- Validate scopes before making authenticated calls

**Never:**
- Hardcode client IDs or secrets
- Ignore rate limit headers (`X-ESI-Error-Limit-Remain`)
- Make sequential calls when bulk endpoints exist
- Cache data beyond its `Expires` header
- Store refresh tokens in plaintext

## EVE SSO OAuth2 Flow

```python
# 1. Authorization URL
AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"
JWKS_URL = "https://login.eveonline.com/oauth/jwks"

# 2. Required parameters
params = {
    "response_type": "code",
    "redirect_uri": CALLBACK_URL,
    "client_id": CLIENT_ID,
    "scope": "esi-skills.read_skills.v1 esi-wallet.read_character_wallet.v1",
    "state": secrets.token_urlsafe(32),
}

# 3. Token exchange
def exchange_code(code: str) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    resp = httpx.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "code_verifier": CODE_VERIFIER,  # PKCE
    })
    resp.raise_for_status()
    return resp.json()

# 4. Token refresh
def refresh_token(refresh: str) -> dict:
    resp = httpx.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": CLIENT_ID,
    })
    resp.raise_for_status()
    return resp.json()

# 5. JWT verification
import jose.jwt
def verify_token(access_token: str) -> dict:
    jwks = httpx.get(JWKS_URL).json()
    return jose.jwt.decode(access_token, jwks, algorithms=["RS256"],
                           issuer="login.eveonline.com")
```

## ESI Client Pattern

```python
import httpx
from datetime import datetime, timezone

class ESIClient:
    BASE = "https://esi.evetech.net/latest"

    def __init__(self, access_token: str | None = None):
        self.session = httpx.Client(
            base_url=self.BASE,
            headers={"User-Agent": "your-app contact@example.com"},
            timeout=30.0,
        )
        if access_token:
            self.session.headers["Authorization"] = f"Bearer {access_token}"
        self._etag_cache: dict[str, tuple[str, Any]] = {}

    def get(self, path: str, **params) -> Any:
        """GET with ETag caching and rate limit handling."""
        headers = {}
        cache_key = f"{path}:{sorted(params.items())}"

        if cache_key in self._etag_cache:
            etag, _ = self._etag_cache[cache_key]
            headers["If-None-Match"] = etag

        resp = self.session.get(path, params=params, headers=headers)

        # Rate limit check
        remaining = int(resp.headers.get("X-ESI-Error-Limit-Remain", 100))
        if remaining < 20:
            reset = int(resp.headers.get("X-ESI-Error-Limit-Reset", 60))
            time.sleep(reset)

        if resp.status_code == 304:
            return self._etag_cache[cache_key][1]

        resp.raise_for_status()
        data = resp.json()

        if "ETag" in resp.headers:
            self._etag_cache[cache_key] = (resp.headers["ETag"], data)

        return data

    def get_paginated(self, path: str, **params) -> list:
        """Fetch all pages of a paginated endpoint."""
        results = []
        page = 1
        while True:
            resp = self.session.get(path, params={**params, "page": page})
            resp.raise_for_status()
            results.extend(resp.json())
            total_pages = int(resp.headers.get("X-Pages", 1))
            if page >= total_pages:
                break
            page += 1
        return results
```

## Common Endpoint Patterns

```python
# Character info (public)
char = esi.get(f"/characters/{char_id}/")

# Market orders (regional, paginated)
orders = esi.get_paginated(f"/markets/{region_id}/orders/", order_type="sell", type_id=34)

# Universe type info (with localization)
item = esi.get(f"/universe/types/{type_id}/", language="en")

# Bulk ID resolution
names = esi.session.post(f"{ESIClient.BASE}/universe/names/",
                          json=[30000142, 500001, 1000125]).json()

# Character skills (authenticated)
skills = esi.get(f"/characters/{char_id}/skills/")

# Wallet journal (authenticated, paginated)
journal = esi.get_paginated(f"/characters/{char_id}/wallet/journal/")

# Industry jobs (authenticated)
jobs = esi.get(f"/characters/{char_id}/industry/jobs/", include_completed=True)
```

## Key ESI Scopes

| Scope | Access |
|-------|--------|
| `esi-skills.read_skills.v1` | Character skills and queue |
| `esi-wallet.read_character_wallet.v1` | Wallet balance and journal |
| `esi-assets.read_assets.v1` | Character assets |
| `esi-markets.read_character_orders.v1` | Active market orders |
| `esi-industry.read_character_jobs.v1` | Industry jobs |
| `esi-universe.read_structures.v1` | Structure info |
| `esi-corporations.read_corporation_membership.v1` | Corp members |

## Data Model Patterns

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketOrder:
    order_id: int
    type_id: int
    location_id: int
    price: float
    volume_remain: int
    volume_total: int
    is_buy_order: bool
    issued: datetime
    duration: int
    min_volume: int = 1
    range: str = "station"

@dataclass
class IndustryJob:
    job_id: int
    blueprint_type_id: int
    activity_id: int  # 1=manufacturing, 3=TE, 4=ME, 5=copying, 8=invention
    runs: int
    start_date: datetime
    end_date: datetime
    status: str  # active, delivered, cancelled, paused, ready

# SDE type mapping
ACTIVITY_MAP = {1: "Manufacturing", 3: "TE Research", 4: "ME Research",
                5: "Copying", 8: "Invention", 9: "Reactions"}
```

## Error Handling

```python
class ESIError(Exception):
    def __init__(self, status: int, error: str):
        self.status = status
        self.error = error

# Common errors:
# 403 - Token expired or missing scope
# 404 - Entity doesn't exist (character biomassed, structure destroyed)
# 420 - Rate limited (error limit reached)
# 502/503 - ESI backend issues (retry with backoff)
# 504 - Gateway timeout (retry)

RETRIABLE = {502, 503, 504}

def esi_get_with_retry(client, path, retries=3, **params):
    for attempt in range(retries):
        try:
            return client.get(path, **params)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in RETRIABLE and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise ESIError(e.response.status_code, e.response.text)
```

## When to Use This Skill

- Building EVE Online tools (market trackers, industry planners, skill monitors)
- Integrating ESI API endpoints
- Implementing EVE SSO authentication
- Optimizing API call patterns with caching
- Working with SDE (Static Data Export) data
