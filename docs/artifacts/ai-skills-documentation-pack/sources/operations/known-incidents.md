---
title: AI Skills Known Incidents and Defects
source_id: SRC-AIS-OPS-001
status: active
authority: high
owner: Engineering
date_created: 2026-06-18
date_collected: 2026-06-18
current: true
sensitive: false
related_documents:
  - plans/prioritized-backlog.md
---

# Known Incidents and Defects

## Severity Definitions

- **P0:** Breaks documented core behavior or corrupts source-of-truth integrity.
- **P1:** Significant reliability, safety, or maintainability defect.
- **P2:** Product maturity or usability gap.
- **P3:** Polish or optimization.

## Incident Register

| ID | Severity | Area | Confirmed Problem | Evidence | Required Resolution |
|---|---|---|---|---|---|
| AIS-INC-001 | P0 | Catalog | README and `CLAUDE.md` state 70 skills; registry stats state 87; registry entries calculate to 91 | README, CLAUDE, registry | Generate all counts |
| AIS-INC-002 | P0 | Registry | Registry category statistics are wrong: security and domain counts are stale | `registry.yaml` entries vs `stats` | Remove stored stats or validate generated values |
| AIS-INC-003 | P0 | Installer | `bundles.yaml` defines 14 bundles but installer accepts 10 | `bundles.yaml`, `install.sh` | Parse bundle YAML at runtime |
| AIS-INC-004 | P0 | Installer / Docs | README advertises `arete-studio-ops`; installer does not recognize it | README quickstart, installer `BUNDLE_NAMES` | Eliminate duplicated bundle list |
| AIS-INC-005 | P0 | Bundle integrity | `content-ops` defines 8 skills in YAML but installer hard-codes 4 | `bundles.yaml`, `install.sh` | Contract test exact bundle contents |
| AIS-INC-006 | P1 | Hooks | Bundle hook declarations are validated but bundle installation code installs only skills | `bundles.yaml`, `install.sh` bundle branch | Add explicit `--with-hooks` behavior |
| AIS-INC-007 | P0 | Registry completeness | At least 12 indexed skills are absent from registry | GitHub indexed paths vs registry | Register, deprecate, or move to experimental |
| AIS-INC-008 | P1 | Agent schema metadata | Registry marks several analysis agents `has_schema: false`; schema files are indexed and fetchable | Registry and agent schema files | Generate schema flags |
| AIS-INC-009 | P0 | Contract vocabulary | Agent risk and consensus enums conflict across `CLAUDE.md`, registry, and v2 template | Three source files | Adopt one canonical model |
| AIS-INC-010 | P1 | Contributor DX | `CLAUDE.md` instructs authors to copy missing `agent-template.md` and `workflow-template.md` | 404 for both paths | Add templates and tests |
| AIS-INC-011 | P1 | CI enforcement | Missing schemas and orphan skills are warnings; Python warning counts do not affect shell summary | Validator implementation | Strict mode and zero-warning stable lane |
| AIS-INC-012 | P1 | Format checks | Script header claims line-length and indentation checks that are not implemented | `format-check.sh` | Implement or remove claims |
| AIS-INC-013 | P1 | Release history | Changelog stops at 1.0.0 while the repository contains many later additions | `CHANGELOG.md`, current tree | Release governance and generated notes |
| AIS-INC-014 | P1 | Uninstall safety | Global uninstall behavior is not tied to an install manifest | Installer design | Track installed ownership; remove only managed assets |
| AIS-INC-015 | P1 | Name collision | Destination uses directory basename only; same skill name across types/categories can overwrite | `install_skill()` | Enforce global unique IDs or namespaced install paths |
| AIS-INC-016 | P1 | Behavioral quality | CI proves syntax, not actual skill effectiveness | CI workflow | Add executable eval harness |
| AIS-INC-017 | P1 | Trust boundary | Executable hooks are distributed alongside prompt content without a formal approval model | Repository structure | Separate permission class and explicit consent |
| AIS-INC-018 | P2 | Framework portability | Core validator enforces OpenClaw metadata on all skills | Validator | Move compatibility fields to adapters |
| AIS-INC-019 | P2 | Documentation | Architecture tables omit newer workflows and skills | README, CLAUDE | Generate catalog reference |
| AIS-INC-020 | P2 | Versioning | Many skills lack a consistently enforced version and lifecycle status | v1/v2 mixed formats | Manifest v2 migration |

## Immediate Release Blockers

A stable release should not be cut until AIS-INC-001 through AIS-INC-011 are resolved or explicitly waived in an ADR.
