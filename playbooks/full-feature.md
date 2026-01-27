---
name: Full Feature Implementation
description: End-to-end workflow for implementing a feature from requirements to merge.
skills:
  - skills/architecture/system-design.md
  - skills/core/coding-standards.md
  - skills/core/security.md
  - skills/testing/test-strategy.md
  - skills/coding/code-review.md
  - skills/communication/technical-writing.md
---

# Full Feature Playbook

## Phase 1 — Understand
- [ ] Clarify requirements: functional, non-functional, constraints.
- [ ] Identify affected files and modules.
- [ ] Check for related issues or prior art.

## Phase 2 — Design
- [ ] Define data model changes (if any).
- [ ] Define API changes (if any).
- [ ] Record architectural decisions in `decisions/log/`.

## Phase 3 — Implement
- [ ] Create a feature branch.
- [ ] Implement in small, atomic commits.
- [ ] Follow coding standards (`skills/core/coding-standards.md`).
- [ ] Run security checks (`skills/core/security.md`).

## Phase 4 — Test
- [ ] Write unit tests for new logic.
- [ ] Write integration tests for component interactions.
- [ ] Run full test suite — all green.

## Phase 5 — Review & Ship
- [ ] Self-review using `prompts/code-review.md`.
- [ ] Write PR description using `skills/communication/technical-writing.md`.
- [ ] Address review feedback.
- [ ] Merge and verify deployment.
