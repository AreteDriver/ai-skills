# Golden Example: Systematic Debugging

Demonstrates the SSE debugging mode: form hypothesis, gather evidence,
identify root cause, fix, and prevent.

## Input: Bug Report

> Users report that password reset emails sometimes go to the wrong user.
> It happens intermittently — maybe 1 in 50 resets. No pattern in timing.

```python
# auth/password_reset.py

import secrets
from datetime import datetime, timedelta

# In-memory token store (Redis in production)
reset_tokens = {}

def request_password_reset(email: str) -> str:
    """Generate a password reset token for the given email."""
    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal whether email exists
        return "If this email exists, a reset link has been sent."

    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "user_id": user.id,
        "email": email,
        "expires": datetime.utcnow() + timedelta(hours=1),
    }

    send_reset_email(email, token)
    return "If this email exists, a reset link has been sent."


def reset_password(token: str, new_password: str) -> bool:
    """Reset password using a valid token."""
    if token not in reset_tokens:
        return False

    data = reset_tokens[token]
    if datetime.utcnow() > data["expires"]:
        del reset_tokens[token]
        return False

    user = User.query.get(data["user_id"])
    user.password_hash = hash_password(new_password)
    db.session.commit()

    del reset_tokens[token]
    return True
```

## Expected SSE Output

```markdown
## Debugging: Password reset emails going to wrong user

### Hypothesis
The token store is a plain dict, and there's a race condition when two users
request password resets concurrently. But that wouldn't cause emails to the
*wrong* user — it would cause token collisions at worst. Let me look more
carefully.

Actually, the bug is simpler: `secrets.token_urlsafe(32)` can theoretically
collide, but with 256 bits of entropy that's astronomically unlikely. The real
issue is more subtle — let me check the token store lifecycle.

**Revised hypothesis:** Old tokens are never cleaned up. The `reset_tokens` dict
grows forever. But that doesn't explain wrong-user emails either.

**Third look:** Wait — the token store maps `token → {user_id, email}`. If
two users request resets and the second one generates the same token (nearly
impossible), the first user's entry would be overwritten. But that's not the
1-in-50 rate we're seeing.

**Root cause found:** The bug isn't in this code — it's in `send_reset_email`.
But this code *does* have a real problem: **there's no invalidation of previous
tokens for the same user.** If user A requests a reset, then requests another,
both tokens are valid. This isn't the reported bug but it's a security issue.

For the actual "wrong user" bug at 1-in-50 rate, I need to see `send_reset_email`.
This is likely an email templating or queuing issue where emails are batched and
a shared mutable template variable leaks across renders.

### Evidence
1. The code itself doesn't have an obvious wrong-user path — the token→email
   mapping is deterministic
2. 1-in-50 is too frequent for a cryptographic collision
3. The intermittent nature suggests a concurrency issue, likely in the email
   sending layer
4. The token store has no per-user deduplication (secondary issue)

### Immediate Action
Request access to `send_reset_email` implementation. In the meantime, fix
the known issues in this file:

```python
# auth/password_reset.py — fixed

def request_password_reset(email: str) -> str:
    user = User.query.filter_by(email=email).first()
    if not user:
        return "If this email exists, a reset link has been sent."

    # Invalidate any existing tokens for this user
    reset_tokens_to_remove = [
        t for t, data in reset_tokens.items()
        if data["user_id"] == user.id
    ]
    for t in reset_tokens_to_remove:
        del reset_tokens[t]

    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "user_id": user.id,
        "email": email,
        "expires": datetime.utcnow() + timedelta(hours=1),
    }

    # Pass user_id explicitly — don't rely on email alone
    send_reset_email(user_id=user.id, email=email, token=token)
    return "If this email exists, a reset link has been sent."
```

### Prevention
1. Move from in-memory dict to Redis with TTL keys — eliminates manual expiry
   and the unbounded growth problem
2. Add a `user_id` foreign key to the token store so lookups go both directions
3. Add an integration test that sends two concurrent reset requests for
   different users and verifies each email has the correct token
4. Log `(user_id, token_prefix, email)` on every reset request so the wrong-user
   bug can be correlated in production logs
```

## Why This Is Good

1. **Shows the work** — doesn't jump to the answer, shows hypothesis refinement
2. **Honest about uncertainty** — "I need to see `send_reset_email`" instead of
   guessing
3. **Fixes what it can** — even though the root cause is elsewhere, it fixes
   the token invalidation gap it found along the way
4. **Prevention is actionable** — specific steps, not vague "add more tests"
5. **Doesn't over-scope** — fixes the file it was given, asks for what it needs
