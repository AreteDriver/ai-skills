# Golden Example: Critical Security Finding

This example shows what a well-structured review looks like when a critical
security vulnerability is found. Note the specific location, clear impact,
and concrete fix with code.

## Input: PR diff

```python
# api/routes/users.py — New endpoint for user lookup

@app.route("/api/users")
def get_user():
    user_id = request.args.get("id")
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return jsonify(result.fetchone())
```

## Expected Review Output

```markdown
## Code Review Summary

### Overview
New user lookup endpoint with a critical SQL injection vulnerability that must
be fixed before merge.

### Critical Issues
- **api/routes/users.py:5** — SQL injection via string interpolation
  - Impact: Attacker can read, modify, or delete any data in the database by
    crafting a malicious `id` parameter (e.g., `1 OR 1=1; DROP TABLE users`)
  - Fix: Use parameterized queries:
    ```python
    query = "SELECT * FROM users WHERE id = :id"
    result = db.execute(text(query), {"id": user_id})
    ```

- **api/routes/users.py:6** — No input validation on user_id
  - Impact: Even with parameterized queries, unvalidated input can cause
    unexpected behavior (e.g., passing a string when an integer is expected)
  - Fix: Validate and cast the input:
    ```python
    try:
        user_id = int(request.args.get("id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user ID"}), 400
    ```

### Suggestions
- **api/routes/users.py:6** — No handling for user not found
  - Recommendation: Return 404 instead of null/None:
    ```python
    row = result.fetchone()
    if row is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(row))
    ```

### Nits
(none)

### Security Considerations
- Endpoint has no authentication — anyone can look up any user
- Response returns `SELECT *` which may expose sensitive columns (password hash,
  email, etc.) — select only the fields needed for the response

### What's Good
- Clean, minimal endpoint structure
- Correct use of `jsonify` for response formatting

### Testing
- [ ] Unit tests cover new functionality
- [ ] Edge cases are tested (missing id, non-numeric id, nonexistent user)
- [ ] No test regressions

**Verdict: request_changes** — Critical SQL injection must be fixed.
```

## Why This Review Is Good

1. **Severity is correct** — SQL injection is unambiguously critical
2. **Location is exact** — file:line for every finding
3. **Impact is concrete** — explains what an attacker can do, not just "this is bad"
4. **Fix is copy-pasteable** — reviewer provides working code, not just "use parameterized queries"
5. **Doesn't pile on** — notes the auth gap in security considerations without making it a critical finding (it's a design decision, not a bug in this PR)
6. **Acknowledges the good** — even a flawed PR has positive aspects worth noting
