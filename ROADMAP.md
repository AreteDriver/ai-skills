# AI-Skills Roadmap

**Project**: AI-Skills — Reusable AI skill library and registry  
**Classification**: Active  
**Version**: 1.0.0 (needs update)  
**Last updated**: 2026-06-18  
**Next review**: 2026-07-18  

---

## Current State

- **144 skills on disk** (114 personas, 17 agents, 13 workflows)
- README claims 70 skills; registry.yaml claims 87
- `bundles.yaml`: 14 bundles; `tools/install.sh`: hard-codes 10
- 7 `agents/analysis/` entries have `schema.yaml` on disk but `has_schema: false` in registry
- Missing templates: `agent-template.md`, `workflow-template.md`
- Changelog frozen at v1.0.0
- No v2 contracts (manifests, generated registry, CLI, evals)
- Truth baseline: 9/10 passing 🟡

---

## Milestones

### Phase 1: Catalog Truth (Q3 2026)
- [ ] Update README.md skill count to match filesystem reality (144)
- [ ] Auto-generate registry stats from disk scan instead of hand-maintained
- [ ] Classify orphans: register 114 personas and 13 workflows properly
- [ ] Add missing templates: `agent-template.md`, `workflow-template.md`

### Phase 2: Bundle/Installer Sync (Q3 2026)
- [ ] Rewrite `tools/install.sh` to parse `bundles.yaml` dynamically
- [ ] Add `--with-hooks` opt-in flag
- [ ] Fix `content-ops` bundle mapping (8 skills in YAML → installer returns 4)
- [ ] Add missing bundles to installer: `project-orchestration`, `eve-frontier`, `session-management`, `arete-studio-ops`

### Phase 3: Registry Integrity (Q3-Q4 2026)
- [ ] Auto-derive `has_schema` from disk presence
- [ ] Remove hand-written `stats:` block from `registry.yaml`
- [ ] Backfill changelog since v1.0.0 or adopt generated changelog

### Phase 4: v2 Contract Rollout (Q4 2026)
- [ ] Introduce `manifest.yaml` to pilot set of stable skills (3-5 personas + all agents)
- [ ] Build manifest compiler (Python) that generates `registry.yaml` and README tables
- [ ] Add `evals/` directories with behavioral test suites

---

## Prioritized Next Actions

1. **Fix README count** — update to 144 skills (5 min)
2. **Fix install.sh** — parse bundles.yaml dynamically (1-2 days)
3. **Add missing templates** — create `agent-template.md`, `workflow-template.md` (1 hour)
4. **Auto-derive registry metadata** — script to scan filesystem and update registry (1-2 days)

---

## Blockers

- None. All fixes are mechanical.

## Definition of Done (Phase 1)

- README, registry.yaml, and filesystem all agree on skill counts
- Missing templates exist
- Truth baseline passes all checks
