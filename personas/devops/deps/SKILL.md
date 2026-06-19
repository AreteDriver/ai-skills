---
name: deps
description: Check for outdated dependencies and security vulnerabilities. Invoke with /deps.
lifecycle: experimental
---

# Deps Skill

Check project dependencies for updates and security issues.

## Usage

```
/deps              # Check all dependencies
/deps --outdated   # Show outdated only
/deps --security   # Security audit
/deps --update     # Update to latest
```

## Process

1. **Check outdated packages**
   ```bash
   source .venv/bin/activate
   pip list --outdated --format=columns
   ```

2. **Security audit**
   ```bash
   # Install pip-audit if needed
   pip install pip-audit

   # Run audit
   pip-audit
   ```

3. **Show dependency tree**
   ```bash
   pip install pipdeptree
   pipdeptree
   ```

## Quick Commands

```bash
# List outdated
pip list --outdated

# Update all (careful!)
pip list --outdated --format=freeze | cut -d= -f1 | xargs pip install --upgrade

# Update specific package
pip install --upgrade requests

# Check for conflicts
pip check

# Export current versions
pip freeze > requirements.lock
```

## Security Audit

```bash
# Using pip-audit
pip-audit

# Using safety (alternative)
pip install safety
safety check

# Check specific requirements file
pip-audit -r requirements.txt
```

## Output Format

```
Outdated Packages:
Package    Current  Latest
---------  -------  ------
requests   2.28.0   2.31.0
pytest     7.2.0    7.4.0

Security Issues:
Found 1 vulnerability:
- requests 2.28.0: CVE-2023-XXXXX (upgrade to 2.31.0)

Dependency Tree:
my-package==1.0.0
├── requests==2.31.0
│   ├── certifi>=2017.4.17
│   └── urllib3>=1.21.1
└── PyQt6==6.6.0
```

## Updating Dependencies

```bash
# Update pyproject.toml deps
# Then reinstall
pip install -e . --upgrade

# Or update lock file
pip-compile pyproject.toml -o requirements.lock
pip install -r requirements.lock
```

## Tips

- Check deps weekly for security updates
- Pin major versions in pyproject.toml
- Use requirements.lock for reproducible builds
- Test after updates: `pytest`
