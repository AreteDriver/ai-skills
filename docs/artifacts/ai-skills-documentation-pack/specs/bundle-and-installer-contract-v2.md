# Bundle and Installer Contract v2

## Bundle Contract

Each bundle is a standalone YAML document or validated entry.

```yaml
schema_version: "2.0"
id: "webapp-security"
version: "2.0.0"
lifecycle: "stable"
description: "Secure web application development and review."
audience: "Teams shipping production web applications"

skills:
  - id: "persona/engineering/code-reviewer"
    version: "^2.0"
  - id: "persona/security/security-auditor"
    version: "^2.0"
  - id: "persona/engineering/testing-specialist"
    version: "^2.0"
  - id: "persona/security/accessibility-checker"
    version: "^2.0"

hooks:
  - id: "hook/tdd-guard"
    version: "^1.0"
    optional: true
  - id: "hook/protected-paths"
    version: "^1.0"
    optional: true

compatibility:
  adapters: [claude-code]

constraints:
  conflicts: []
```

## Installer Contract

### Resolution

The installer must consume bundle YAML and the generated registry. It must not contain a second bundle table.

### Mutating Command Requirements

All mutating commands support:

- `--dry-run`
- `--json`
- `--yes` for non-interactive approved operations
- `--target`
- `--with-hooks`
- `--version`
- `--force` only for explicitly documented cases

### Transaction Semantics

1. Validate request.
2. Resolve exact versions.
3. Detect conflicts.
4. Calculate permission union.
5. Preview changes.
6. Obtain approval.
7. Stage in a temporary directory.
8. Verify content and digests.
9. Back up owned prior versions.
10. Atomically activate.
11. Write manifest and lockfile.
12. Run verification.
13. Roll back on failure.

### Ownership

The installer may delete only paths recorded in its install manifest and still matching an expected identity.

### Collision Policy

If a target exists and is not project-owned:

- stop;
- show the path;
- offer a namespaced target or explicit migration;
- never silently remove it.

### Hook Policy

- excluded by default;
- displayed separately;
- include lifecycle event and command preview;
- require explicit consent;
- verified executable and checksum;
- removable independently.

### Uninstall

`uninstall all` means all assets owned by the AI Skills manifest, not all files in the destination.

### Idempotency

Repeated installation of the same versions and digests is a no-op.

## Recommended Implementation

Build a Python CLI under `src/ai_skills/` with a minimal shell bootstrap if desired. The repository already relies on Python and YAML parsing; keeping bundle resolution in Bash increases duplication and test complexity.

## Required Contract Tests

- every defined bundle resolves;
- exact installed skill set equals the YAML;
- optional hooks are absent by default;
- advertised README commands succeed;
- bundle permissions are the union of contents;
- unresolved dependencies fail before writes;
- rollback leaves prior state intact;
- uninstall preserves unknown files;
- project lockfile reproduces installation.
