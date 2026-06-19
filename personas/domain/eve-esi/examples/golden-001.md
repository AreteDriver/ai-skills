# Eve Esi Response
## Example Output
```
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
    return re
```
