---
name: release
description: Create a new version release with proper tagging and changelog. Handles version bumping, tagging, and GitHub release creation. Invoke with /release [patch|minor|major] or just /release for patch.
---

# Release Skill

Create properly versioned releases with tags and GitHub releases.

## Process

1. **Pre-flight checks**
   ```bash
   git status --short  # Must be clean
   git describe --tags --abbrev=0  # Get current version
   ```

2. **Determine version bump**
   - `patch` (default): Bug fixes, minor changes (1.2.3 → 1.2.4)
   - `minor`: New features, backwards compatible (1.2.3 → 1.3.0)
   - `major`: Breaking changes (1.2.3 → 2.0.0)

3. **Run tests**
   - Python: `pytest`
   - Rust: `cargo test`
   - Node: `npm test`

4. **Update version in manifest**
   - Python: `pyproject.toml` version field
   - Rust: `Cargo.toml` version field
   - Node: `package.json` version field

5. **Commit version bump**
   ```bash
   git add pyproject.toml  # or Cargo.toml, package.json
   git commit -m "Bump version to X.Y.Z"
   ```

6. **Create annotated tag**
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z - Brief description"
   ```

7. **Push with tags**
   ```bash
   git push && git push origin vX.Y.Z
   ```

8. **Create GitHub release**
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z - Title" --notes "$(cat <<'EOF'
   ## What's New
   - Feature 1
   - Feature 2

   ## Bug Fixes
   - Fix 1

   ## Full Changelog
   https://github.com/AreteDriver/REPO/compare/vPREV...vX.Y.Z
   EOF
   )"
   ```

## Changelog Generation

Review commits since last tag:
```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

Group by type:
- **Features**: `feat:` commits
- **Bug Fixes**: `fix:` commits
- **Other**: everything else worth mentioning

## Version Locations

| Project Type | File | Field |
|--------------|------|-------|
| Python | `pyproject.toml` | `version = "X.Y.Z"` |
| Rust | `Cargo.toml` | `version = "X.Y.Z"` |
| Node | `package.json` | `"version": "X.Y.Z"` |

## Rules

- Never release with failing tests
- Never release with uncommitted changes
- Always use annotated tags (`-a`), not lightweight
- Include changelog in GitHub release notes
- Use semantic versioning strictly
