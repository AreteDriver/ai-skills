# Claude Code Execution Brief: AI Skills Repository Remediation

## Mission

Repair `AreteDriver/ai-skills` so its catalog, installer, documentation, schemas, and tests form one coherent system.

## Non-Negotiable Rules

1. Do not add new stable skills until inventory drift is closed.
2. Preserve source content unless a change is required and documented.
3. Do not manually patch counts in multiple files.
4. Do not retain a hard-coded bundle catalog in the installer.
5. Do not auto-install hooks.
6. Do not delete orphan skills without classifying them.
7. Do not report completion without running the relevant gates.
8. Separate current behavior from intended v2 behavior.
9. Use small, reviewable commits.
10. Record architecture decisions.

## Execution Order

### Workstream A — Truth Repair

- inventory all skill directories;
- compare filesystem to registry;
- reconcile orphans;
- recompute registry counts;
- correct schema flags;
- repair README and `CLAUDE.md`;
- create missing templates.

### Workstream B — Strict Validation

- add strict mode;
- fail stable lane on warnings;
- validate exact registry entry equality;
- validate bundle definitions;
- validate generated docs;
- validate enums and lifecycle;
- add unit tests for validator logic.

### Workstream C — Installer

- write tests that reproduce current bundle mismatch;
- build a resolver that reads `bundles.yaml`;
- add dry-run;
- add hook consent;
- add install manifest;
- add rollback and safe uninstall;
- test every bundle.

### Workstream D — Contract v2

- add schema files;
- generate manifests for a pilot set;
- build registry generator;
- migrate engineering/security pilot skills;
- preserve v1 compatibility.

### Workstream E — Behavioral Evals

- define case schema;
- migrate golden examples;
- add negative-routing and safety cases;
- integrate changed-skill evals into PR CI.

## Required First Tests

Create failing tests for:

1. README `arete-studio-ops` command;
2. content-ops exact contents;
3. all `bundles.yaml` IDs accepted;
4. registry computed stats;
5. technical-debt-auditor schema flag;
6. missing template references;
7. orphan detection under strict mode;
8. uninstall preserving unknown files.

## Definition of Done

- all source-of-truth drift incidents closed;
- every bundle installs exactly as defined;
- registry and docs generated;
- strict CI clean;
- installation reversible;
- pilot stable skills pass behavioral evals;
- implementation notes and ADRs committed.

## Suggested Commit Sequence

1. `test: reproduce catalog and installer drift`
2. `fix: reconcile registry and skill inventory`
3. `docs: replace stale catalog data with generated output`
4. `feat: resolve bundles from bundles.yaml`
5. `feat: add transactional install manifest`
6. `feat: add strict contract validation`
7. `feat: introduce skill manifest v2 pilot`
8. `test: add behavioral evaluation harness`
9. `docs: add governance and contributor documentation`
10. `release: prepare v2 alpha`
