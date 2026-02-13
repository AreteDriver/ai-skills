---
name: release-engineer
description: Automates the last mile of shipping software — verifies release readiness, generates changelogs, tags versions, and pushes releases. Complements technical-debt-auditor (finds problems) by shipping fixes. Use when preparing a repo for public release, tagging a version, publishing to PyPI/npm, or when the user says "ship it". Designed to close the planning-vs-execution gap.
---

# Release Engineer

Automate the last mile. This skill takes a repo from "it works on my machine" to
"it's tagged, documented, and published."

## When to Activate

- "Ship it" / "release this" / "make this public"
- "Tag a new version"
- "Publish to PyPI / npm"
- "Prepare this for release"
- "Make this portfolio-ready"
- After a technical-debt-auditor run resolves critical/high items

## Philosophy

Shipping is a skill, not an event. Most solo developers lose momentum in the
gap between "code works" and "code is released." This skill eliminates that gap
by making release a repeatable, automated pipeline.

## Operating Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| **Preflight** | `release preflight` | Checks readiness without changing anything |
| **Ship** | `release ship [version]` | Full release pipeline |
| **Hotfix** | `release hotfix` | Patch release from current state |
| **Portfolio** | `release portfolio` | Preflight all career repos, report which are shippable |

## Preflight Checklist

Before any release, verify ALL of the following:

### Gate 1: Code Health
```bash
# Tests pass
pytest -v 2>&1 || npm test 2>&1 || cargo test 2>&1

# No uncommitted changes
git status --porcelain  # Must be empty

# On main/master branch
git branch --show-current  # Must be main or master

# Up to date with remote
git fetch origin && git diff HEAD origin/main --stat
```

### Gate 2: Documentation
```bash
# README exists and is non-trivial
[ -f README.md ] && [ $(wc -l < README.md) -gt 10 ]

# LICENSE exists
[ -f LICENSE ] || [ -f LICENSE.md ]

# Install instructions present
grep -qi "install\|setup\|getting started" README.md

# Usage example present
grep -qi "usage\|example\|quickstart" README.md
```

### Gate 3: Metadata
```bash
# Version is set somewhere
grep -r "version" pyproject.toml setup.py setup.cfg package.json Cargo.toml 2>/dev/null | head -5

# Description exists
grep -r "description" pyproject.toml package.json Cargo.toml 2>/dev/null | head -3

# Author/maintainer set
grep -r "author\|maintainer" pyproject.toml package.json Cargo.toml 2>/dev/null | head -3
```

### Gate 4: Security
```bash
# No secrets in tracked files
git ls-files | grep -iE "\.env$" | grep -v ".env.example"

# Quick secret scan
grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "(api_key|secret|password|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]" . 2>/dev/null
```

### Gate 5: CI (if configured)
```bash
# GitHub Actions passing (check via API or badge)
gh run list --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null
```

### Preflight Report

```
RELEASE PREFLIGHT — {repo_name}
═══════════════════════════════

  ✅ Code Health     Tests pass (30/30), clean working tree, on main
  ✅ Documentation   README (85 lines), LICENSE (MIT), install + usage present
  ⚠️  Metadata       Version set (0.2.0) but no CHANGELOG
  ✅ Security        No secrets detected
  ❌ CI              GitHub Actions failing (test_edge_case)

  Verdict: NOT READY — fix CI before release
  Blockers: 1 (CI failure)
  Warnings: 1 (no CHANGELOG)
```

## Ship Pipeline

Once preflight passes (or user overrides warnings):

### Step 1: Version Bump

```bash
# Detect current version
current=$(grep -oP 'version\s*=\s*"\K[^"]+' pyproject.toml 2>/dev/null || \
          node -p "require('./package.json').version" 2>/dev/null || \
          grep -oP 'version\s*=\s*"\K[^"]+' Cargo.toml 2>/dev/null)

echo "Current version: $current"
# Prompt user: major, minor, or patch bump?
```

Versioning follows semver:
- **patch** (0.2.0 → 0.2.1): Bug fixes, no new features
- **minor** (0.2.0 → 0.3.0): New features, backward compatible
- **major** (0.2.0 → 1.0.0): Breaking changes or first stable release

### Step 2: Generate CHANGELOG Entry

Scan git log since last tag:

```bash
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$last_tag" ]; then
    git log ${last_tag}..HEAD --oneline --no-merges
else
    git log --oneline --no-merges | head -20
fi
```

Categorize commits into:
- **Added** — new features
- **Changed** — modifications to existing features
- **Fixed** — bug fixes
- **Removed** — removed features
- **Security** — vulnerability fixes

Write or prepend to CHANGELOG.md:

```markdown
## [{new_version}] - {date}

### Added
- Timeline reconstruction module for forensic document analysis
- Entity co-occurrence scoring in NER pipeline

### Fixed
- Sentence splitter now handles abbreviations (Dr., Mr.) correctly

### Changed
- Upgraded FastAPI from 0.100 to 0.115
```

### Step 3: Commit Version + Changelog

```bash
git add -A
git commit -m "release: v{new_version}"
```

### Step 4: Tag

```bash
git tag -a "v{new_version}" -m "Release v{new_version}"
```

### Step 5: Push

```bash
git push origin main
git push origin "v{new_version}"
```

### Step 6: Publish (if applicable)

**Python (PyPI):**
```bash
python -m build
twine upload dist/*
```

**Node (npm):**
```bash
npm publish
```

**Rust (crates.io):**
```bash
cargo publish
```

### Step 7: GitHub Release (optional)

```bash
gh release create "v{new_version}" \
  --title "v{new_version}" \
  --notes-file CHANGELOG_ENTRY.md
```

## Portfolio Mode

Runs preflight across all career-relevant repos and produces a shipping status:

```
PORTFOLIO RELEASE STATUS
════════════════════════

  ✅ SHIPPABLE
     SteamProtonHelper (v1.3.2) — all gates pass
     DOSSIER (v0.1.0) — ready for initial release

  ⚠️  ALMOST READY (1-2 fixes needed)
     Gorgon (v0.3.0) — CI failing, fix 1 test
     Convergent (v0.1.0) — no LICENSE file

  ❌ NOT READY
     EVE_Rebellion — no tests, README is boilerplate

  Quick wins to unblock 2 more releases:
  1. Add LICENSE to Convergent (2 min)
  2. Fix test_edge_case in Gorgon (15 min)
```

## Gorgon Workflow Integration

```yaml
workflow:
  name: release_pipeline
  agents:
    - role: preflight_checker
      task: "Run all 5 preflight gates"
      output: preflight-report.json

    - role: changelog_generator
      task: "Parse git log, categorize commits, generate CHANGELOG entry"
      depends_on: [preflight_checker]
      condition: "preflight passes or user overrides"
      output: CHANGELOG_ENTRY.md

    - role: version_bumper
      task: "Bump version in project config files"
      depends_on: [changelog_generator]
      output: version-bump.json

    - role: publisher
      task: "Commit, tag, push, publish"
      depends_on: [version_bumper]
      output: release-result.json

  gates:
    - after: preflight_checker
      condition: "any gate FAILED"
      action: pause
      message: "Preflight failed. Fix blockers or override to continue."
```

## Constraints

- **Never force-push** — always regular push
- **Never publish without user confirmation** — pause before `twine upload` / `npm publish`
- **Never skip tests** — if tests fail, release is blocked (user can override)
- **Always generate CHANGELOG** — even if user didn't ask for one
- **Respect .gitignore** — never commit build artifacts
- **Idempotent** — running preflight twice produces same result
