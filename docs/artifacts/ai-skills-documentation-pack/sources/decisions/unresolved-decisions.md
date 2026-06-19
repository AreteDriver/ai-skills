---
title: AI Skills Unresolved Decisions
source_id: SRC-AIS-DEC-001
status: active
authority: medium
owner: Project Owner
date_created: 2026-06-18
date_collected: 2026-06-18
current: true
sensitive: false
related_documents:
  - plans/migration-plan.md
---

# Unresolved Decisions

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| AIS-DEC-001 | Canonical metadata source | Registry-first; SKILL frontmatter-first; separate manifest | Separate `manifest.yaml` or strict frontmatter, then generate registry |
| AIS-DEC-002 | Installer implementation | Continue Bash; Python CLI; packaged binary | Python CLI; retain shell wrapper |
| AIS-DEC-003 | Global identity | Basename; namespaced ID; UUID | Namespaced ID plus stable slug |
| AIS-DEC-004 | Risk vocabulary | low/medium/high/critical; safe/caution/destructive; operation classes | Risk severity plus separate approval class |
| AIS-DEC-005 | Hook installation default | Automatic with bundles; prompt; explicit flag | Explicit `--with-hooks` and permission preview |
| AIS-DEC-006 | Stable vs experimental | One catalog; separate directories; lifecycle field | Lifecycle field and release channels |
| AIS-DEC-007 | Schema format | Custom YAML; JSON Schema; Pydantic | JSON Schema as interchange; Pydantic implementation |
| AIS-DEC-008 | Framework portability | Core mixed metadata; adapter folders | Core neutral contract plus adapters |
| AIS-DEC-009 | Behavioral evaluation backend | Live model only; fixture only; hybrid | Hybrid deterministic + optional model eval |
| AIS-DEC-010 | Orphan skills | Register all; delete; archive | Audit individually, then register or move to experimental |
| AIS-DEC-011 | Physical restructure | Preserve paths; consolidate under `skills/` | Preserve paths for v2, normalize logically first |
| AIS-DEC-012 | Release unit | Whole repository; per-skill; both | Repository release plus per-skill versions |
