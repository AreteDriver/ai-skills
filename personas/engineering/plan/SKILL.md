---
name: plan
description: Implementation Planning
---

# /plan - Implementation Planning

Create structured implementation plans with task breakdown, dependencies, and risk assessment.

## Usage
```
/plan <feature or task description>
```

## What This Skill Does

1. **Analyze Requirements** - Break down the request into concrete deliverables
2. **Task Breakdown** - Create actionable tasks with clear acceptance criteria
3. **Dependency Mapping** - Identify task dependencies and optimal ordering
4. **Risk Assessment** - Flag potential blockers, unknowns, and mitigation strategies
5. **Output Plan** - Generate a structured plan ready for execution

## Output Format

```markdown
# Implementation Plan: [Feature Name]

## Overview
Brief description of what we're building and why.

## Deliverables
- [ ] Deliverable 1
- [ ] Deliverable 2

## Tasks

### Phase 1: [Phase Name]
| Task | Description | Dependencies | Risk |
|------|-------------|--------------|------|
| 1.1  | Task desc   | None         | Low  |
| 1.2  | Task desc   | 1.1          | Med  |

### Phase 2: [Phase Name]
...

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Risk 1 | High | Medium | Strategy |

## Open Questions
- Question needing clarification?

## Definition of Done
- [ ] All tasks completed
- [ ] Tests passing
- [ ] Documentation updated
```

## Instructions for Claude

When /plan is invoked:

1. **Clarify scope** - Ask questions if requirements are ambiguous
2. **Research first** - Read relevant code to understand current state
3. **Break down tasks** - Each task should be completable in one focused session
4. **Identify dependencies** - What must happen before what?
5. **Assess risks** - What could go wrong? What's unknown?
6. **No time estimates** - Focus on what, not when
7. **Use TodoWrite** - After plan approval, create todos from tasks
