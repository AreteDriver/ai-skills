---
title: AI Skills Repository Inventory
source_id: SRC-AIS-REPO-001
status: under-review
authority: high
owner: Engineering
date_created: 2026-06-18
date_collected: 2026-06-18
current: true
sensitive: false
related_documents:
  - sources/repository/directory-tree.md
  - sources/technical/existing-architecture.md
---

# Repository Inventory

## Repository

- Repository name: `ai-skills`
- Repository URL: `github.com/AreteDriver/ai-skills`
- Default branch: `main`
- Primary formats: Markdown, YAML, Bash, Python
- Runtime model: content library plus local installer and validation tooling
- Package manager: none governing the whole repository
- Deployment target: `~/.claude/skills`, `~/.claude/hooks`, compatible agent runtimes
- License: MIT
- Maintainer: AreteDriver

## Major Components

| Component | Path | Purpose | Status |
|---|---|---|---|
| Persona skills | `personas/` | Behavior and domain specialization | Active; registry drift present |
| Agent skills | `agents/` | Typed capability contracts | Active; schema metadata drift present |
| Workflows | `workflows/` | Multi-step orchestration | Active; README omits newer workflows |
| Bundles | `bundles.yaml` | Curated installation sets | Active; installer does not consume this source |
| Registry | `registry.yaml` | Central catalog | Active; internally and externally inconsistent |
| Installer | `tools/install.sh` | Copy/symlink skills and hooks | Active; duplicated bundle catalog |
| Validators | `tools/validate-skills.sh`, `tools/format-check.sh` | Structural quality checks | Active; incomplete enforcement |
| Hooks | `hooks/` | Claude Code lifecycle controls | Active; executable code, elevated trust |
| Plugins | `plugins/` | Bundled examples | Active / lightly documented |
| Templates | `templates/` | Authoring scaffolds | Active; contributor guide references missing files |
| Legacy prompts | `prompts/` | Older standalone prompt artifacts | Legacy |
| Intelligence notes | `intel/` | External pattern research | Research / non-runtime |
| Documentation | `docs/` | Executive and historical material | Partial; no canonical documentation spine |

## Registry-Derived Inventory

The entries currently present in `registry.yaml` calculate to:

| Type | Registry Entries |
|---|---:|
| Personas | 66 |
| Agents | 17 |
| Workflows | 8 |
| **Total** | **91** |

The registry's stored statistics say 62 personas and 87 total. Those values are stale.

## Observed Unregistered Skill Directories

Indexed repository paths show at least the following `SKILL.md` directories absent from `registry.yaml`:

- `personas/devops/ci`
- `personas/devops/deps`
- `personas/devops/lint`
- `personas/devops/logs`
- `personas/devops/package`
- `personas/devops/postmortem`
- `personas/devops/pr`
- `personas/engineering/e2e`
- `personas/engineering/readme`
- `personas/engineering/scaffold`
- `personas/domain/g13-layout`
- `personas/domain/ogma`

This is a minimum observed set, not a complete filesystem count.

## Entry Points

| Entry Point | Path | Purpose |
|---|---|---|
| User documentation | `README.md` | Discover and install skills |
| AI contributor context | `CLAUDE.md` | Repository conventions |
| Catalog | `registry.yaml` | Discover skills |
| Bundle catalog | `bundles.yaml` | Define curated sets |
| Installer | `tools/install.sh` | Install, list, uninstall |
| Structural validation | `tools/validate-skills.sh` | Validate files and references |
| Format validation | `tools/format-check.sh` | Check YAML, Markdown, shell |
| CI | `.github/workflows/validate-skills.yml` | Execute local checks on push/PR |

## Dependencies

| Dependency | Declared / Implied | Purpose | Risk |
|---|---|---|---|
| Bash | Required | Installer and validators | Cross-platform behavior |
| Python 3 | Required in CI and validator helpers | YAML parsing and metadata tooling | Version not pinned locally |
| PyYAML | Installed in CI | YAML parsing | Unpinned dependency |
| GitHub Actions | Required for CI | Validation | Actions pinned by mutable major tags |
| Claude Code | Primary target | Skill runtime | Compatibility not version-tested |
| Optional Docker | Referenced by advanced skills | Sandboxed execution | Not a repository-wide dependency |

## Tests and Quality Gates

| Gate | Command | Current Status | Limitation |
|---|---|---|---|
| Structural validator | `./tools/validate-skills.sh` | Present | Many violations are warnings |
| Format checker | `./tools/format-check.sh` | Present | Claims checks not implemented |
| CI | GitHub Actions workflow | Present | Runs only the two scripts |
| Installer tests | None found | Missing | No temp-home integration matrix |
| Behavioral skill evals | No canonical harness found | Missing | Golden examples are not executable tests |
| Security tests | Partial content-level guidance | Missing as gate | Hooks and prompt injection not tested |
| Docs drift check | None found | Missing | Counts and catalogs drift manually |

## Repository Truth Summary

### Current Behavior

The repository installs discovered skill directories and a hard-coded subset of bundles. Validation confirms basic file presence and YAML parseability but permits substantial contract drift.

### Intended Behavior

The repository presents itself as a production-ready, portable skill library with a central registry, typed interfaces, curated bundles, and CI-backed reliability.

### Gaps

The central metadata graph is manually duplicated. Runtime behavior, catalogs, and documentation can diverge without CI failure.

### Immediate Risks

- Users invoke documented bundle commands that fail.
- Bundles install different contents than their YAML definitions.
- Registry consumers receive wrong counts and schema flags.
- Unregistered skills are installable through search but undiscoverable through the catalog.
- Executable hooks can be distributed without a formal permission and review model.
