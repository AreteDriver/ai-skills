# Skill Authoring Guide

## Quality Standard

A good skill is not long. It is **specific, routable, bounded, verifiable, and demonstrably useful**.

## Authoring Sequence

1. Define the user job.
2. State when the skill should and should not be used.
3. Define outputs and completion criteria.
4. Define tool permissions and side effects.
5. Define failure behavior.
6. Add examples.
7. Add executable eval cases.
8. Run contract validation.
9. Run behavioral evaluation.
10. Request review.

## Required Metadata

See `specs/skill-contract-v2.md`. At minimum:

- stable ID
- name
- version
- kind
- category
- lifecycle status
- description
- tags
- compatibility
- risk severity
- approval class
- tool allowlist
- parallel safety
- maintainer
- last reviewed date

## Required Content by Kind

### Persona

- Role
- When to use
- When not to use
- Always
- Never
- Output expectations
- Constraints
- Verification
- Examples

### Agent Capability

Everything required for a persona, plus:

- typed operations
- inputs and outputs
- tool policy
- side effects
- preconditions
- postconditions
- retries
- idempotency
- approval requirements
- failure and partial-success semantics

### Workflow

- intent
- entry criteria
- state model
- steps
- dependencies
- checkpoints
- gates
- rollback or recovery
- completion contract
- handoff artifacts

## Negative Routing

Every stable skill must name alternatives.

Bad:

> Do not use for unrelated work.

Good:

> Do not use for diagnosing one failing test. Use `workflow-debugger` because this skill performs broad repository assessment and will add unnecessary scope.

## Tool Policy

Do not use `tools: ["*"]` in stable skills without an explicit waiver.

Preferred:

```yaml
tools:
  allow:
    - Read
    - Glob
    - Grep
  deny:
    - Bash
    - Write
    - Edit
```

Tool use must match the skill's purpose. A reporting persona does not need shell access merely because examples contain commands.

## Error Handling

Use bounded strategies:

| Failure | Default |
|---|---|
| Invalid input | Return structured validation error |
| Missing environment capability | Stop or use documented fallback |
| Recoverable generation defect | Retry up to 2–3 times |
| Permission or authentication | Stop and request user action |
| External side effect uncertain | Do not retry automatically |
| Repeated identical failure | Stop and report attempted remedies |

## Token Budget

Each skill should declare an approximate loaded token footprint. Split large references into on-demand files. The core skill should contain policy and routing, not an encyclopedia.

## Examples and Evals

Examples teach. Evals prove.

Minimum stable-skill eval set:

- one happy path;
- one ambiguous routing case;
- one "do not use" case;
- one malformed-input case when inputs are typed;
- one safety or overreach case;
- one output-contract case.

## Review Checklist

- Is the skill narrower than its title suggests?
- Does it duplicate an existing skill?
- Are alternatives named?
- Are permissions minimal?
- Are all promised outputs testable?
- Does it distinguish advice from execution?
- Are retries bounded?
- Are external facts or references dated?
- Are examples realistic?
- Can a reviewer explain why this skill should exist?
