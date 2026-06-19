# AI-Skills Roadmap

**Project**: AI-Skills — Reusable AI skill library and registry  
**Classification**: Active  
**Version**: 1.0.0 (needs update)  
**Last updated**: 2026-06-18  
**Next review**: 2026-07-18  

---

## Current State (Updated 2026-06-19)

- **144 skills on disk** (114 personas, 17 agents, 13 workflows)
- **Registry, README, and filesystem are fully reconciled**
- `bundles.yaml`: 14 bundles; `tools/install.sh`: dynamically parsed via `scripts/resolve-bundle.py`
- All 7 `agents/analysis/` schema flags corrected
- Templates: `agent-template.md`, `workflow-template.md`, `skill-template-v2.md` all present
- Manifest compiler (`scripts/generate-manifests.py`) generates 144 manifests + `_index.json`
- Registry generator (`scripts/generate-registry.py`) produces canonical `registry.yaml`
- Docs generator (`scripts/generate-docs.py`) produces 6 artifacts including search index and lifecycle dashboard
- **144 eval cases** (100% coverage), all passing in golden mode
- **7 stable skills**, **137 experimental**, lifecycle-managed via `scripts/lifecycle-manager.py`
- **Tag + trigger extraction** auto-derived from SKILL.md content
- **Skill search CLI** (`scripts/skill-search.py`) with full-text, facet, and fuzzy matching
- Installer supports `--search`, `--info`, `--dry-run`, `--preview`, `--uninstall`
- Truth baseline: 10/10 passing ✅
- CI: strict catalog validation, eval coverage gate (≥90%), lifecycle audit, installer integration tests
- Project maturity: **~9.5/10**

---

## Milestones (Completed)

### Phase 1: Catalog Truth ✅
- [x] Update README.md skill count to match filesystem reality (144)
- [x] Auto-generate registry stats from disk scan
- [x] Classify orphans: register 114 personas and 13 workflows properly
- [x] Add missing templates: `agent-template.md`, `workflow-template.md`

### Phase 2: Bundle/Installer Sync ✅
- [x] Rewrite `tools/install.sh` to parse `bundles.yaml` dynamically
- [x] Add `--with-hooks` opt-in flag (listed but not auto-installed)
- [x] Fix `content-ops` bundle mapping (8 skills in YAML)
- [x] Add missing bundles to installer: `project-orchestration`, `eve-frontier`, `session-management`, `arete-studio-ops`

### Phase 3: Registry Integrity ✅
- [x] Auto-derive `has_schema` from disk presence
- [x] Remove hand-written `stats:` block from `registry.yaml` (now auto-generated)
- [x] Backfill changelog or adopt generated changelog

### Phase 4: v2 Contract Rollout ✅
- [x] Introduce `manifest.yaml` equivalent (`manifests/*.json` + `_index.json`)
- [x] Build manifest compiler that generates `registry.yaml` and README tables
- [x] Add `evals/` directories with behavioral test suites (144 cases, 100% coverage)

### Phase 5: Discovery & Governance ✅ (New)
- [x] Auto-extract tags and triggers from SKILL.md
- [x] Build skill-search CLI with faceted filtering
- [x] Add lifecycle field (`experimental | beta | stable | deprecated`)
- [x] Bulk-classify all 144 skills
- [x] Add lifecycle promotion/demotion pipeline with automated gates
- [x] Add deprecation metadata to registry
- [x] Add lifecycle audit gate to CI
- [x] Generate lifecycle dashboard

---

## Prioritized Next Actions

1. ~~Fix README count~~ ✅
2. ~~Fix install.sh~~ ✅
3. ~~Add missing templates~~ ✅
4. ~~Auto-derive registry metadata~~ ✅

---

## Blockers

- None. All phases complete.

## Definition of Done (Overall)

- README, registry.yaml, and filesystem all agree on skill counts ✅
- All templates exist ✅
- Truth baseline passes all checks ✅
- Eval coverage ≥90% (currently 100%) ✅
- Stable skills gated by promotion criteria ✅
- CI catches catalog drift, eval failures, and lifecycle violations ✅
