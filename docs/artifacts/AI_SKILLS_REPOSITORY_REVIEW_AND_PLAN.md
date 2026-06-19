# AI Skills Repository Review and 10/10 Plan

**Repository:** `AreteDriver/ai-skills`  
**Review date:** 2026-06-18  
**Snapshot:** `f7528ea34f7a5c68c0886e6d7d698055d2283b99`

# Executive Assessment

## Bottom Line

The project has crossed the line from a prompt collection into a software distribution system, but its engineering controls have not fully caught up.

The content itself is often strong. The repository contains typed agent schemas, orchestration workflows, hooks, bundles, installers, validation, and CI. That is real product architecture.

The weakness is not ambition. It is **truth management**.

A user cannot currently trust that:

- the documented inventory is accurate;
- a named bundle can be installed;
- the installed bundle matches its definition;
- an agent's registry metadata reflects its files;
- a passing CI run means the repository is contract-consistent;
- uninstall will remove only assets owned by this project;
- a skill has been behaviorally tested.

That prevents a 10/10 rating.

## Scorecard

| Dimension | Score | Assessment |
|---|---:|---|
| Product thesis | 9.0 | Clear and valuable |
| Breadth of content | 8.5 | Strong portfolio across engineering, web, data, operations, and workflows |
| Skill depth | 8.0 | Several sophisticated skills and schemas |
| Information architecture | 7.5 | Good conceptual separation, but registry drift |
| Documentation completeness | 7.0 | Many useful docs; no canonical spine |
| Documentation accuracy | 4.5 | Counts, tables, and commands are stale |
| Installer reliability | 4.0 | Catalog duplication breaks documented bundles |
| Contract consistency | 4.5 | Risk vocabulary and schema flags conflict |
| CI and structural validation | 6.0 | Useful baseline; too permissive |
| Behavioral evaluation | 3.0 | No governing executable eval system |
| Security and trust | 5.5 | Risk concepts exist; executable distribution boundary is immature |
| Release governance | 5.0 | Changelog and semantic claims are not synchronized |
| **Weighted maturity** | **6.7** | Strong foundation, unreliable control plane |

## What Is Already Excellent

1. **The three-part model is correct.** Personas, capabilities, and workflows are meaningfully different artifacts.
2. **Typed agent schemas are the right direction.** The technical-debt auditor schema demonstrates mature routing, inputs, outputs, verification, and safety metadata.
3. **Bundles turn the library into products.** They map skills to user jobs.
4. **The v2 template contains strong ideas.** Negative routing, bounded retries, checkpoints, trust, and parallel safety are material improvements.
5. **The repository is public and portable.** Markdown/YAML makes inspection and contribution accessible.
6. **Validation already exists.** The project does not need to start from zero; it needs stricter enforcement and consolidation.

## What Must Change

### 1. End Manual Duplication

Counts, paths, bundle contents, schema flags, and reference tables must be generated. A production catalog cannot be maintained in five places.

### 2. Make Installation a Transaction

Installation must resolve dependencies, preview permissions, stage changes, verify contents, write an ownership manifest, and roll back on failure.

### 3. Test Behavior

A syntactically valid skill can still be vague, contradictory, unsafe, over-broad, or ineffective. Every stable skill needs executable cases.

### 4. Separate Core Contract from Runtime Adapters

Claude Code, OpenClaw, Codex, and other runtimes should consume a neutral skill contract through adapters. Runtime-specific metadata should not pollute the core schema.

### 5. Treat Hooks as Executable Supply Chain

Hooks are code, not documentation. Their installation requires explicit consent, review, checksums, permissions, and security tests.

## 10/10 Definition

A 10/10 release is one where a new user can:

1. run `ai-skills doctor`;
2. search the catalog;
3. inspect a skill's purpose, risk, permissions, compatibility, version, and eval score;
4. preview a bundle installation;
5. install atomically;
6. verify the installed state;
7. update or roll back;
8. remove only project-owned files;
9. reproduce the same result from a signed release;
10. trust that documentation was generated from validated source data.


---

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


---

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


---

# Prioritized Backlog

## P0 — Release Blocking

| ID | Work Item | Acceptance |
|---|---|---|
| AIS-P0-001 | Full skill inventory and orphan reconciliation | Every `SKILL.md` is registered, experimental, deprecated, or archived |
| AIS-P0-002 | Correct registry stats | Generated counts match entries |
| AIS-P0-003 | Installer consumes `bundles.yaml` | No bundle names or contents hard-coded |
| AIS-P0-004 | Fix advertised bundles | Every README example succeeds in integration tests |
| AIS-P0-005 | Normalize risk and approval model | One schema and migration map |
| AIS-P0-006 | Add missing agent/workflow templates | Contributor commands reference existing files |
| AIS-P0-007 | Strict CI | Stable lane fails on orphan, missing schema, drift, or warning |
| AIS-P0-008 | Generate README inventory | Badge and tables derive from registry |
| AIS-P0-009 | Fix schema flags | `has_schema` and related metadata derived |
| AIS-P0-010 | Add safe uninstall ownership | Unknown files can never be deleted |

## P1 — Reliability and Safety

| ID | Work Item | Acceptance |
|---|---|---|
| AIS-P1-001 | Python CLI | Feature parity plus dry-run, doctor, verify |
| AIS-P1-002 | Atomic install and rollback | Failure leaves prior installation valid |
| AIS-P1-003 | Hook consent and review | Hooks absent without explicit approval |
| AIS-P1-004 | Installer integration tests | All bundles tested in temp HOME |
| AIS-P1-005 | Skill Contract v2 | All candidate/stable skills migrated |
| AIS-P1-006 | Eval runner | Executable deterministic and model-graded cases |
| AIS-P1-007 | Stable skill eval minimum | Required suites enforced |
| AIS-P1-008 | Prompt-injection suite | Untrusted-content cases pass |
| AIS-P1-009 | Changelog automation | Every release includes all merged fragments |
| AIS-P1-010 | Governance files | Contribution and security process documented |

## P2 — Product Maturity

| ID | Work Item | Acceptance |
|---|---|---|
| AIS-P2-001 | Generated documentation site | Searchable catalog with health cards |
| AIS-P2-002 | Capability graph | Dependencies, alternatives, conflicts queryable |
| AIS-P2-003 | Runtime adapters | Core-neutral contract with tested adapters |
| AIS-P2-004 | Project lockfile | Repeatable per-project installation |
| AIS-P2-005 | Semantic skill diff | Breaking contract changes detected |
| AIS-P2-006 | Stable/candidate channels | Installer can select release channel |
| AIS-P2-007 | Token footprint metrics | Catalog shows load cost |
| AIS-P2-008 | Team profile bundles | Organization policy overlay supported |

## P3 — Expansion

| ID | Work Item |
|---|---|
| AIS-P3-001 | Private registry support |
| AIS-P3-002 | Signed third-party publisher model |
| AIS-P3-003 | Local opt-in effectiveness feedback |
| AIS-P3-004 | Bundle recommendation engine |
| AIS-P3-005 | Visual catalog and dependency explorer |
