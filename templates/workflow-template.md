---
name: workflow-name
version: "1.0.0"
lifecycle: experimental
description: One-line description of what this workflow does
---

# Workflow Name

## WHY — Intent

**Goal:** [What this workflow achieves]
**Motivation:** [Why this matters]
**Success Criteria:**
- Criterion 1
- Criterion 2

**Anti-Goals:**
- Out of scope item 1
- Out of scope item 2

## WHAT — Scope

**Inputs:**
- Input 1: [description and type]
- Input 2: [description and type]

**Outputs:**
- Output 1: [description and format]
- Output 2: [description and format]

**Dependencies:**
- Dependency 1
- Dependency 2

**Files In Scope:**
- `path/to/file1`
- `path/to/file2`

**Files Out of Scope:**
- `path/to/unrelated`

## HOW — Plan

### Phase 1: [Phase Name]

1. Step 1
2. Step 2
3. Step 3

**Quality Gate:** [What must be true to proceed]

### Phase 2: [Phase Name]

1. Step 1
2. Step 2

**Quality Gate:** [What must be true to proceed]

### Phase 3: [Phase Name]

1. Step 1

**Completion Criteria:**
- All outputs delivered
- Quality gates passed
- User confirmation received

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Risk 1 | High | Mitigation 1 |
| Risk 2 | Medium | Mitigation 2 |

## Rollback

If failure occurs at any phase:
1. Revert changes made in current phase
2. Notify user with specific failure point
3. Preserve artifacts from previous successful phases
