# /pre-release - Pre-Release Checklist

Comprehensive checklist before tagging and releasing a new version.

## Usage
```
/pre-release patch       # Prepare patch release (1.0.0 → 1.0.1)
/pre-release minor       # Prepare minor release (1.0.0 → 1.1.0)
/pre-release major       # Prepare major release (1.0.0 → 2.0.0)
/pre-release 1.2.3       # Prepare specific version
```

## What This Skill Does

1. **Version Bump** - Update version in config files
2. **Run Tests** - Ensure all tests pass
3. **Update Changelog** - Add release notes
4. **Check Documentation** - README, API docs current
5. **Verify CI** - All checks passing
6. **Generate Checklist** - Pre-release verification

## Pre-Release Checklist

```markdown
# Pre-Release Checklist: v1.2.0

## Version Updates
- [ ] pyproject.toml version updated
- [ ] __version__ in __init__.py updated (if applicable)
- [ ] CHANGELOG.md updated with release date

## Quality Checks
- [ ] All tests passing (`pytest`)
- [ ] No lint errors (`ruff check .`)
- [ ] Type checks pass (`mypy`)
- [ ] Coverage meets threshold

## Documentation
- [ ] README.md is current
- [ ] CHANGELOG.md has this version's changes
- [ ] API documentation updated (if applicable)
- [ ] Migration guide written (if breaking changes)

## CI/CD
- [ ] All CI checks passing on main
- [ ] No pending dependabot PRs for security issues

## Git
- [ ] All changes committed
- [ ] Working directory clean
- [ ] On main/master branch
- [ ] Pulled latest changes

## Final Steps
- [ ] Create release commit: `git commit -m "chore: release v1.2.0"`
- [ ] Create tag: `git tag -a v1.2.0 -m "v1.2.0"`
- [ ] Push: `git push && git push --tags`

## Post-Release
- [ ] Verify GitHub release created
- [ ] Verify package published (PyPI/crates.io)
- [ ] Announce release (if applicable)
```

## Version Bump Locations

### Python (pyproject.toml)
```toml
[project]
version = "1.2.0"
```

### Python (__init__.py)
```python
__version__ = "1.2.0"
```

### Rust (Cargo.toml)
```toml
[package]
version = "1.2.0"
```

### Node (package.json)
```json
{
  "version": "1.2.0"
}
```

## Instructions for Claude

When /pre-release is invoked:

1. **Determine current version** - Read from config files
2. **Calculate new version** - Based on bump type
3. **Update version files** - All locations consistently
4. **Run tests** - Ensure passing
5. **Run lints** - Ensure clean
6. **Update CHANGELOG** - Use /changelog skill
7. **Generate checklist** - Customized for project
8. **Offer to commit** - Stage and commit changes
9. **Provide tag command** - Don't auto-tag, let user confirm
