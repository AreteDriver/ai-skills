# /migrate - Code Migration Helper

Assist with dependency upgrades, API changes, and version migrations.

## Usage
```
/migrate dep requests 2.28 2.31    # Upgrade dependency
/migrate python 3.9 3.12           # Python version upgrade
/migrate framework django 4.0 5.0  # Framework upgrade
/migrate --breaking                # Find breaking changes only
```

## What This Skill Does

1. **Identify Changes** - Breaking changes, deprecations, new features
2. **Find Affected Code** - Grep for deprecated APIs
3. **Generate Migration Plan** - Step-by-step upgrade path
4. **Apply Changes** - Update code for new APIs
5. **Verify** - Run tests, check for issues

## Migration Report Format

```markdown
# Migration Report: [package] v1.0 → v2.0

## Summary
| Category | Count |
|----------|-------|
| Breaking Changes | 3 |
| Deprecations | 5 |
| New Features | 12 |

## Breaking Changes

### 1. `old_function()` removed
**Replacement**: `new_function()`
**Affected Files**: 5

```python
# Before
from package import old_function
result = old_function(arg)

# After
from package import new_function
result = new_function(arg, new_required_arg=True)
```

**Files to Update**:
- src/module.py:23
- src/other.py:45
- tests/test_module.py:12

### 2. Return type changed for `process()`
**Before**: `dict`
**After**: `ProcessResult` (dataclass)

```python
# Before
result = process(data)
value = result["key"]

# After
result = process(data)
value = result.key
```

## Deprecations (warnings now, removed in v3.0)

### `legacy_api()` deprecated
**Replacement**: `modern_api()`
**Deadline**: v3.0

## New Features Worth Adopting

### Async support added
```python
# Now available
result = await package.async_process(data)
```

## Migration Steps

1. [ ] Update dependency version in pyproject.toml
2. [ ] Run tests to identify failures
3. [ ] Fix breaking change #1: old_function → new_function
4. [ ] Fix breaking change #2: dict → ProcessResult
5. [ ] Fix breaking change #3: ...
6. [ ] Update deprecated calls (optional but recommended)
7. [ ] Run full test suite
8. [ ] Manual testing of affected features

## Verification Commands

```bash
# Update dependency
pip install package==2.0

# Run tests
pytest

# Check for remaining deprecated usage
grep -r "old_function\|legacy_api" src/
```
```

## Common Migrations

### Python Version Upgrade
```markdown
## Python 3.9 → 3.12

### Syntax Changes
- `dict | dict` union syntax (3.9+)
- `match` statement (3.10+)
- `type` statement for type aliases (3.12+)

### Removed
- `asyncio.coroutine` decorator (use `async def`)
- `collections.` ABCs (use `collections.abc.`)

### New Features
- `tomllib` built-in (3.11+)
- Improved error messages
- Faster startup
```

### Dependency Upgrade Checklist
```markdown
1. [ ] Read changelog/release notes
2. [ ] Check for breaking changes
3. [ ] Update version constraint
4. [ ] Run tests
5. [ ] Fix failures
6. [ ] Update deprecated usage
7. [ ] Test manually
8. [ ] Commit with clear message
```

## Instructions for Claude

When /migrate is invoked:

1. **Identify migration type** - Dependency, language, framework
2. **Research changes** - Read changelogs, migration guides
3. **Find breaking changes** - API removals, signature changes
4. **Search codebase** - Find usage of affected APIs
5. **Generate plan** - Step-by-step migration
6. **Apply changes** - Update code with new patterns
7. **Verify** - Run tests after each step
8. **Document** - Note any gotchas for future reference
