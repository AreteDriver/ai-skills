---
name: env
description: Environment Management
lifecycle: experimental
---

# /env - Environment Management

Manage .env files, secrets, and environment configuration.

## Usage
```
/env                     # Audit current env setup
/env --init              # Create .env from .env.example
/env --check             # Verify all required vars set
/env --rotate KEY        # Rotate a secret
```

## What This Skill Does

1. **Audit Setup** - Check .env, .env.example, .gitignore
2. **Validate Config** - Required vars present and valid
3. **Security Check** - No secrets in code or git
4. **Generate Template** - Create .env.example from code
5. **Document Vars** - What each variable does

## Environment File Structure

### .env (local, never commit)
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# API Keys
API_KEY=sk-xxxxxxxxxxxx
SECRET_KEY=your-secret-key-here

# Feature Flags
DEBUG=true
LOG_LEVEL=debug
```

### .env.example (commit this)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# API Keys (get from dashboard)
API_KEY=
SECRET_KEY=

# Feature Flags
DEBUG=false
LOG_LEVEL=info
```

### .gitignore (required entries)
```
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
secrets/
```

## Environment Audit Report

```markdown
# Environment Audit: [Project]

## Files
| File | Status | Notes |
|------|--------|-------|
| .env | Exists | 12 variables |
| .env.example | Missing | Should create |
| .gitignore | OK | .env excluded |

## Variables

### Required (Missing)
| Variable | Used In | Purpose |
|----------|---------|---------|
| `API_KEY` | api.py:23 | External API auth |

### Required (Set)
| Variable | Status | Validated |
|----------|--------|-----------|
| `DATABASE_URL` | Set | Valid URL format |
| `SECRET_KEY` | Set | Sufficient length |

### Optional
| Variable | Default | Current |
|----------|---------|---------|
| `DEBUG` | false | true |
| `LOG_LEVEL` | info | debug |

## Security Issues
- [ ] `.env` in .gitignore
- [x] No secrets in source code
- [ ] No secrets in git history

## Recommendations
1. Create `.env.example` with all variables
2. Add `API_KEY` to .env
3. Run `git log -p | grep -i secret` to check history
```

## Variable Discovery

```python
# Find env var usage in Python
import os
os.environ.get("VAR_NAME")
os.getenv("VAR_NAME")

# Find in Rust
std::env::var("VAR_NAME")

# Find in shell scripts
$VAR_NAME
${VAR_NAME}
```

## Security Best Practices

1. **Never commit .env** - Always in .gitignore
2. **Use .env.example** - Document required vars without values
3. **Validate on startup** - Fail fast if missing required vars
4. **Rotate secrets** - Regular rotation schedule
5. **Use secret managers** - For production (Vault, AWS Secrets, etc.)
6. **Audit git history** - Check for accidentally committed secrets

## Instructions for Claude

When /env is invoked:

1. **Find env files** - .env, .env.example, .env.local
2. **Check .gitignore** - Ensure .env excluded
3. **Discover variables** - Grep for env var usage in code
4. **Categorize vars** - Required vs optional, secrets vs config
5. **Validate values** - Format checks (URLs, keys)
6. **Security scan** - Check for secrets in code
7. **Generate .env.example** - If missing
8. **Report findings** - Audit with recommendations
