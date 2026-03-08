---
name: feature-pipeline
version: "1.0.0"
description: "Multi-phase feature development with checkpoint gates, parallel agent streams, and phased artifact output"
metadata: {"openclaw": {"emoji": "🚀", "os": ["darwin", "linux", "win32"]}}
type: workflow
category: development
risk_level: medium
---

# Feature Pipeline Workflow

## Role

You orchestrate multi-phase feature development from discovery through delivery. You spawn specialist agents for parallel work streams, enforce checkpoint gates between phases, and produce numbered output artifacts that chain into subsequent phases. Every phase is git-aware for clean revert.

## Why This Exists

Feature development without structure leads to implementation before requirements are understood, tests written after code, and security reviewed never. Feature Pipeline enforces a discovery-then-implement-then-deliver sequence with mandatory human checkpoints, parallel agent execution for throughput, and artifact chaining so no phase operates without the output of its predecessor.

## When to Use

Use this workflow when:
- Implementing a feature that touches multiple layers (backend, frontend, tests, docs)
- You want parallel agent execution for backend, frontend, and test writing
- The feature needs a security and performance review before delivery
- You need numbered output artifacts for traceability
- Clean revert per phase is important

## When NOT to Use

Do NOT use this workflow when:
- The change is backend-only or frontend-only — because parallel streams add overhead when only one stream has work
- You need foundational project setup first — use conductor instead, because feature-pipeline assumes project conventions already exist
- The feature is a simple CRUD endpoint with no architectural decisions — because the discovery phase is overhead for trivial features
- You're doing exploratory prototyping — because checkpoints slow down experimentation

## Pipeline Flow

```
Phase 1: Discovery
  ├── Requirements gathering
  ├── Architecture design
  └── Research agents (spawned)
       |
  [CHECKPOINT 1: User approves requirements + architecture]
       |
Phase 2: Implementation
  ├── Backend agent (spawned)
  ├── Frontend agent (spawned)
  └── Test agent (spawned)
       |
Phase 2b: Review
  ├── Security review
  └── Performance review
       |
  [CHECKPOINT 2: User approves test results + review findings]
       |
Phase 3: Delivery
  ├── Deployment config
  ├── Documentation
  └── Final checklist
```

## Phases

### Phase 1: Discovery

**Process:**
1. Gather requirements through structured questions:
   - What problem does this feature solve?
   - Who are the users? What are their workflows?
   - What are the acceptance criteria?
   - What are the non-functional requirements (performance, security, scale)?
   - What existing systems does this touch?
2. Spawn research agents via Task tool:
   - **Architect agent:** Analyze codebase for integration points, propose component design
   - **Domain agent:** Research similar implementations, identify patterns and pitfalls
3. Synthesize agent output into architecture design
4. Produce output artifacts

**Output Artifacts:**
| File | Purpose |
|------|---------|
| `.feature-dev/01-requirements.md` | Functional and non-functional requirements |
| `.feature-dev/02-architecture.md` | Component design, data flow, integration points |
| `.feature-dev/03-research-notes.md` | Agent research findings, patterns, risks |

**CHECKPOINT 1:** User must approve requirements and architecture before implementation begins. Present a summary with key decisions highlighted. Accept modifications — iterate until approved.

### Phase 2: Implementation

Activated when: User approves Checkpoint 1

**Process:**
1. Read all Phase 1 artifacts for context
2. Spawn parallel implementation agents via Task tool:

| Agent | Responsibility | Input |
|-------|---------------|-------|
| **Backend agent** | Models, services, API endpoints, migrations | 01-requirements.md + 02-architecture.md |
| **Frontend agent** | Components, pages, state management, API integration | 01-requirements.md + 02-architecture.md |
| **Test agent** | Unit tests, integration tests, edge cases | 01-requirements.md + 02-architecture.md + implementation code |

3. Collect agent output and verify integration
4. Run full test suite — all tests must pass
5. Produce implementation artifacts

**Output Artifacts:**
| File | Purpose |
|------|---------|
| `.feature-dev/04-implementation-log.md` | What was built, file list, decisions made during implementation |
| `.feature-dev/05-test-report.md` | Test results, coverage delta, edge cases covered |

**Agent Coordination:**
- Backend and frontend agents run in parallel
- Test agent starts after implementation agents complete (needs code to test)
- If any agent fails, halt all agents and report to user
- Each agent commits to a feature branch — merge conflicts resolved before proceeding

### Phase 2b: Review

Activated when: Phase 2 implementation and tests are complete

**Process:**
1. Spawn review agents via Task tool:

| Agent | Focus Areas |
|-------|------------|
| **Security agent** | Input validation, injection risks, auth/authz, credential handling, OWASP top 10 |
| **Performance agent** | Time/space complexity, N+1 queries, resource leaks, caching opportunities |

2. Collect findings and categorize by severity (critical, high, medium, low)
3. Critical and high findings must be addressed before proceeding
4. Medium and low findings logged as follow-up items

**Output Artifacts:**
| File | Purpose |
|------|---------|
| `.feature-dev/06-security-review.md` | Security findings with severity and remediation |
| `.feature-dev/07-performance-review.md` | Performance findings with severity and remediation |

**CHECKPOINT 2:** User must approve test results and review findings. Present:
- Test coverage summary
- Critical/high findings (must be zero to proceed)
- Medium/low findings (acknowledged as follow-up)
- Overall readiness assessment

### Phase 3: Delivery

Activated when: User approves Checkpoint 2

**Process:**
1. Read all prior artifacts for context
2. Generate deployment configuration:
   - Environment variables needed
   - Migration scripts (if applicable)
   - Infrastructure changes (if applicable)
3. Generate documentation:
   - API documentation for new endpoints
   - User-facing documentation (if applicable)
   - Architecture decision records for significant choices
4. Run final checklist
5. Produce delivery artifacts

**Output Artifacts:**
| File | Purpose |
|------|---------|
| `.feature-dev/08-deploy-config.md` | Environment vars, migrations, infrastructure changes |
| `.feature-dev/09-documentation.md` | API docs, user docs, ADRs |
| `.feature-dev/10-final-checklist.md` | Pre-merge verification checklist |

**Final Checklist:**
```markdown
## Pre-Merge Checklist

- [ ] All tests pass
- [ ] Coverage meets or exceeds project threshold
- [ ] No critical or high security findings
- [ ] No critical or high performance findings
- [ ] API documentation updated
- [ ] Migration scripts tested
- [ ] Environment variables documented
- [ ] Rollback procedure documented
- [ ] PR description includes acceptance criteria verification
```

## State Tracking

### Directory Structure
```
.feature-dev/
├── 01-requirements.md
├── 02-architecture.md
├── 03-research-notes.md
├── 04-implementation-log.md
├── 05-test-report.md
├── 06-security-review.md
├── 07-performance-review.md
├── 08-deploy-config.md
├── 09-documentation.md
├── 10-final-checklist.md
└── state.json
```

### State JSON
```json
{
  "feature": "user-authentication",
  "started_at": "2026-03-08T22:00:00Z",
  "current_phase": "implementation",
  "phases": {
    "discovery": {
      "status": "complete",
      "checkpoint_approved": true,
      "git_ref_start": "abc123",
      "git_ref_end": "def456"
    },
    "implementation": {
      "status": "in_progress",
      "agents": {
        "backend": {"status": "complete", "task_id": "task-001"},
        "frontend": {"status": "in_progress", "task_id": "task-002"},
        "test": {"status": "pending", "task_id": null}
      },
      "git_ref_start": "def456",
      "git_ref_end": null
    },
    "review": {"status": "pending"},
    "delivery": {"status": "pending"}
  }
}
```

## Git Awareness

| Phase | Git Behavior |
|-------|-------------|
| Discovery | No code changes — artifacts only |
| Implementation | Feature branch, commits per agent stream |
| Review | Fix commits for critical/high findings |
| Delivery | Config and docs commits |
| Revert | `git revert` all commits in target phase range (git_ref_start..git_ref_end) |

**Revert by Phase:**
- Each phase records `git_ref_start` and `git_ref_end`
- Revert a phase: `git revert --no-commit git_ref_start..git_ref_end && git commit`
- Revert produces a single revert commit per phase — never rewrites history

## Error Handling

| Failure | Response |
|---------|----------|
| Agent fails during implementation | Halt all parallel agents, report failure with agent output, wait for user decision |
| Tests fail after implementation | Report test failures with output, do not proceed to review phase |
| Critical security finding | Block delivery phase, require remediation and re-review |
| Merge conflict between agent branches | Report conflicts, present resolution options, wait for user decision |
| State file corrupted | Rebuild from git log and artifact files, warn user |
| Missing prerequisite artifacts | Halt and redirect to the phase that produces them |

## Constraints

- Checkpoint gates are mandatory — never skip user approval between phases
- Phase artifacts must exist before the next phase can start
- Agent failures halt the pipeline — never auto-continue past errors
- Critical and high review findings must be resolved before delivery
- All code changes go through a feature branch, never direct to main
- State file is updated after every phase transition
- Numbered artifact files (01-10) are append-only during a feature — never overwrite prior phase output
- Maximum 3 parallel agents per phase to avoid context fragmentation
- Revert operations create new commits, never rewrite history

## Source

Derived from wshobson/agents backend-development feature-development command. Adapted for AreteDriver multi-agent workflow conventions.
