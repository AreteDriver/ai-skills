# Installation, Operations, and Support

## Current Operational Problem

The installer has its own hard-coded bundle catalog. `bundles.yaml` is not the source used to install bundles. This is the most important functional defect in the repository.

## Target Installation Flow

```text
Resolve request
→ load generated registry
→ load bundle
→ verify versions and compatibility
→ calculate permission union
→ display plan
→ acquire lock
→ stage files
→ verify digests
→ back up managed conflicts
→ atomically activate
→ write install manifest
→ run health check
```

## Safe Defaults

- `--dry-run` available for every mutating command;
- hooks excluded unless `--with-hooks`;
- no overwrite of unowned files;
- no delete outside the managed manifest;
- no implicit network access after package acquisition;
- exact versions pinned in project mode;
- target path normalized and validated;
- install interrupted safely and recoverably.

## Install Manifest

Example:

```json
{
  "schema_version": "1",
  "installed_at": "2026-06-18T00:00:00Z",
  "source_release": "v2.0.0",
  "target": "~/.claude",
  "artifacts": [
    {
      "id": "persona/engineering/code-reviewer",
      "version": "2.1.0",
      "path": "skills/code-reviewer",
      "digest": "sha256:...",
      "mode": "copy"
    }
  ],
  "hooks": [],
  "bundle": "webapp-security"
}
```

## Operational Commands

```text
ai-skills doctor
ai-skills verify
ai-skills list --installed
ai-skills diff --installed
ai-skills update --dry-run
ai-skills rollback
ai-skills uninstall <id|bundle>
```

## Doctor Checks

- supported runtime found;
- destination writable;
- no unmanaged collisions;
- registry signature valid;
- installed digests match;
- hooks executable and approved;
- adapter compatible;
- lockfile consistent.

## Support Triage

Collect:

- OS and runtime version;
- CLI version;
- command;
- bundle or skill ID;
- dry-run output;
- doctor output;
- install manifest with sensitive paths redacted;
- whether hooks were enabled;
- relevant logs.

Never request credentials, tokens, or entire private repositories.

## Deprecation

A deprecated skill remains installable for a defined window but:

- emits a warning;
- names the replacement;
- includes migration guidance;
- cannot enter new stable bundles;
- is removed only in a major release.
