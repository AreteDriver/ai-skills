---
name: feature-implementation
description: End-to-end feature implementation workflow using WHY/WHAT/HOW framework — from requirements through context mapping, implementation, testing, and PR creation. Use when implementing a complete feature across multiple files.
---

# Feature Implementation Workflow

## Role

You orchestrate the complete lifecycle of implementing a feature — from understanding requirements through shipping a pull request. You coordinate agents through the WHY/WHAT/HOW framework, ensuring every step has clear intent, scope, and execution strategy.

## Workflow Phases

```
Phase 0: Context Mapping     → Understand the codebase
Phase 1: Requirements         → Capture WHY
Phase 2: Design               → Define WHAT
Phase 3: Implementation       → Execute HOW
Phase 4: Verification         → Validate against success criteria
Phase 5: Delivery             → Create PR with full documentation
```

## Phase 0: Context Mapping

**Agent:** context-mapper
**Output:** context_map.yaml

Before anything else, map the territory:

```yaml
context_mapping:
  scan:
    - Project structure and conventions
    - Existing patterns for similar features
    - Test infrastructure and patterns
    - CI/CD pipeline requirements
  identify:
    - Entry points for the new feature
    - Files that will need modification
    - Dependencies (internal and external)
    - Potential conflicts with in-progress work
```

## Phase 1: Requirements (WHY)

**Agent:** supervisor
**Output:** requirements.yaml

Capture the complete intent:

```yaml
why:
  goal: "[User's actual objective]"
  motivation: "[Why this feature matters]"
  success_criteria:
    - "[Measurable criterion 1]"
    - "[Measurable criterion 2]"
    - "[Measurable criterion 3]"
  anti_goals:
    - "[What we explicitly don't want]"
  user_stories:
    - as: "[role]"
      i_want: "[capability]"
      so_that: "[benefit]"
  acceptance_tests:
    - given: "[precondition]"
      when: "[action]"
      then: "[expected result]"
```

### Requirements Validation Checklist

| Question | Required |
|----------|----------|
| Is the goal specific enough to test against? | Yes |
| Are success criteria measurable? | Yes |
| Are anti-goals explicit? | Yes |
| Do acceptance tests cover edge cases? | Yes |
| Is the scope bounded? | Yes |

## Phase 2: Design (WHAT)

**Agent:** software-architect (persona) + context-mapper
**Output:** design.yaml

Define the scope precisely:

```yaml
what:
  architecture:
    pattern: "[e.g., Repository pattern, Event-driven, etc.]"
    rationale: "[Why this pattern fits]"

  files_to_create:
    - path: "src/features/new-feature/handler.ts"
      purpose: "Request handler for the new feature"
    - path: "src/features/new-feature/handler.test.ts"
      purpose: "Tests for the handler"

  files_to_modify:
    - path: "src/routes/index.ts"
      change: "Add route for new feature"
      lines: [45, 67]
    - path: "src/types/index.ts"
      change: "Add type definitions"

  interfaces:
    - name: "NewFeatureInput"
      fields:
        - name: "field1"
          type: "string"
          required: true
        - name: "field2"
          type: "number"
          required: false

  data_flow: "Client → Route → Handler → Service → Database → Response"

  dependencies:
    new: []  # Prefer no new deps
    existing: ["express", "prisma"]
```

## Phase 3: Implementation (HOW)

**Agent:** senior-software-engineer (persona) + system agents
**Output:** Working code with tests

Execute in disciplined order:

```yaml
how:
  strategy: "test-first"

  steps:
    - step: 1
      action: "Write failing tests from acceptance criteria"
      agent: system
      files: ["src/features/new-feature/handler.test.ts"]
      risk: low
      acceptance:
        - "Tests exist and fail for the right reasons"

    - step: 2
      action: "Implement types and interfaces"
      agent: system
      files: ["src/types/index.ts"]
      risk: low
      depends_on: []
      acceptance:
        - "Types compile without errors"

    - step: 3
      action: "Implement core feature logic"
      agent: system
      files: ["src/features/new-feature/handler.ts"]
      risk: medium
      depends_on: [1, 2]
      acceptance:
        - "All tests from step 1 pass"
        - "No lint warnings"

    - step: 4
      action: "Wire up routes and middleware"
      agent: system
      files: ["src/routes/index.ts"]
      risk: medium
      depends_on: [3]
      acceptance:
        - "Feature accessible via expected endpoint"

    - step: 5
      action: "Run full test suite"
      agent: system
      risk: low
      depends_on: [4]
      acceptance:
        - "All existing tests still pass"
        - "New tests pass"
        - "No regressions"

  quality_gates:
    - name: "Tests pass"
      after_step: 5
      check: "npm test"
      on_failure: block

    - name: "Lint clean"
      after_step: 5
      check: "npm run lint"
      on_failure: warn

    - name: "Type check"
      after_step: 5
      check: "npm run typecheck"
      on_failure: block

    - name: "Build succeeds"
      after_step: 5
      check: "npm run build"
      on_failure: block
```

## Phase 4: Verification

**Agent:** testing-specialist (persona) + code-reviewer (persona)
**Output:** Verification report

```yaml
verification:
  automated:
    - "All unit tests pass"
    - "Integration tests pass"
    - "Lint and type check clean"
    - "Build succeeds"
    - "No new security vulnerabilities (npm audit)"

  manual_review:
    - "Code follows project conventions"
    - "Error handling is comprehensive"
    - "No unnecessary complexity"
    - "Documentation is adequate"
    - "Acceptance criteria from Phase 1 are met"

  regression:
    - "Existing functionality unaffected"
    - "Performance within acceptable bounds"
    - "No new console errors or warnings"
```

## Phase 5: Delivery

**Agent:** github-operations
**Output:** Pull request with full documentation

```yaml
delivery:
  branch: "feat/[feature-name]"
  commit_strategy: "atomic commits per logical change"

  pr_template: |
    ## Summary
    [1-2 sentence description]

    ## WHY
    - Goal: [from Phase 1]
    - Motivation: [from Phase 1]

    ## WHAT Changed
    - [File 1]: [what changed and why]
    - [File 2]: [what changed and why]

    ## HOW to Test
    - [ ] [Acceptance test 1]
    - [ ] [Acceptance test 2]
    - [ ] [Acceptance test 3]

    ## Checklist
    - [ ] Tests pass
    - [ ] Lint clean
    - [ ] Types check
    - [ ] Build succeeds
    - [ ] No new dependencies (or justified)
    - [ ] Documentation updated (if needed)
```

## Orchestration

The supervisor coordinates this workflow by:

1. Invoking context-mapper for Phase 0
2. Engaging the user to validate WHY (Phase 1)
3. Using software-architect persona for WHAT (Phase 2)
4. Decomposing HOW into agent-executable steps (Phase 3)
5. Running quality gates between steps
6. Using code-reviewer persona for verification (Phase 4)
7. Using github-operations for delivery (Phase 5)

```
Supervisor
├── Phase 0: context-mapper agent
├── Phase 1: user interaction
├── Phase 2: software-architect persona
├── Phase 3: system agents (per step)
│   ├── Step 1: Write tests
│   ├── Step 2: Implement types
│   ├── Step 3: Implement logic
│   ├── Step 4: Wire up routes
│   └── Step 5: Run tests (quality gate)
├── Phase 4: code-reviewer persona
└── Phase 5: github-operations agent
```

## Constraints

- Never skip Phase 0 (context mapping) — blind implementation causes regressions
- Phase 1 (WHY) must be validated with the user before proceeding
- Phase 3 follows test-first by default (override with strategy field)
- Quality gates are blocking — failed gates stop the pipeline
- Phase 5 always creates a PR, never pushes directly to main
- Each phase produces a structured artifact that feeds the next phase
