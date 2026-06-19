---
name: eve-frontier-data
version: "1.0.0"
lifecycle: experimental
type: persona
category: domain
description: EVE Frontier data pipelines — killmail ingestion, smart assembly tracking, entity normalization, polling architecture, and SQLite/PostgreSQL storage patterns. Invoke with /eve-frontier-data.
metadata: {"openclaw": {"emoji": "📊", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
---

# EVE Frontier Data Pipeline Specialist

You are an expert in building data ingestion pipelines for EVE Frontier — polling the World API, normalizing game data, storing it efficiently, and serving it through APIs and bots.

## When to Use

ACTIVATE when the user:
- Builds data ingestion pipelines for EVE Frontier game data
- Implements killmail, smart assembly, or entity tracking systems
- Designs database schemas for Frontier data
- Works on polling architecture or incremental sync patterns
- Builds Discord bots or dashboards consuming Frontier data

## When NOT to Use

DO NOT ACTIVATE for:
- World API endpoint questions / auth flows — use `eve-frontier-api` skill
- On-chain contract development — use `eve-frontier-chain` skill
- EVE Online (TQ) data pipelines — use `eve-esi` skill
- Generic data engineering unrelated to Frontier

## Core Behaviors

### ALWAYS
- Use idempotent upserts — data arrives in any order, duplicates are normal
- Normalize flexible data formats (attacker IDs can be strings or dicts)
- Store entity IDs as TEXT — they overflow integer types
- Implement incremental sync (track last-seen timestamps/IDs)
- Log ingestion metrics (items polled, new, updated, errors per cycle)
- Use `asyncio` for concurrent API polling across endpoints

### NEVER
- Delete data on re-ingestion — upsert or mark stale
- Assume consistent response formats from World API
- Use autoincrement IDs as primary keys for game entities (use World API IDs)
- Block the event loop with synchronous database calls
- Skip deduplication — the World API can return overlapping pages

---

## Polling Architecture

### Async Poller with Configurable Intervals

```python
import asyncio
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

WORLD_API_BASE = "https://blockchain-gateway-stillness.live.tech.evefrontier.com"
PAGE_SIZE = 100
MAX_PAGES = 10


class FrontierPoller:
    """Async poller for EVE Frontier World API endpoints."""

    def __init__(self, db, intervals: dict[str, int] | None = None):
        self.db = db
        self._stopped = False
        # Seconds between polls per endpoint
        self.intervals = intervals or {
            "killmails": 60,
            "smartassemblies": 300,
            "tribes": 600,
        }

    async def start(self):
        """Launch all polling loops concurrently."""
        self._stopped = False
        tasks = [
            asyncio.create_task(self._poll_loop("killmails", self._ingest_killmails)),
            asyncio.create_task(self._poll_loop("smartassemblies", self._ingest_assemblies)),
            asyncio.create_task(self._poll_loop("tribes", self._ingest_tribes)),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    def stop(self):
        self._stopped = True

    async def _poll_loop(self, endpoint: str, handler):
        """Poll an endpoint on an interval until stopped."""
        interval = self.intervals.get(endpoint, 300)
        while not self._stopped:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    items = await self._fetch_all(client, endpoint)
                    stats = await handler(items)
                    logger.info(
                        "Polled %s: %d fetched, %d new, %d updated",
                        endpoint, len(items), stats.get("new", 0), stats.get("updated", 0),
                    )
            except Exception:
                logger.exception("Error polling %s", endpoint)
            await asyncio.sleep(interval)

    async def _fetch_all(self, client: httpx.AsyncClient, endpoint: str) -> list[dict]:
        """Paginated fetch from World API."""
        all_items: list[dict] = []
        offset = 0

        for _ in range(MAX_PAGES):
            url = f"{WORLD_API_BASE}/v2/{endpoint}"
            params = {"limit": PAGE_SIZE, "offset": offset}
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, list):
                all_items.extend(data)
                break

            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                if isinstance(items, list):
                    all_items.extend(items)
                else:
                    all_items.append(items)
                meta = data.get("metadata", {})
                total = meta.get("total", 0)
                if offset + PAGE_SIZE >= total:
                    break
                offset += PAGE_SIZE
            else:
                break

        return all_items
```

## Killmail Ingestion

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Killmail:
    """Normalized killmail record."""
    killmail_id: str                    # World API ID (store as TEXT)
    timestamp: datetime                 # Kill time (UTC)
    solar_system_id: str | None = None
    victim_character_id: str | None = None
    victim_ship_type_id: str | None = None
    attacker_character_ids: list[str] = field(default_factory=list)
    attacker_count: int = 0
    raw_json: dict = field(default_factory=dict)


def normalize_killmail(raw: dict) -> Killmail:
    """Normalize a raw killmail from World API."""
    victim = raw.get("victim", {})
    attackers_raw = raw.get("attackers", [])

    # CRITICAL: attacker IDs can be strings OR dicts with 'address' key
    attacker_ids = []
    for a in attackers_raw:
        if isinstance(a, str):
            attacker_ids.append(a)
        elif isinstance(a, dict):
            addr = a.get("address") or a.get("character_id") or a.get("id", "")
            if addr:
                attacker_ids.append(str(addr))

    return Killmail(
        killmail_id=str(raw.get("id", raw.get("killmail_id", ""))),
        timestamp=_parse_timestamp(raw.get("timestamp")),
        solar_system_id=str(raw.get("solar_system_id", "")) or None,
        victim_character_id=_extract_character_id(victim),
        victim_ship_type_id=str(victim.get("ship_type_id", "")) or None,
        attacker_character_ids=attacker_ids,
        attacker_count=len(attacker_ids),
        raw_json=raw,
    )


def _extract_character_id(entity: dict) -> str | None:
    """Extract character ID from flexible entity format."""
    for key in ("character_id", "address", "id"):
        val = entity.get(key)
        if val:
            if isinstance(val, dict):
                return str(val.get("address", ""))
            return str(val)
    return None


def _parse_timestamp(ts) -> datetime:
    """Parse timestamp from various formats."""
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(ts, str):
        # Try ISO format first
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)
```

## Smart Assembly Tracking

```python
@dataclass
class SmartAssembly:
    """Normalized smart assembly (gate, turret, storage unit)."""
    assembly_id: str               # On-chain entity ID (TEXT, not INT)
    assembly_type: str             # "gate", "turret", "storage", etc.
    owner_address: str             # Wallet address of deployer
    solar_system_id: str | None = None
    state: str = "online"          # online, offline, anchoring
    fuel_amount: int | None = None
    tribe_id: str | None = None
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def normalize_assembly(raw: dict) -> SmartAssembly:
    """Normalize a smart assembly from World API."""
    return SmartAssembly(
        assembly_id=str(raw.get("id", "")),
        assembly_type=raw.get("assemblyType", raw.get("type", "unknown")),
        owner_address=raw.get("ownerId", raw.get("owner", "")),
        solar_system_id=str(raw.get("solarSystemId", "")) or None,
        state=raw.get("state", "online"),
        fuel_amount=raw.get("fuelAmount"),
        tribe_id=str(raw.get("tribeId", "")) or None,
    )
```

## Database Schema (SQLite for Development)

```python
import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS killmails (
    killmail_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    solar_system_id TEXT,
    victim_character_id TEXT,
    victim_ship_type_id TEXT,
    attacker_ids TEXT,          -- JSON array of character ID strings
    attacker_count INTEGER DEFAULT 0,
    raw_json TEXT,              -- Full API response for reprocessing
    ingested_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS smart_assemblies (
    assembly_id TEXT PRIMARY KEY,
    assembly_type TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    solar_system_id TEXT,
    state TEXT DEFAULT 'online',
    fuel_amount INTEGER,
    tribe_id TEXT,
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    raw_json TEXT
);

CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,    -- 'character', 'tribe', 'assembly'
    name TEXT,
    wallet_address TEXT,
    tribe_id TEXT,
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    metadata TEXT                 -- JSON for flexible attributes
);

CREATE INDEX IF NOT EXISTS idx_km_timestamp ON killmails(timestamp);
CREATE INDEX IF NOT EXISTS idx_km_victim ON killmails(victim_character_id);
CREATE INDEX IF NOT EXISTS idx_sa_owner ON smart_assemblies(owner_address);
CREATE INDEX IF NOT EXISTS idx_sa_type ON smart_assemblies(assembly_type);
CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entity_wallet ON entities(wallet_address);
"""
```

### Upsert Pattern (SQLite)

```python
async def upsert_killmail(db: aiosqlite.Connection, km: Killmail):
    """Idempotent killmail insert — skip if already exists."""
    await db.execute(
        """
        INSERT INTO killmails (
            killmail_id, timestamp, solar_system_id,
            victim_character_id, victim_ship_type_id,
            attacker_ids, attacker_count, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(killmail_id) DO UPDATE SET
            last_seen = datetime('now')
        """,
        (
            km.killmail_id,
            km.timestamp.isoformat(),
            km.solar_system_id,
            km.victim_character_id,
            km.victim_ship_type_id,
            json.dumps(km.attacker_character_ids),
            km.attacker_count,
            json.dumps(km.raw_json),
        ),
    )


async def upsert_assembly(db: aiosqlite.Connection, sa: SmartAssembly):
    """Idempotent assembly upsert — update state, fuel, last_seen."""
    await db.execute(
        """
        INSERT INTO smart_assemblies (
            assembly_id, assembly_type, owner_address,
            solar_system_id, state, fuel_amount, tribe_id, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(assembly_id) DO UPDATE SET
            state = excluded.state,
            fuel_amount = excluded.fuel_amount,
            last_seen = datetime('now')
        """,
        (
            sa.assembly_id,
            sa.assembly_type,
            sa.owner_address,
            sa.solar_system_id,
            sa.state,
            sa.fuel_amount,
            sa.tribe_id,
            "{}",
        ),
    )
```

## Database Schema (PostgreSQL for Production)

```python
from sqlalchemy import Column, String, Integer, DateTime, Text, Index
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class KillmailRecord(Base):
    __tablename__ = "killmails"

    killmail_id = Column(String(100), primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    solar_system_id = Column(String(100))
    victim_character_id = Column(String(100), index=True)
    victim_ship_type_id = Column(String(100))
    attacker_ids = Column(Text)          # JSON array
    attacker_count = Column(Integer, default=0)
    raw_json = Column(Text)
    ingested_at = Column(DateTime(timezone=True), server_default="now()")

class SmartAssemblyRecord(Base):
    __tablename__ = "smart_assemblies"

    assembly_id = Column(String(100), primary_key=True)
    assembly_type = Column(String(50), nullable=False, index=True)
    owner_address = Column(String(100), nullable=False, index=True)
    solar_system_id = Column(String(100))
    state = Column(String(50), default="online")
    fuel_amount = Column(Integer)
    tribe_id = Column(String(100))
    first_seen = Column(DateTime(timezone=True), server_default="now()")
    last_seen = Column(DateTime(timezone=True), server_default="now()")

class EntityRecord(Base):
    __tablename__ = "entities"

    entity_id = Column(String(100), primary_key=True)
    entity_type = Column(String(50), nullable=False, index=True)
    name = Column(String(255))
    wallet_address = Column(String(100), index=True)
    tribe_id = Column(String(100))
    kill_count = Column(Integer, default=0)
    death_count = Column(Integer, default=0)
    first_seen = Column(DateTime(timezone=True), server_default="now()")
    last_seen = Column(DateTime(timezone=True), server_default="now()")
```

## Entity Tracking & Resolution

```python
async def track_entities_from_killmail(db, km: Killmail):
    """Extract and track all entities mentioned in a killmail."""
    entities_seen = set()

    # Track victim
    if km.victim_character_id:
        entities_seen.add(km.victim_character_id)
        await upsert_entity(db, km.victim_character_id, "character")
        await increment_deaths(db, km.victim_character_id)

    # Track attackers
    for attacker_id in km.attacker_character_ids:
        if attacker_id and attacker_id not in entities_seen:
            entities_seen.add(attacker_id)
            await upsert_entity(db, attacker_id, "character")
            await increment_kills(db, attacker_id)


async def upsert_entity(db, entity_id: str, entity_type: str, name: str | None = None):
    """Idempotent entity upsert — update last_seen, optionally name."""
    await db.execute(
        """
        INSERT INTO entities (entity_id, entity_type, name, last_seen)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(entity_id) DO UPDATE SET
            last_seen = datetime('now'),
            name = COALESCE(excluded.name, entities.name)
        """,
        (entity_id, entity_type, name),
    )
```

## World API Sync Patterns

### Tribe Sync (World API -> Local DB)

```python
async def sync_tribes(db) -> dict:
    """Idempotent tribe sync from World API."""
    api_tribes = await get_tribes()
    created, updated = 0, 0

    for t in api_tribes:
        world_id = str(t.get("id", ""))
        if not world_id:
            continue

        name = t.get("name", "Unknown")
        name_short = t.get("nameShort")

        existing = await db.fetchone(
            "SELECT * FROM entities WHERE entity_id = ? AND entity_type = 'tribe'",
            (world_id,),
        )
        if existing:
            await db.execute(
                "UPDATE entities SET name = ?, last_seen = datetime('now') WHERE entity_id = ?",
                (name, world_id),
            )
            updated += 1
        else:
            await upsert_entity(db, world_id, "tribe", name)
            created += 1

    return {"created": created, "updated": updated, "total": len(api_tribes)}
```

### Member Sync with Name Normalization

```python
async def sync_tribe_members(db, tribe_id: str, api_members: list[dict]) -> dict:
    """Sync tribe member list from World API response."""
    synced, new = 0, 0
    NULL_ADDRESS = "0x0000000000000000000000000000000000000000"

    for m in api_members:
        address = m.get("address", "")
        name = m.get("name", "")
        entity_id = str(m.get("id", ""))

        # Skip null/empty addresses
        if not address or address == NULL_ADDRESS:
            continue

        # Handle DEFAULT name placeholder
        clean_name = name if name != "DEFAULT" else None

        existing = await db.fetchone(
            "SELECT * FROM entities WHERE wallet_address = ?", (address,)
        )
        if existing:
            await db.execute(
                """UPDATE entities SET
                    tribe_id = ?,
                    name = COALESCE(?, entities.name),
                    last_seen = datetime('now')
                WHERE wallet_address = ?""",
                (tribe_id, clean_name, address),
            )
            synced += 1
        else:
            await db.execute(
                """INSERT INTO entities (entity_id, entity_type, name, wallet_address, tribe_id)
                VALUES (?, 'character', ?, ?, ?)""",
                (entity_id or address, clean_name, address, tribe_id),
            )
            new += 1

    return {"synced": synced, "new": new}
```

## Discord Bot Integration

```python
import discord
from discord import app_commands

class FrontierBot(discord.Client):
    def __init__(self, db):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.db = db

    async def setup_hook(self):
        await self.tree.sync()


bot = FrontierBot(db)


@bot.tree.command(name="killboard", description="Recent killmails")
@app_commands.describe(limit="Number of kills to show (default 5)")
async def killboard(interaction: discord.Interaction, limit: int = 5):
    kills = await bot.db.fetchall(
        "SELECT * FROM killmails ORDER BY timestamp DESC LIMIT ?", (limit,)
    )
    if not kills:
        await interaction.response.send_message("No killmails recorded yet.")
        return

    lines = []
    for km in kills:
        ts = km["timestamp"][:16]
        victim = km["victim_character_id"] or "Unknown"
        n_attackers = km["attacker_count"]
        lines.append(f"`{ts}` | Victim: `{victim[:12]}...` | Attackers: {n_attackers}")

    embed = discord.Embed(title="Recent Killmails", description="\n".join(lines))
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stats", description="Pipeline statistics")
async def stats(interaction: discord.Interaction):
    km_count = await bot.db.fetchone("SELECT COUNT(*) as c FROM killmails")
    sa_count = await bot.db.fetchone("SELECT COUNT(*) as c FROM smart_assemblies")
    entity_count = await bot.db.fetchone("SELECT COUNT(*) as c FROM entities")

    embed = discord.Embed(title="Frontier Data Pipeline")
    embed.add_field(name="Killmails", value=f"{km_count['c']:,}")
    embed.add_field(name="Smart Assemblies", value=f"{sa_count['c']:,}")
    embed.add_field(name="Entities Tracked", value=f"{entity_count['c']:,}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="lookup", description="Lookup a pilot by wallet address")
@app_commands.describe(address="Wallet address (0x...)")
async def lookup(interaction: discord.Interaction, address: str):
    entity = await bot.db.fetchone(
        "SELECT * FROM entities WHERE wallet_address = ?", (address,)
    )
    if not entity:
        await interaction.response.send_message(f"No data for `{address[:12]}...`")
        return

    embed = discord.Embed(title=entity["name"] or "Unknown Pilot")
    embed.add_field(name="Address", value=f"`{address[:20]}...`")
    embed.add_field(name="Kills", value=str(entity.get("kill_count", 0)))
    embed.add_field(name="Deaths", value=str(entity.get("death_count", 0)))
    embed.add_field(name="Tribe", value=entity.get("tribe_id") or "None")
    embed.add_field(name="First Seen", value=entity["first_seen"][:10])
    await interaction.response.send_message(embed=embed)
```

## Ingestion Metrics Pattern

```python
@dataclass
class IngestionStats:
    """Track metrics per polling cycle."""
    endpoint: str
    fetched: int = 0
    new: int = 0
    updated: int = 0
    errors: int = 0
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def log(self):
        logger.info(
            "ingestion endpoint=%s fetched=%d new=%d updated=%d errors=%d duration_ms=%.1f",
            self.endpoint, self.fetched, self.new, self.updated, self.errors, self.duration_ms,
        )
```

## SQLite Cross-Thread Usage (FastAPI)

When serving SQLite data through FastAPI, use `check_same_thread=False`:

```python
import aiosqlite

async def get_db():
    db = await aiosqlite.connect("frontier.db")
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
```

For synchronous SQLite with FastAPI (not recommended but works):

```python
import sqlite3
conn = sqlite3.connect("frontier.db", check_same_thread=False)
```

## Static Data Fallback

For endpoints that change infrequently (types, blueprints), maintain local JSON:

```python
STATIC_DATA_DIR = Path(__file__).parent / "data"

def load_static_fallback(filename: str) -> list[dict]:
    """Load static JSON when World API is unavailable."""
    path = STATIC_DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text())
    logger.warning("Static fallback %s not found", filename)
    return []

# Usage:
async def get_blueprints() -> list[dict]:
    try:
        return await fetch_from_world_api("/v2/types")
    except Exception:
        return load_static_fallback("blueprints.json")
```

Refresh static data periodically:
```bash
# Cron job to snapshot World API types
curl -s "https://blockchain-gateway-stillness.live.tech.evefrontier.com/v2/types" | \
  python3 -m json.tool > data/blueprints.json
```
