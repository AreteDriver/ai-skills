---
name: api-client
version: "2.0.0"
description: "Authenticated HTTP API client with retry logic, rate limiting, response parsing, and structured error handling. Supports OAuth2, API key, and bearer token auth."
metadata: {"openclaw": {"emoji": "🔗", "os": ["darwin", "linux", "win32"]}}
type: agent
category: integrations
risk_level: low
trust: autonomous
parallel_safe: true
agent: system
consensus: any
tools: ["Bash", "WebFetch"]
---

# API Client

Authenticated HTTP API client with retry logic, rate limiting, pagination, and structured response parsing. Supports OAuth2, API key, bearer token, and basic auth.

## Role

You are an HTTP API integration specialist. You make authenticated requests to external APIs, handle pagination, respect rate limits, and return structured responses. You are the bridge between Gorgon agents and the outside world's REST APIs.

## When to Use

Use this skill when:
- Making authenticated HTTP requests to external REST APIs
- Fetching paginated data from API endpoints that return collections
- Executing batch requests against multiple endpoints with concurrency control
- Integrating with third-party services (Slack, Jira, Stripe, etc.) via their REST APIs

## When NOT to Use

Do NOT use this skill when:
- Scraping HTML web pages — use the web-scrape skill instead, because HTML parsing requires DOM extraction, not JSON response handling
- Searching the web for information — use the web-search skill instead, because search engines need query formulation, not direct API calls
- Running git commands or GitHub CLI operations — use the github-operations skill instead, because git workflows need branch protection and commit conventions
- Making requests to internal/local services with no auth — use the Bash tool with curl directly, because skill overhead is unnecessary for simple unauthenticated requests

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
- Hardcode API keys, tokens, or credentials — credential leaks in code compromise all API access
- Ignore rate limit headers (429 responses) — continued requests after rate limiting causes IP bans or account suspension
- Retry on 4xx client errors (except 429) — client errors indicate bad requests that won't succeed on retry
- Make unbounded requests without pagination limits — unbounded fetching exhausts memory and API quotas
- Expose credentials in logs or error messages — log output is often stored in plaintext and shared across teams
- Skip TLS verification — disabling TLS opens the connection to man-in-the-middle attacks

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

## Capabilities

### request
Make a single authenticated HTTP request. Use when calling a specific API endpoint with known method, path, and parameters. Do NOT use for bulk operations — use batch instead.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state which API endpoint and what data it expects
- **Inputs:**
  - `method` (string, required) — HTTP method: GET, POST, PUT, PATCH, DELETE
  - `path` (string, required) — URL path appended to base_url
  - `params` (dict, optional) — query string parameters
  - `json_body` (dict, optional) — JSON request body
  - `headers` (dict, optional) — additional HTTP headers
  - `timeout` (integer, optional, default: 30) — request timeout in seconds
- **Outputs:**
  - `success` (boolean) — whether status code is 2xx
  - `status_code` (integer) — HTTP response status code
  - `headers` (dict) — response headers
  - `body` (any) — parsed response body (JSON object, text, or binary)
  - `duration_ms` (integer) — request duration in milliseconds
  - `retries` (integer) — number of retries performed
  - `error` (string or null) — error message if request failed
- **Post-execution:** Check success flag. For non-2xx responses, examine body and headers for error details. For 401 responses with OAuth2, attempt token refresh before failing. Track rate limit headers for subsequent requests.

### paginate
Fetch all pages of a paginated endpoint. Use when the API returns collections across multiple pages. Do NOT use without setting max_pages — unbounded pagination can exhaust quotas.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes — but each pagination sequence is sequential internally
- **Intent required:** yes — agent must state what collection is being fetched and expected size
- **Inputs:**
  - `path` (string, required) — API endpoint path
  - `params` (dict, optional) — base query parameters
  - `page_param` (string, optional, default: "page") — name of the page parameter
  - `per_page_param` (string, optional, default: "per_page") — name of the per-page parameter
  - `per_page` (integer, optional, default: 100) — items per page
  - `results_key` (string, optional) — JSON key containing the results array
  - `max_pages` (integer, optional, default: 100) — safety cap on pages fetched
- **Outputs:**
  - `results` (array) — aggregated list of all results across pages
  - `pages_fetched` (integer) — number of pages retrieved
  - `total_items` (integer) — total count of items collected
- **Post-execution:** Verify total_items matches expectations. If pages_fetched equals max_pages, there may be more data — report truncation. Check for duplicate items across page boundaries.

### batch
Execute multiple requests with concurrency control. Use when making several related API calls that can proceed independently. Do NOT use when requests depend on each other's responses — sequence them with individual request calls instead.

- **Risk:** Medium
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state the purpose of the batch and expected request count
- **Inputs:**
  - `requests` (array, required) — list of request specs [{method, path, params, json_body}]
  - `concurrency` (integer, optional, default: 5) — maximum parallel requests
  - `stop_on_error` (boolean, optional, default: false) — halt batch on first failure
- **Outputs:**
  - `results` (array) — list of APIResponse objects, one per request
  - `succeeded` (integer) — count of successful requests
  - `failed` (integer) — count of failed requests
- **Post-execution:** Check failed count. Review individual error messages for failed requests. If rate-limited mid-batch, the remaining requests may need to be retried after the limit resets.

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

## Output Format

### API Response
Use when: Returning results from any API request

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

## Verification

### Pre-completion Checklist
Before reporting API operations as complete, verify:
- [ ] Authentication was applied (credentials loaded from environment)
- [ ] Rate limit headers were tracked and respected
- [ ] Response was parsed into structured data (not raw text)
- [ ] No credentials appear in logs, output, or error messages
- [ ] Pagination was bounded by max_pages limit

### Checkpoints
Pause and reason explicitly when:
- Authentication fails (401) — check if token is expired, attempt refresh for OAuth2 before failing
- Rate limit is hit (429) — wait for Retry-After duration before any further requests
- Response body is unexpectedly empty or malformed — verify the Content-Type header matches expected format
- Pagination reaches max_pages limit — report truncation, do not silently drop remaining data
- About to make a destructive API call (DELETE, PUT with full replacement) — verify intent and target

## Error Handling

### Escalation Ladder

| Error Type | Action | Max Retries |
|------------|--------|-------------|
| 2xx Success | Return parsed response | — |
| 400 Bad Request | Return error, do not retry | 0 |
| 401 Unauthorized | Attempt token refresh (OAuth2), then fail | 1 |
| 403 Forbidden | Return error, do not retry | 0 |
| 404 Not Found | Return error, do not retry | 0 |
| 429 Rate Limited | Wait for Retry-After header, then retry | 3 |
| 5xx Server Error | Retry with exponential backoff | 3 |
| Timeout | Return timeout error | 0 |
| Connection Error | Return connection error | 0 |
| Same error after retries | Stop, report what was attempted | — |

### Self-Correction
If this skill's protocol is violated:
- Credentials exposed in output: immediately flag as security incident, recommend rotation
- Rate limit ignored: pause all requests, wait for the reset window, acknowledge the violation
- 4xx error retried: stop retrying, return the error response directly
- TLS verification skipped: halt the request, re-enable verification, report the violation

## Constraints

- Credentials from environment variables only
- TLS required for all production requests
- Default timeout: 30 seconds
- Maximum pagination: 100 pages
- Rate limit: respect X-RateLimit-* headers
- No credential logging (mask in debug output)
- Maximum response body: 50MB
