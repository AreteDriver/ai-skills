---
name: release-engineering
description: End-to-end release workflow — preflight checks, code review, changelog generation, version bump, tagging, and publishing. Coordinates release-engineer agent, code-reviewer persona, and github-operations agent through the WHY/WHAT/HOW framework.
metadata: {"openclaw": {"emoji": "📋", "os": ["darwin", "linux", "win32"]}}
---

# Release Engineering Workflow

## Role

You orchestrate the complete release lifecycle — from verifying a repo is ready
to ship through tagging, changelog generation, and publishing. You coordinate
the release-engineer agent for preflight checks, the code-reviewer persona for
final review, and github-operations for the actual release.

This workflow closes the gap between "it works" and "it's shipped."

## Workflow Phases

```
Phase 0: Context Mapping     → Understand the project and release history
Phase 1: Preflight (WHY)     → Verify the repo is ready — tests, docs, security
Phase 2: Review (WHAT)       → Final code review of unreleased changes
Phase 3: Prepare (HOW)       → Version bump, changelog, commit
Phase 4: Publish             → Tag, push, create GitHub release
Phase 5: Verify              → Confirm release is live and correct
```

## Phase 0: Context Mapping

**Agent:** context-mapper
**Output:** release_context.yaml

Before any release work, map the project state:

```yaml
context_mapping:
  scan:
    - Project type (Python/Node/Rust/other)
    - Package manager and build system
    - Current version and version location(s)
    - Last release tag and commits since then
    - CI/CD configuration and status
    - Existing CHANGELOG format (if any)
  identify:
    - Version files to update (pyproject.toml, package.json, Cargo.toml, etc.)
    - Test command (pytest, npm test, cargo test, etc.)
    - Build command (if applicable)
    - Publish target (PyPI, npm, crates.io, GitHub Releases only)
    - Branch protection rules
```

## Phase 1: Preflight (WHY)

**Agent:** release-engineer (preflight mode)
**Output:** preflight_report.yaml

Verify every gate before proceeding:

```yaml
why:
  goal: "Ship a reliable release that won't break users"
  motivation: "Close the gap between working code and published software"

  preflight_gates:
    code_health:
      tests_pass: required
      clean_working_tree: required
      on_release_branch: required  # main/master or release/*
      up_to_date_with_remote: required

    documentation:
      readme_exists: required
      readme_nontrivial: required  # >10 lines
      license_exists: required
      install_instructions: required
      usage_examples: recommended

    metadata:
      version_set: required
      description_set: recommended
      author_set: recommended

    security:
      no_secrets_in_tracked_files: required
      no_hardcoded_credentials: required
      dependencies_audited: recommended

    ci:
      latest_run_passing: required  # if CI is configured

  success_criteria:
    - "All required gates pass"
    - "User has reviewed and acknowledged any warnings"
    - "Version bump strategy is agreed upon (major/minor/patch)"

  anti_goals:
    - "Don't release with failing tests"
    - "Don't skip changelog even if user asks — it's always generated"
    - "Don't force-push or bypass branch protection"
```

### Preflight Report Format

```
RELEASE PREFLIGHT — {repo_name}
═══════════════════════════════

  ✅ Code Health     Tests pass (42/42), clean tree, on main, up to date
  ✅ Documentation   README (120 lines), LICENSE (MIT), install + usage present
  ⚠️  Metadata       Version set (0.3.0) but description missing in pyproject.toml
  ✅ Security        No secrets detected, deps clean
  ✅ CI              GitHub Actions passing (run #87)

  Verdict: READY (1 warning)
  Warnings: description missing in pyproject.toml
  Commits since last release: 14
  Suggested version: 0.4.0 (minor — new features, no breaking changes)
```

## Phase 2: Review (WHAT)

**Agent:** code-reviewer persona
**Output:** release_review.md

Review all changes since the last release tag:

```yaml
what:
  scope: "All commits between last tag and HEAD"
  review_focus:
    - Breaking changes that affect semver decision
    - Security issues introduced since last release
    - API surface changes (new exports, removed functions, changed signatures)
    - Documentation accuracy (do docs match current behavior?)

  files_in_scope:
    - "git diff {last_tag}..HEAD --name-only"

  deliverable:
    format: "review_report (per code-reviewer schema)"
    additional_fields:
      breaking_changes: "List of breaking changes with migration steps"
      api_surface_delta: "Added, changed, and removed public API items"
      semver_recommendation: "major | minor | patch with rationale"
```

## Phase 3: Prepare (HOW)

**Agent:** release-engineer (ship mode)
**Output:** Release commit with version bump + changelog

```yaml
how:
  strategy: "atomic release commit"

  steps:
    - step: 1
      action: "Determine version bump"
      details: |
        Based on Phase 2 review:
        - Breaking changes → major
        - New features, backward compatible → minor
        - Bug fixes only → patch
        User confirms or overrides.
      acceptance:
        - "Version strategy agreed with user"

    - step: 2
      action: "Generate CHANGELOG entry"
      details: |
        Parse git log since last tag. Categorize:
        - Added: new features
        - Changed: modifications to existing features
        - Fixed: bug fixes
        - Removed: removed features
        - Security: vulnerability fixes
        Format: Keep-a-Changelog (https://keepachangelog.com)
      acceptance:
        - "CHANGELOG entry covers all commits"
        - "Categories are correct"

    - step: 3
      action: "Bump version in project files"
      details: |
        Update version in all detected locations:
        - pyproject.toml / setup.py / setup.cfg
        - package.json / package-lock.json
        - Cargo.toml
        - __version__ in __init__.py
        Ensure all locations agree.
      acceptance:
        - "All version references updated consistently"

    - step: 4
      action: "Create release commit"
      details: |
        git add -A
        git commit -m "release: v{new_version}"
      acceptance:
        - "Commit contains only version bump + changelog"
        - "Commit message follows conventional format"

  quality_gates:
    - name: "Tests still pass after version bump"
      after_step: 3
      check: "{detected_test_command}"
      on_failure: block

    - name: "Build succeeds"
      after_step: 3
      check: "{detected_build_command}"
      on_failure: block
```

## Phase 4: Publish

**Agent:** github-operations + release-engineer
**Output:** Git tag, pushed release, package published

```yaml
publish:
  steps:
    - step: 1
      action: "Create annotated tag"
      command: 'git tag -a "v{version}" -m "Release v{version}"'
      risk: low

    - step: 2
      action: "Push commit and tag"
      command: |
        git push origin {branch}
        git push origin "v{version}"
      risk: medium
      consensus: required  # User must confirm before push

    - step: 3
      action: "Create GitHub Release"
      command: |
        gh release create "v{version}" \
          --title "v{version}" \
          --notes-file CHANGELOG_ENTRY.md
      risk: medium
      consensus: required

    - step: 4
      action: "Publish to package registry (if applicable)"
      details: |
        Python: python -m build && twine upload dist/*
        Node: npm publish
        Rust: cargo publish
      risk: high
      consensus: required  # Always pause before publishing
```

## Phase 5: Verify

**Agent:** release-engineer (verification mode)
**Output:** verification_report.yaml

```yaml
verification:
  checks:
    - "Tag exists on remote: git ls-remote --tags origin v{version}"
    - "GitHub Release is visible and has correct notes"
    - "Package is available on registry (if published)"
    - "README badges reflect new version (if applicable)"
    - "CI ran on the tagged commit and passed"

  report_format: |
    RELEASE VERIFICATION — v{version}
    ═══════════════════════════════════

      ✅ Tag pushed          v{version} exists on origin
      ✅ GitHub Release       Created with changelog
      ✅ Package published    {package_name} v{version} on {registry}
      ✅ CI passing           Run #{run_id} on tag

      Release complete.
```

## Orchestration

```
Supervisor
├── Phase 0: context-mapper agent
│   └── Output: release_context.yaml
├── Phase 1: release-engineer agent (preflight)
│   └── Output: preflight_report.yaml
│   └── Gate: All required checks pass
├── Phase 2: code-reviewer persona
│   └── Output: release_review.md
│   └── Gate: No critical findings
├── Phase 3: release-engineer agent (prepare)
│   ├── Step 1: Version strategy (user input)
│   ├── Step 2: Generate CHANGELOG
│   ├── Step 3: Bump version
│   ├── Step 4: Release commit
│   └── Gate: Tests + build pass
├── Phase 4: github-operations agent (publish)
│   ├── Step 1: Create tag
│   ├── Step 2: Push (user confirms)
│   ├── Step 3: GitHub Release (user confirms)
│   └── Step 4: Package publish (user confirms)
└── Phase 5: release-engineer agent (verify)
    └── Output: verification_report.yaml
```

## Constraints

- Never skip preflight — shipping broken releases erodes trust
- Phase 2 review is scoped to changes since last tag, not the entire repo
- Version strategy must be confirmed with the user
- All Phase 4 publish steps require explicit user confirmation
- Never force-push — always regular push
- Never publish without tests passing
- Always generate CHANGELOG even if the user didn't ask
- Idempotent — running preflight twice produces the same result
- If any phase fails, stop and report — don't continue silently
