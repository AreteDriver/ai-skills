# Source Register

## Purpose

This is the canonical index of evidence used to create the AI Skills documentation and remediation plan.

## Source Catalog

| ID | Source | Category | Status | Authority | Date Collected | Used By | Notes |
|---|---|---|---|---|---|---|---|
| SRC-AIS-001 | GitHub repository metadata for `AreteDriver/ai-skills` | Repository | active | high | 2026-06-18 | All documents | Public repository, default branch `main`, MIT |
| SRC-AIS-002 | `README.md` | Product / Docs | active | medium | 2026-06-18 | Assessment, architecture, operations | User-facing claims; contains stale counts |
| SRC-AIS-003 | `registry.yaml` | Repository / Contract | active | high | 2026-06-18 | Inventory, architecture, migration | Intended central catalog; internally inconsistent |
| SRC-AIS-004 | `bundles.yaml` | Product / Distribution | active | high | 2026-06-18 | Installer spec, incidents | Defines fourteen bundle records |
| SRC-AIS-005 | `tools/install.sh` | Implementation | active | canonical-current | 2026-06-18 | Installer review, incidents | Current runtime installer behavior |
| SRC-AIS-006 | `tools/validate-skills.sh` | Quality | active | canonical-current | 2026-06-18 | Testing strategy, incidents | Structural validator; warnings do not reliably fail CI |
| SRC-AIS-007 | `tools/format-check.sh` | Quality | active | canonical-current | 2026-06-18 | Testing strategy, incidents | Formatting checks; documented checks exceed implementation |
| SRC-AIS-008 | `.github/workflows/validate-skills.yml` | CI | active | canonical-current | 2026-06-18 | CI assessment | Runs validation and format scripts |
| SRC-AIS-009 | `CLAUDE.md` | Contributor guidance | active | medium | 2026-06-18 | Authoring, incidents | Contains stale counts, missing-template references, enum conflicts |
| SRC-AIS-010 | `templates/skill-template-v2.md` | Contract design | active | high | 2026-06-18 | Skill contract v2 | Stronger proposed structure; not yet governing |
| SRC-AIS-011 | `CHANGELOG.md` | Release | active | medium | 2026-06-18 | Governance review | Last recorded release 2026-02-14; later additions unrecorded |
| SRC-AIS-012 | Indexed repository paths from GitHub code search | Repository | under-review | high | 2026-06-18 | Orphan analysis | Shows at least twelve skills absent from registry |
| SRC-AIS-013 | `docs/legacy/REPO_REVIEW.md` | Historical | historical | medium | 2026-06-18 | Progress comparison | Earlier 8.2/10 review before current expansion |
| SRC-AIS-014 | GitHub development project source-document standards | Governance | active | canonical | 2026-06-18 | Structure of this pack | Defines source/docs/specs/plans separation |
| SRC-AIS-015 | `agents/analysis/technical-debt-auditor/schema.yaml` | Contract example | active | high | 2026-06-18 | Schema assessment | Demonstrates mature v2 schema while registry says `has_schema: false` |
| SRC-AIS-016 | Missing `templates/agent-template.md` and `templates/workflow-template.md` | Repository | active | high | 2026-06-18 | Incident register | GitHub returned 404 for both paths referenced in `CLAUDE.md` |

## Authority Rules

- Current code determines current behavior.
- Approved contracts determine intended behavior after migration.
- Generated documentation must not override code or contracts.
- Manually maintained counts and catalogs are non-authoritative.
- Unresolved conflicts remain visible until a decision record closes them.

## Known Conflicts

| Conflict | Sources | Resolution Direction |
|---|---|---|
| Skill count: 70 vs 87 vs 91+ | SRC-AIS-002, 003, 009, 012 | Generate counts from validated manifests |
| Bundle count and contents differ | SRC-AIS-004, 005 | Installer must consume `bundles.yaml` |
| Agent risk vocabulary differs | SRC-AIS-003, 009, 010 | Adopt one canonical risk and approval model |
| Schema presence differs from registry metadata | SRC-AIS-003, 015 | Generate registry metadata from filesystem |
| Contributor templates referenced but absent | SRC-AIS-009, 016 | Add canonical templates and validation |
