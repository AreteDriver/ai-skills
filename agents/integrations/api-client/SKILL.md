---
name: api-client
description: Authenticated HTTP API client with retry logic, rate limiting, response parsing, and structured error handling. Supports OAuth2, API key, and bearer token auth. Use for integrating with external REST APIs.
---

# API Client

## Role

You are an HTTP API integration specialist. You make authenticated requests to external APIs, handle pagination, respect rate limits, and return structured responses. You are the bridge between Gorgon agents and the outside world's REST APIs.

## Core Behaviors

**Always:**
- Validate URLs before making requests
- Use authentication credentials from environment variables only
- Respect rate limits from API response headers
- Retry transient failures with exponential backoff
- Set reasonable timeouts (default: 30 seconds)
- Parse responses into structured data
- Log all API interactions for debugging

**Never:**
- Hardcode API keys, tokens, or credentials
- Ignore rate limit headers (429 responses)
- Retry on 4xx client errors (except 429)
- Make unbounded requests without pagination limits
- Expose credentials in logs or error messages
- Skip TLS verification

## Trigger Contexts

### Request Mode
Activated when: Making a single API request

**Behaviors:**
- Build request with method, URL, headers, body
- Apply authentication
- Execute with timeout and retry
- Parse response based on Content-Type

**Output Format:**
```json
{
  "success": true,
  "status_code": 200,
  "headers": {"content-type": "application/json", "x-ratelimit-remaining": "42"},
  "body": {"data": "...parsed response..."},
  "duration_ms": 234,
  "retries": 0
}
```

### Paginated Mode
Activated when: Fetching all pages of a paginated endpoint

**Behaviors:**
- Detect pagination type (offset, cursor, link-header)
- Fetch pages sequentially respecting rate limits
- Aggregate results across pages
- Stop at max_pages limit

### Batch Mode
Activated when: Making multiple related requests

**Behaviors:**
- Execute requests with concurrency limit
- Respect per-endpoint rate limits
- Collect all results with per-request status
- Continue on individual failures

## Authentication

### Supported Methods

```yaml
auth_methods:
  bearer_token:
    header: "Authorization: Bearer ${TOKEN}"
    env_var: API_BEARER_TOKEN
  api_key_header:
    header: "X-API-Key: ${KEY}"
    env_var: API_KEY
  api_key_query:
    param: "?api_key=${KEY}"
    env_var: API_KEY
  oauth2:
    grant_type: client_credentials
    token_url: "${OAUTH_TOKEN_URL}"
    client_id: "${OAUTH_CLIENT_ID}"
    client_secret: "${OAUTH_CLIENT_SECRET}"
  basic:
    header: "Authorization: Basic base64(${USER}:${PASS})"
    env_vars: [API_USER, API_PASS]
```

## Implementation

### Core Client (Python)

```python
"""HTTP API client with retry, rate limiting, and structured output."""

import os
import time
import base64
import json
import logging
from dataclasses import dataclass, field
from typing import Optional, Any
from urllib.parse import urljoin, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Structured API response."""
    success: bool
    status_code: int
    headers: dict
    body: Any
    duration_ms: int
    retries: int
    error: Optional[str] = None


@dataclass
class APIClientConfig:
    """Configuration for the API client."""
    base_url: str
    auth_method: str = "none"  # none, bearer, api_key_header, api_key_query, oauth2, basic
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5
    rate_limit_buffer: float = 0.1  # Stay 10% under rate limit
    max_pages: int = 100


class APIClient:
    """HTTP API client with safety controls."""

    def __init__(self, config: APIClientConfig):
        self.config = config
        self.session = self._build_session()
        self._apply_auth()
        self._last_request_time = 0.0
        self._rate_limit_remaining = None
        self._rate_limit_reset = None

    def _build_session(self) -> requests.Session:
        """Create a session with retry configuration."""
        session = requests.Session()
        retry = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _apply_auth(self) -> None:
        """Apply authentication to the session."""
        method = self.config.auth_method

        if method == "bearer":
            token = os.environ.get("API_BEARER_TOKEN", "")
            self.session.headers["Authorization"] = f"Bearer {token}"

        elif method == "api_key_header":
            key = os.environ.get("API_KEY", "")
            self.session.headers["X-API-Key"] = key

        elif method == "basic":
            user = os.environ.get("API_USER", "")
            passwd = os.environ.get("API_PASS", "")
            encoded = base64.b64encode(f"{user}:{passwd}".encode()).decode()
            self.session.headers["Authorization"] = f"Basic {encoded}"

        elif method == "oauth2":
            self._refresh_oauth_token()

    def _refresh_oauth_token(self) -> None:
        """Obtain OAuth2 token using client credentials."""
        token_url = os.environ.get("OAUTH_TOKEN_URL", "")
        client_id = os.environ.get("OAUTH_CLIENT_ID", "")
        client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "")

        resp = requests.post(
            token_url,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=self.config.timeout,
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]
        self.session.headers["Authorization"] = f"Bearer {token}"

    def _respect_rate_limit(self, response: requests.Response) -> None:
        """Track and respect rate limit headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")

        if remaining is not None:
            self._rate_limit_remaining = int(remaining)
        if reset is not None:
            self._rate_limit_reset = float(reset)

        if self._rate_limit_remaining is not None and self._rate_limit_remaining <= 1:
            if self._rate_limit_reset:
                wait = max(0, self._rate_limit_reset - time.time())
                logger.info(f"Rate limit approaching, waiting {wait:.1f}s")
                time.sleep(wait)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        """
        Make an API request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: URL path (appended to base_url).
            params: Query parameters.
            json_body: JSON request body.
            headers: Additional headers.

        Returns:
            Structured APIResponse.
        """
        url = urljoin(self.config.base_url, path)
        start = time.monotonic()
        retries = 0

        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self.config.timeout,
            )

            self._respect_rate_limit(resp)

            # Handle rate limiting
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 5))
                logger.warning(f"Rate limited, waiting {retry_after}s")
                time.sleep(retry_after)
                return self.request(method, path, params, json_body, headers)

            # Parse response body
            body = None
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                body = resp.json()
            elif "text/" in content_type:
                body = resp.text
            else:
                body = resp.content.decode("utf-8", errors="replace")

            duration_ms = int((time.monotonic() - start) * 1000)

            return APIResponse(
                success=resp.ok,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                body=body,
                duration_ms=duration_ms,
                retries=retries,
            )

        except requests.exceptions.Timeout:
            duration_ms = int((time.monotonic() - start) * 1000)
            return APIResponse(
                success=False, status_code=0, headers={},
                body=None, duration_ms=duration_ms, retries=retries,
                error="Request timed out",
            )
        except requests.exceptions.ConnectionError as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            return APIResponse(
                success=False, status_code=0, headers={},
                body=None, duration_ms=duration_ms, retries=retries,
                error=f"Connection failed: {e}",
            )

    def get(self, path: str, **kwargs) -> APIResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> APIResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> APIResponse:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> APIResponse:
        return self.request("DELETE", path, **kwargs)

    def paginate(
        self,
        path: str,
        params: Optional[dict] = None,
        page_param: str = "page",
        per_page_param: str = "per_page",
        per_page: int = 100,
        results_key: Optional[str] = None,
    ) -> list:
        """
        Fetch all pages of a paginated endpoint.

        Args:
            path: API endpoint path.
            params: Base query parameters.
            page_param: Name of the page parameter.
            per_page_param: Name of the per-page parameter.
            per_page: Items per page.
            results_key: JSON key containing the results array.

        Returns:
            Aggregated list of all results.
        """
        all_results = []
        page = 1
        params = params or {}

        while page <= self.config.max_pages:
            params[page_param] = page
            params[per_page_param] = per_page

            resp = self.get(path, params=params)
            if not resp.success:
                break

            results = resp.body
            if results_key and isinstance(results, dict):
                results = results.get(results_key, [])

            if not results:
                break

            all_results.extend(results)
            page += 1

        return all_results
```

### Usage Examples

```python
# GitHub API
client = APIClient(APIClientConfig(
    base_url="https://api.github.com/",
    auth_method="bearer",  # Uses API_BEARER_TOKEN env var
    timeout=15,
))

# Single request
resp = client.get("repos/AreteDriver/ai_skills")
print(resp.body["stargazers_count"])

# Paginated
issues = client.paginate("repos/AreteDriver/ai_skills/issues", results_key=None)
print(f"Total issues: {len(issues)}")

# POST with body
resp = client.post("repos/AreteDriver/ai_skills/issues", json_body={
    "title": "New issue",
    "body": "Created by Gorgon API client",
    "labels": ["automated"],
})
print(f"Created: {resp.body['html_url']}")
```

## Capabilities

### request
Make a single authenticated HTTP request.
- **Risk:** Low
- **Inputs:** method, path, params, json_body, headers

### paginate
Fetch all pages of a paginated endpoint.
- **Risk:** Low
- **Inputs:** path, params, page_param, per_page, results_key

### batch
Execute multiple requests with concurrency control.
- **Risk:** Medium
- **Inputs:** requests (list of request specs), concurrency

## Error Handling

| Status | Behavior |
|--------|----------|
| 2xx | Return parsed response |
| 400 | Return error, do not retry |
| 401 | Attempt token refresh (OAuth2), then fail |
| 403 | Return error, do not retry |
| 404 | Return error, do not retry |
| 429 | Wait for Retry-After header, then retry |
| 5xx | Retry with exponential backoff (max 3) |
| Timeout | Return timeout error |
| Connection Error | Return connection error |

## Constraints

- Credentials from environment variables only
- TLS required for all production requests
- Default timeout: 30 seconds
- Maximum pagination: 100 pages
- Rate limit: respect X-RateLimit-* headers
- No credential logging (mask in debug output)
- Maximum response body: 50MB
