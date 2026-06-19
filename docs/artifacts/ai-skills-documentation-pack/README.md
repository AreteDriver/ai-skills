# AI Skills Documentation and 10/10 Improvement Pack

**Repository reviewed:** `AreteDriver/ai-skills`  
**Review date:** 2026-06-18  
**Repository snapshot:** GitHub code-search snapshot at commit `f7528ea34f7a5c68c0886e6d7d698055d2283b99`  
**Review type:** Static architecture, documentation, contract, installer, CI, and product-maturity review

## Executive Judgment

`ai-skills` has a strong idea, substantial content, and several production-shaped components. It is not yet operationally trustworthy enough to call 10/10.

The central failure is **control-plane drift**:

- the README says 70 skills;
- `CLAUDE.md` says 70 skills;
- `registry.yaml` claims 87 total;
- the registry's own category entries calculate to 91;
- at least twelve discoverable `SKILL.md` directories are absent from the registry;
- `bundles.yaml` defines fourteen bundles, while the installer hard-codes ten;
- a bundle advertised in the README is not accepted by the installer;
- some agent entries claim no schema even though a schema file exists;
- contributor instructions reference templates that do not exist.

The repository is therefore stronger as a **content collection** than as a **reliable installable product**.

**Current production-maturity score: 6.7/10.**  
**Potential after the roadmap in this pack: 9.5–10/10.**

## What This Pack Contains

| Area | Documents |
|---|---|
| Evidence layer | Source register, repository inventory, dependency snapshot, incident register, unresolved decisions |
| Product and architecture | Executive assessment, product model, system architecture, skill lifecycle |
| Engineering standards | Authoring guide, security model, testing strategy, installation/operations, governance |
| Implementation contracts | Skill contract v2, registry contract v2, bundle/installer contract v2, evaluation contract |
| Execution | 10/10 roadmap, prioritized backlog, migration plan, release checklist, Claude Code execution brief |

## Recommended Reading Order

1. `docs/00-executive-assessment.md`
2. `sources/operations/known-incidents.md`
3. `docs/02-system-architecture.md`
4. `specs/registry-contract-v2.md`
5. `specs/bundle-and-installer-contract-v2.md`
6. `docs/05-testing-and-evaluation-strategy.md`
7. `plans/10-out-of-10-roadmap.md`
8. `CLAUDE_CODE_EXECUTION_BRIEF.md`

## Governing Principle

> A skill is executable policy. Treat its metadata, behavior, permissions, installation, evaluation, and release evidence with the same rigor as software code.

## Evidence Limitation

The review used repository files retrieved through GitHub file access and indexed code search. The repository could not be cloned into the local artifact environment, so runtime commands were not executed. Findings labeled **confirmed** are directly visible in repository files. Findings labeled **observed** derive from indexed paths and should be reconciled with a full local tree during implementation.
