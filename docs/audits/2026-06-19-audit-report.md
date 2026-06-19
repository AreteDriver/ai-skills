# AI Skills Repository Audit Report

**Date:** 2026-06-19
**Commit:** f7528ea34f7a5c68c0886e6d7d698055d2283b99
**Auditor:** Claude Code + Documentation Pack Review

---

## Summary

The `ai-skills` repository has significant **control-plane drift**. The filesystem contains substantially more skills than the registry acknowledges, the installer hard-codes fewer bundles than `bundles.yaml` defines, and schema flags are inconsistently set. The content itself is strong; the metadata layer is unreliable.

---

## Findings

### 1. Persona Registry Drift (48 orphans)

| Category | Registry Claims | Filesystem | Orphans |
|----------|---------------|------------|---------|
| engineering | 8 | 33 | 25 |
| devops | 6 | 22 | 16 |
| claude-code | 7 | 9 | 2 |
| domain | 18 | 22 | 4 |
| web | 16 | 20 | 4 |
| data | 4 | 4 | 0 |
| api | 4 | 4 | 0 |
| security | 3 | 3 | 0 |
| **Total** | **66** | **117** | **51** |

*(Note: 117 leaf directories in personas/ vs 114 earlier — recount shows 3 extra)*

All orphan personas have valid `SKILL.md` files with substantial content (1.7KB–14KB). They are legitimate skills omitted from the registry.

### 2. Agent Registry Match (perfect)

Registry claims 17 agents. Filesystem has 17 agents. Perfect alignment.

However, **7 agents have `schema.yaml` files but `has_schema: false`** in registry:
- `analysis/context-mapper`
- `analysis/document-forensics`
- `analysis/entity-resolver`
- `analysis/intent-author`
- `analysis/release-engineer`
- `analysis/technical-debt-auditor`
- `analysis/workflow-debugger`

### 3. Workflow Registry Drift (6 orphans + 1 mismatch)

| Registry | Filesystem | Status |
|----------|------------|--------|
| 8 workflows | 13 workflows | 5 orphans + 1 renamed |

Orphans (on disk, not in registry):
- `context-mapping` (9512 bytes)
- `evaluation` (3284 bytes)
- `exploration` (2528 bytes)
- `goal` (2814 bytes)
- `production` (3796 bytes)
- `specification` (3100 bytes)

Missing from disk but in registry:
- `context-mapper` — possibly renamed to `context-mapping`

### 4. Installer Hard-Coding (4 bundles missing)

`bundles.yaml` defines **14 bundles**. Installer hard-codes **10 bundles**.

Missing from installer:
| Bundle | `bundles.yaml` Skills | Installer Status |
|--------|----------------------|------------------|
| `project-orchestration` | 6 skills | **Not implemented** |
| `eve-frontier` | 4 skills | **Not implemented** |
| `session-management` | 3 skills | **Not implemented** |
| `arete-studio-ops` | 7 skills | **Not implemented** |

Additionally, `content-ops` bundle in installer has **4 skills** vs `bundles.yaml`'s **8 skills** — missing:
- `personas/web/seo-content-pipeline`
- `personas/web/brand-voice-architect`
- `personas/web/cro-analyst`
- `personas/web/headline-hook-generator`

README documents `./tools/install.sh --bundle arete-studio-ops` but the installer rejects it.

### 5. Schema Flag Inconsistencies (12 personas)

12 personas have `schema.yaml` or `schema/` files but are not flagged with `has_schema: true`:

**Personas:**
- `engineering/senior-software-engineer`
- `engineering/software-architect`
- `engineering/code-reviewer`
- `engineering/testing-specialist`
- `security/security-auditor`

### 6. Template Audit (false positive from review)

All three templates referenced in `CLAUDE.md` exist:
- `templates/skill-template.md` ✓
- `templates/agent-template.md` ✓
- `templates/workflow-template.md` ✓

The documentation pack flagged these as missing based on GitHub code-search 404s, but local verification confirms presence.

### 7. Skills Directory Empty

`skills/` directory exists but is empty. `README.md` claims "114 skills" in the personas column — this appears to count personas as skills, which is a taxonomy inconsistency.

---

## Recommended Phase 0 Actions

1. **Reconcile registry.yaml** — add all 51 orphan personas, 6 orphan workflows, fix `context-mapper`→`context-mapping`
2. **Fix schema flags** — set `has_schema: true` for 7 agents + 5 personas with actual schema files
3. **Repair installer** — replace hard-coded bundle table with `bundles.yaml` parser; add 4 missing bundles; fix `content-ops`
4. **Add strict validation** — CI should fail if registry doesn't match filesystem
5. **Document `skills/`** — either populate, remove, or clarify that "skills" in README counts personas+agents+workflows

---

## Score Impact

| Dimension | Current | After Phase 0 |
|-----------|---------|---------------|
| Documentation accuracy | 4.5 | 7.0 |
| Installer reliability | 4.0 | 7.0 |
| Contract consistency | 4.5 | 7.0 |
| **Projected maturity** | **6.7** | **~7.5** |

Phase 0 alone gets the repository to "trustworthy catalog" status.
