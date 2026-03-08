---
name: conductor
version: "1.0.0"
description: "Context-driven development workflow — interactive setup, spec generation, TDD implementation with checkpoints and revert"
metadata: {"openclaw": {"emoji": "🎼", "os": ["darwin", "linux", "win32"]}}
type: workflow
category: development
risk_level: medium
---

# Conductor Workflow

## Role

You orchestrate context-driven development from project setup through implementation. You guide the user through interactive Q&A to build foundational artifacts, generate specifications and phased plans, then execute tasks using TDD with mandatory checkpoints between phases. You detect whether a project is greenfield or brownfield and adapt accordingly.

## Why This Exists

Feature development without foundational context produces inconsistent code. Without a product vision, tech stack decisions, workflow rules, and style guides, every session starts from scratch and drifts from prior decisions. Conductor creates and maintains these artifacts so every implementation phase has the same shared context.

## When to Use

Use this workflow when:
- Starting a new project and need to establish foundational artifacts (product.md, tech-stack.md, workflow.md, style-guide.md)
- Planning and implementing a feature that spans multiple files or concerns
- You want TDD-driven implementation with explicit user approval between phases
- You need the ability to revert by logical unit (track, phase, or task)
- Managing multiple feature tracks with prioritization

## When NOT to Use

Do NOT use this workflow when:
- The change is a single-file bug fix — because the overhead of setup/spec/implement phases is not justified for trivial changes
- The project already has comprehensive planning docs and you just need to code — use feature-pipeline instead, because conductor's value is in artifact generation
- You need parallel agent execution — use feature-pipeline instead, because conductor is sequential and single-threaded
- The task is exploratory research with no clear deliverable — because conductor expects concrete implementation targets

## Pipeline Flow

```
1. Setup Phase (interactive, one-time per project)
       |
       v
2. Detect: Greenfield or Brownfield
       |
       v
3. New-Track Phase (per feature)
       |
   [CHECKPOINT: user approves spec + plan]
       |
       v
4. Implement Phase (per task in plan)
       |
   [CHECKPOINT: user approves each phase completion]
       |
       v
5. Track Complete
```

## Phases

### Phase 1: Setup (One-Time)

Activated when: No `.conductor/` directory exists, or user invokes `/conductor setup`

**Process:**
1. Detect project type — scan for existing files (package.json, pyproject.toml, Cargo.toml, etc.)
2. Classify as greenfield (no source code) or brownfield (existing codebase)
3. Interactive Q&A to establish:
   - Product vision and core value proposition
   - Target users and key workflows
   - Tech stack decisions and rationale
   - Development workflow preferences (branching, testing, CI)
   - Code style conventions
4. Generate foundational artifacts

**Output Artifacts:**
| File | Purpose |
|------|---------|
| `.conductor/product.md` | Product vision, users, value prop, key workflows |
| `.conductor/tech-stack.md` | Languages, frameworks, infrastructure, rationale for each choice |
| `.conductor/workflow.md` | Branching model, PR conventions, testing requirements, CI expectations |
| `.conductor/style-guide.md` | Naming conventions, file organization, code patterns, anti-patterns |
| `.conductor/state.json` | Tracks, phases, task status, git refs for revert |

**Brownfield Adaptations:**
- Scan existing code for conventions (naming, structure, patterns)
- Read existing docs (README, CONTRIBUTING, CLAUDE.md)
- Propose artifacts that complement rather than contradict what exists
- Flag conflicts between detected patterns and proposed conventions

### Phase 2: New Track

Activated when: User invokes `/conductor track "feature description"`

**Process:**
1. Read all foundational artifacts for context
2. Gather requirements through targeted questions (3-5 questions max)
3. Generate detailed specification
4. Produce phased implementation plan with task breakdown
5. Each task includes: description, acceptance criteria, test expectations, estimated complexity

**Output Artifacts:**
| File | Purpose |
|------|---------|
| `.conductor/tracks/<track-id>/spec.md` | Detailed feature specification |
| `.conductor/tracks/<track-id>/plan.md` | Phased implementation plan with numbered tasks |

**CHECKPOINT:** User must approve spec and plan before implementation begins. Modifications accepted — iterate until approved.

### Phase 3: Implement

Activated when: User approves a track's spec and plan

**Process per task:**
1. Read spec, plan, and all foundational artifacts
2. Write failing tests first (TDD red phase)
3. Implement minimum code to pass tests (TDD green phase)
4. Refactor if needed (TDD refactor phase)
5. Verify all tests pass
6. Update state.json with completion status and git ref
7. Report task outcome to user

**Verification Checkpoints:**
- After each task: tests must pass, linter must pass
- After each phase: user approval required before next phase
- On any failure: halt and report — never auto-continue past errors

**State Tracking:**
```json
{
  "project": "project-name",
  "setup_complete": true,
  "tracks": {
    "track-001": {
      "name": "user authentication",
      "status": "in_progress",
      "phases": [
        {
          "name": "Phase 1: Data Models",
          "status": "complete",
          "tasks": [
            {
              "id": "task-001",
              "description": "Create User model with email/password fields",
              "status": "complete",
              "git_ref": "abc123",
              "tests_passing": true
            }
          ]
        }
      ]
    }
  }
}
```

### Phase 4: Revert

Activated when: User invokes `/conductor revert <scope>`

**Revert Scopes:**
| Scope | What It Reverts | Mechanism |
|-------|-----------------|-----------|
| `task <task-id>` | Single task | `git revert` to pre-task ref |
| `phase <phase-name>` | All tasks in a phase | Sequential `git revert` for all phase tasks |
| `track <track-id>` | Entire feature track | Sequential `git revert` for all track tasks |

**Safety:**
- Show user exactly which commits will be reverted before executing
- Require explicit confirmation
- Update state.json after revert
- Never force-push — always create revert commits

## Track Management

| Command | Action |
|---------|--------|
| `/conductor tracks` | List all tracks with status |
| `/conductor track "description"` | Create new track |
| `/conductor prioritize` | Reorder tracks by priority |
| `/conductor status` | Show current state (active track, phase, task) |
| `/conductor resume` | Pick up where you left off |

## Error Handling

| Failure | Response |
|---------|----------|
| Tests fail during implementation | Halt task, report failure with test output, wait for user decision |
| Lint errors after implementation | Halt task, report errors, attempt auto-fix, re-run verification |
| User rejects spec/plan at checkpoint | Iterate on feedback, regenerate artifacts, re-present for approval |
| State file corrupted | Rebuild from git log, warn user about reconstruction |
| Missing foundational artifacts | Redirect to setup phase before allowing track creation |
| Conflicting existing code patterns | Flag conflicts explicitly, ask user to resolve before proceeding |

## Constraints

- Never skip checkpoints — user approval is mandatory between phases
- Never auto-continue past test failures or lint errors
- Foundational artifacts must exist before any track can be created
- Every task must have a corresponding git ref for revert capability
- State file is the source of truth — keep it synchronized with actual git state
- TDD is non-negotiable — tests before implementation for every task
- Revert operations create new commits, never rewrite history
- Maximum 10 tasks per phase — if more are needed, split into sub-phases

## Source

Derived from wshobson/agents conductor plugin. Adapted for AreteDriver development workflow conventions.
