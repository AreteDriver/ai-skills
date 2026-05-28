---
name: lint
description: Run ruff linter and formatter. Checks code quality and auto-fixes issues. Invoke with /lint or /lint <path>.
---

# Lint Skill

Run ruff to check and format Python code.

## Usage

```
/lint              # Check entire project
/lint src/         # Check specific directory
/lint --fix        # Auto-fix issues
/lint --format     # Format code
```

## Process

1. **Check for ruff**
   ```bash
   which ruff || pip install ruff
   ```

2. **Run linter**
   ```bash
   # Check for issues
   ruff check .

   # Check with auto-fix
   ruff check . --fix

   # Format code
   ruff format .

   # Check formatting without changing
   ruff format --check .
   ```

3. **Report issues**
   - Error count by type
   - Files with issues
   - Suggested fixes

## Quick Commands

```bash
# Full lint + format
ruff check . && ruff format .

# Fix everything
ruff check . --fix && ruff format .

# Check single file
ruff check src/main.py

# Show specific rule info
ruff rule E501
```

## Common Issues

| Code | Issue | Fix |
|------|-------|-----|
| E501 | Line too long | Break line or disable |
| F401 | Unused import | Remove it |
| F841 | Unused variable | Remove or prefix with _ |
| I001 | Import order | Run `ruff check --fix` |
| UP035 | Deprecated typing | Use collections.abc |

## Configuration

In `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
ignore = ["E501"]  # Optional: ignore long lines
```

## Output Format

```
src/api.py:45:1: F401 `os` imported but unused
src/utils.py:20:5: F841 Local variable `x` assigned but never used
Found 2 errors (1 fixable with --fix)
```
