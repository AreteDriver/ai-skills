---
name: Debug and Fix
description: Workflow for triaging a bug from report to verified fix.
skills:
  - skills/coding/debugging.md
  - skills/core/security.md
  - skills/testing/test-strategy.md
---

# Debug and Fix Playbook

## Phase 1 — Triage
- [ ] Read the bug report / error log.
- [ ] Classify: crash, wrong result, performance, security.
- [ ] Determine severity and affected users.

## Phase 2 — Reproduce
- [ ] Identify exact steps / input to trigger the bug.
- [ ] Confirm reproduction locally.

## Phase 3 — Diagnose
- [ ] Trace the code path from input to failure.
- [ ] Form a hypothesis about root cause.
- [ ] Verify with a targeted test or log.

## Phase 4 — Fix
- [ ] Make the minimal change that addresses root cause.
- [ ] Check for the same pattern elsewhere.
- [ ] Add a regression test.

## Phase 5 — Verify
- [ ] Run full test suite.
- [ ] Confirm the original reproduction case now passes.
- [ ] Self-review the diff for security issues.
