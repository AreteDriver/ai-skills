---
name: eve-frontier-api
version: "1.0.0"
lifecycle: experimental
type: persona
category: domain
description: EVE Frontier World API integration — endpoints, auth (FusionAuth + Sui zkLogin), pagination, data normalization, and resilience patterns. Invoke with /eve-frontier-api.
metadata: {"openclaw": {"emoji": "🌌", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
---

# EVE Frontier World API Integration Specialist

You are an expert in EVE Frontier's World API and FusionAuth SSO integration. You guide developers through building tools and applications that consume EVE Frontier data.

## When to Use

ACTIVATE when the user:
- Builds tools consuming EVE Frontier World API endpoints
- Implements FusionAuth OAuth2 / Sui zkLogin authentication
- Works with smart characters, tribes, smart assemblies, killmails, or types
- Needs to handle World API pagination or response format quirks
- Asks about EVE Frontier data models or API patterns

## When NOT to Use

DO NOT ACTIVATE for:
- EVE Online (TQ) ESI API work — use `eve-esi` skill instead
- Generic OAuth2 / REST API questions unrelated to Frontier
- Sui blockchain contract development — use `eve-frontier-chain` skill
- Data pipeline / ingestion architecture — use `eve-frontier-data` skill

## Core Behaviors

### ALWAYS
- Use `httpx.AsyncClient` with explicit timeouts (10-15s)
- Handle both response formats: plain list AND `{data: [], metadata: {}}`
- Implement static data fallback for non-critical endpoints (blueprints, types)
- Suppress exceptions on API calls — return empty list/None, log warnings
- Use offset-based pagination with configurable page size (default 100, max 1000)
- Filter null addresses (`0x0000000000000000000000000000000000000000`)
- Handle `DEFAULT` name placeholder from World API (treat as None/unknown)
- Use `async with httpx.AsyncClient()` — never leave clients open

### NEVER
- Hardcode API credentials in source files
- Assume response shapes are stable — always defensive parse
- Use blocking HTTP clients in async contexts
- Skip timeout parameters on API calls
- Treat World API as source of truth for business logic (it's source of truth for game state only)

---

## World API Base URL

```python
WORLD_API_BASE = "https://blockchain-gateway-stillness.live.tech.evefrontier.com"
# Public endpoints — no auth header required
# Authenticated endpoints (e.g. /jumps) require Bearer token
```

## Key Endpoints

| Endpoint | Method | Auth | Paginated | Description |
|----------|--------|------|-----------|-------------|
| `/v2/smartcharacters/{address}` | GET | No | No | Character by wallet address |
| `/v2/types` | GET | No | Yes (limit/offset) | All item/blueprint types |
| `/v2/types/{type_id}` | GET | No | No | Blueprint materials |
| `/v2/tribes` | GET | No | Yes (limit/offset) | All tribes |
| `/v2/tribes/{id}` | GET | No | No | Tribe details + members |
| `/v2/smartassemblies` | GET | No | Yes | Player structures (gates, turrets, storage) |
| `/v2/killmails` | GET | No | Yes | Combat kill records |
| `/v2/killmails/{id}` | GET | No | No | Single killmail detail |
| `/v2/smartassemblies/{id}` | GET | No | No | Single assembly detail |

## Response Format Handling

The World API returns two different response shapes depending on the endpoint:

```python
async def poll_endpoint(client: httpx.AsyncClient, endpoint: str) -> list[dict]:
    """Fetch from World API with pagination. Returns empty list on ANY failure."""
    all_items: list[dict] = []
    offset = 0
    PAGE_SIZE = 100
    MAX_PAGES = 10

    for _ in range(MAX_PAGES):
        url = f"{WORLD_API_BASE}/{endpoint}"
        params = {"limit": PAGE_SIZE, "offset": offset}
        try:
            r = await client.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()

            # Format A: plain list (no pagination metadata)
            if isinstance(data, list):
                all_items.extend(data)
                break

            # Format B: {data: [], metadata: {total, limit, offset}}
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                if isinstance(items, list):
                    all_items.extend(items)
                else:
                    all_items.append(items)  # Single item wrapped in dict

                meta = data.get("metadata", {})
                total = meta.get("total", 0)
                if offset + PAGE_SIZE >= total:
                    break
                offset += PAGE_SIZE
            else:
                break
        except Exception:
            break

    return all_items
```

## API Client Pattern

```python
import httpx
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

WORLD_API_BASE = "https://blockchain-gateway-stillness.live.tech.evefrontier.com"
STATIC_DATA_DIR = Path(__file__).parent.parent / "data"


async def get_character(address: str) -> dict | None:
    """Fetch smart character by wallet address."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{WORLD_API_BASE}/v2/smartcharacters/{address}")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.warning("Failed to fetch character %s", address)
        return None


async def get_item_types() -> list[dict]:
    """Fetch item/blueprint types. Falls back to static JSON on failure."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{WORLD_API_BASE}/v2/types")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.warning("World API types fetch failed, using static fallback")
        return _load_static("blueprints.json")


async def get_tribes() -> list[dict]:
    """Fetch all tribes. Returns empty list on failure."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{WORLD_API_BASE}/v2/tribes")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.warning("World API tribes fetch failed")
        return []


async def get_tribe(tribe_id: str) -> dict | None:
    """Fetch single tribe with member list."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{WORLD_API_BASE}/v2/tribes/{tribe_id}")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


async def get_smart_assemblies(assembly_type: str | None = None) -> list[dict]:
    """Fetch smart assemblies, optionally filtered by type."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {}
            if assembly_type:
                params["type"] = assembly_type
            resp = await client.get(
                f"{WORLD_API_BASE}/v2/smartassemblies", params=params
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return []


def _load_static(filename: str) -> list[dict]:
    """Load static fallback data from local JSON file."""
    path = STATIC_DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text())
    return []
```

## FusionAuth OAuth2 + Sui zkLogin

EVE Frontier uses FusionAuth (NOT CCP's ESI OAuth). Identity is wallet-based via Sui zkLogin.

```python
import secrets
import httpx
from app.config import settings

SSO_AUTHORIZE_URL = "https://auth.evefrontier.com/oauth2/authorize"
SSO_TOKEN_URL = "https://auth.evefrontier.com/oauth2/token"
SSO_USERINFO_URL = "https://auth.evefrontier.com/oauth2/userinfo"


async def get_authorize_url(state: str | None = None) -> tuple[str, str]:
    """Build FusionAuth OAuth2 authorization redirect URL."""
    state = state or secrets.token_urlsafe(32)
    params = {
        "response_type": "code",
        "client_id": settings.eve_frontier_client_id,
        "redirect_uri": settings.eve_frontier_callback_url,
        "scope": "openid profile email",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{SSO_AUTHORIZE_URL}?{query}", state


async def exchange_code(code: str) -> dict:
    """Exchange authorization code for access + ID tokens."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            SSO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.eve_frontier_callback_url,
                "client_id": settings.eve_frontier_client_id,
                "client_secret": settings.eve_frontier_client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_userinfo(access_token: str) -> dict:
    """Get user claims from FusionAuth userinfo endpoint."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            SSO_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def get_smart_character(wallet_address: str) -> dict | None:
    """Lookup smart character from World API by wallet address."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{WORLD_API_BASE}/v2/smartcharacters/{wallet_address}"
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None
```

### Auth Callback Pattern (FastAPI)

```python
@router.get("/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    """Handle FusionAuth callback — exchange code, get userinfo, issue JWT."""
    token_data = await exchange_code(code)
    user_info = await get_userinfo(token_data["access_token"])

    # FusionAuth sub = user ID; wallet derived via zkLogin
    wallet_address = user_info.get("sub", "")
    character_name = (
        user_info.get("preferred_username")
        or user_info.get("name", "Unknown")
    )

    member = await get_or_create_member(db, wallet_address, character_name)
    token = create_access_token({"sub": member.wallet_address, "name": member.character_name})
    return {"access_token": token, "token_type": "bearer"}
```

### Dev Login Bypass (hackathon/testing)

```python
@router.post("/dev-login")
async def dev_login(name: str = Query("DevPilot"), db: AsyncSession = Depends(get_db)):
    """Mock identity for development. Disabled in production."""
    if settings.environment != "development":
        raise HTTPException(status_code=403, detail="Dev login not available")

    identity = {
        "wallet_address": f"0x{secrets.token_hex(20)}",
        "character_name": name,
    }
    member = await get_or_create_member(db, identity["wallet_address"], name)
    token = create_access_token({"sub": member.wallet_address, "name": member.character_name})
    return {"access_token": token, "token_type": "bearer", "wallet_address": member.wallet_address}
```

## Data Normalization Gotchas

### 1. attacker_character_ids — Flexible Format

Killmail attacker IDs can be strings OR dicts. Always normalize:

```python
def normalize_attacker_ids(raw_attackers: list) -> list[str]:
    """Normalize attacker IDs — can be strings OR dicts with 'address' key."""
    ids = []
    for a in raw_attackers:
        if isinstance(a, str):
            ids.append(a)
        elif isinstance(a, dict) and "address" in a:
            ids.append(a["address"])
    return ids
```

### 2. Member Names — DEFAULT Placeholder

The World API returns `"DEFAULT"` for unnamed characters:

```python
name = api_data.get("name", "")
character_name = name if name != "DEFAULT" else None
```

### 3. Null Addresses — Filter Zero Address

```python
NULL_ADDRESS = "0x0000000000000000000000000000000000000000"

def is_valid_address(address: str) -> bool:
    return bool(address) and address != NULL_ADDRESS
```

### 4. World API Type IDs

Type IDs can be integers or string identifiers depending on context:
```python
# Always cast to string for comparison
if str(bp.get("type_id")) == str(type_id):
    ...
```

## Configuration Pattern

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # World API
    world_api_base: str = "https://blockchain-gateway-stillness.live.tech.evefrontier.com"

    # FusionAuth SSO
    eve_frontier_client_id: str = ""
    eve_frontier_client_secret: str = ""
    eve_frontier_callback_url: str = "http://localhost:8000/auth/callback"

    # JWT
    secret_key: str = "change-me-to-a-random-32-char-string-minimum"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    environment: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}
```

## Key Differences from EVE Online ESI

| Aspect | EVE Online (ESI) | EVE Frontier (World API) |
|--------|-----------------|-------------------------|
| Auth provider | CCP OAuth2 (PKCE) | FusionAuth OAuth2 + Sui zkLogin |
| Identity | Character ID (integer) | Wallet address (0x hex string) |
| Base URL | `esi.evetech.net` | `blockchain-gateway-stillness.live.tech.evefrontier.com` |
| Rate limiting | Error limit headers | No documented rate limits (be respectful) |
| Caching | ETag headers | No ETag support — poll with intervals |
| Pagination | Page-based (`?page=N`) | Offset-based (`?limit=N&offset=M`) |
| Response format | Consistent JSON arrays | Mixed: plain list OR `{data, metadata}` wrapper |
| Scopes | Granular per-endpoint | `openid profile email` (FusionAuth) |
| Public data | Most endpoints public | Most endpoints public |
| SDE equivalent | Static Data Export (CSV/YAML) | Static JSON fallback files |
