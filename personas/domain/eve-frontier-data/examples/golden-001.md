# Eve Frontier Data Response
## Example Output
```
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
            asyncio.create_task(self._poll_
```
