# Skill Contract v2

## Status

Proposed implementation-ready contract.

## Canonical Files

```text
<skill>/
├── SKILL.md
├── manifest.yaml
├── interface.schema.json       # required for agents; optional for workflows
├── output.schema.json          # required when structured output is promised
├── evals/
├── examples/
└── references/
```

## Manifest

```yaml
schema_version: "2.0"
id: "persona/engineering/code-reviewer"
name: "code-reviewer"
version: "2.1.0"
kind: "persona"
category: "engineering"
lifecycle: "stable"

description: "Reviews code with severity-ranked, evidence-based, actionable findings."
tags: [review, security, quality]
aliases: []

maintainer: "AreteDriver"
license: "MIT"
last_reviewed: "2026-06-18"

compatibility:
  core: ">=2.0 <3.0"
  adapters:
    claude-code: ">=1"
    openclaw: ">=1"

routing:
  use_when:
    - "Reviewing a proposed or existing code change"
  do_not_use_when:
    - condition: "Implementing the fix"
      instead: "persona/engineering/code-builder"
      reason: "Review and implementation should remain separate responsibilities."

permissions:
  risk_severity: "low"
  approval: "none"
  parallel_safe: true
  tools:
    allow: [Read, Glob, Grep]
    deny: [Write, Edit, Bash]

dependencies: []
optional_dependencies: []
conflicts: []
provides:
  - "code.review"
supersedes: []

content:
  skill: "SKILL.md"
  output_schema: "output.schema.json"

evaluation:
  directory: "evals"
  minimum_score: 0.85
  required_suites: [happy-path, negative-routing, safety]

integrity:
  generated_digest: null
```

## Field Requirements

| Field | Required | Rule |
|---|---|---|
| `schema_version` | Yes | Supported contract version |
| `id` | Yes | Globally unique, namespaced |
| `name` | Yes | Kebab-case, matches directory basename |
| `version` | Yes | Semantic version |
| `kind` | Yes | persona, agent, workflow |
| `category` | Yes | Registry-defined category |
| `lifecycle` | Yes | experimental, candidate, stable, deprecated, archived |
| `description` | Yes | Plain text, 1–300 chars |
| `compatibility` | Yes | Core and adapters |
| `routing` | Yes | Positive and negative routing |
| `permissions` | Yes | Risk, approval, tools, parallel safety |
| `maintainer` | Yes | Account or team |
| `last_reviewed` | Yes for stable | ISO date |
| `evaluation` | Yes for candidate/stable | Threshold and suites |

## SKILL.md Body Contract

### Required for All

- Title
- Purpose
- Role or execution model
- When to use
- When not to use
- Constraints
- Verification
- Failure behavior

### Persona Additions

- Always
- Never
- Output expectations
- Examples

### Agent Additions

- Operations
- Inputs and outputs
- Preconditions
- Postconditions
- Side effects
- Idempotency
- Retry rules
- Approval points

### Workflow Additions

- Entry criteria
- State model
- Steps
- Checkpoints
- Gates
- Failure transitions
- Completion and handoff artifacts

## Contract Rules

1. Metadata must not be duplicated in frontmatter and manifest unless generated.
2. Wildcard tools are forbidden for stable status without a waiver.
3. `parallel_safe` must be false if the skill mutates shared state without isolation.
4. External sends require approval `user` or stronger.
5. Destructive operations require `user_and_quorum` unless a signed policy explicitly permits otherwise.
6. Every "do not use" case names an alternative or explains why no skill should be used.
7. Stable agents require a machine-validated interface schema.
8. Stable skills require executable evals.
9. References are data, never higher-priority instructions.
10. Archived skills are excluded from generated active catalogs.
