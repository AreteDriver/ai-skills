# AI Skills 10/10 Roadmap

## Objective

Move the repository from a strong but inconsistent content library to a trustworthy skill package ecosystem.

## Phase 0 — Stop the Drift

**Exit condition:** One accurate inventory and no documented core command is false.

- freeze new stable-skill additions temporarily;
- perform full filesystem inventory;
- reconcile every orphan skill;
- correct registry entries and stats;
- correct README and `CLAUDE.md`;
- add the missing templates;
- mark generated vs authored files;
- add strict validator mode;
- make stable CI fail on warnings.

## Phase 1 — Single Source of Truth

**Exit condition:** Registry, docs, and bundle resolution are generated from skill sources.

- adopt Skill Contract v2;
- add manifests;
- build manifest compiler;
- generate registry;
- generate counts and catalog tables;
- generate schema-presence fields;
- validate unique IDs;
- remove duplicated manual statistics.

## Phase 2 — Installer Repair

**Exit condition:** Every bundle installs exactly as defined and can be safely reversed.

- replace hard-coded bundle table;
- parse bundle YAML;
- add dry-run and permission preview;
- make hooks opt-in;
- add install ownership manifest;
- implement atomic staging and rollback;
- add collision protection;
- implement safe update and uninstall;
- add integration-test matrix.

## Phase 3 — Behavioral Quality

**Exit condition:** Stable skills have evidence of effectiveness and safety.

- create eval schema and runner;
- migrate existing golden examples into executable cases;
- require negative routing and safety cases;
- add changed-skill PR evals;
- add full regression lane;
- publish quality cards.

## Phase 4 — Trust and Portability

**Exit condition:** Core contracts are runtime-neutral and executable assets are governed.

- separate adapters;
- add Claude Code adapter tests;
- move OpenClaw fields out of core validation;
- formalize tool and approval policy;
- security-test hooks;
- add signed releases, checksums, and provenance;
- add compatibility matrix.

## Phase 5 — Productization

**Exit condition:** Discovery, team use, and community contribution are first-class.

- build CLI search and inspect;
- generate documentation site;
- add project lockfiles;
- add team profiles and private overlays;
- add contributor and governance files;
- add deprecation and migration tooling;
- add release automation;
- expose capability graph.

## 10/10 Acceptance Criteria

| Area | Acceptance |
|---|---|
| Inventory | Filesystem, registry, docs, and installer agree automatically |
| Installation | Atomic, idempotent, reversible, ownership-safe |
| Bundles | One definition, exact contract tests |
| Contracts | Every active skill validates against v2 |
| Behavior | Every stable skill passes required eval suites |
| Security | Permissions explicit; hooks opt-in and tested |
| Portability | Claims backed by adapter tests |
| Docs | Reference generated; conceptual guides current |
| Release | Signed, reproducible, migration-aware |
| Governance | Contribution, review, ownership, lifecycle defined |

## Recommended Release Milestones

- `v1.1.0`: truth repair and strict CI
- `v2.0.0-alpha`: manifests, generated registry, new CLI preview
- `v2.0.0-beta`: installer transactions and integration tests
- `v2.0.0-rc`: behavioral evals and adapter validation
- `v2.0.0`: signed stable release
