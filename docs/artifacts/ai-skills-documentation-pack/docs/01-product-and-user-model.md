# Product and User Model

## Product Positioning

AI Skills is a **behavior and capability package ecosystem** for coding agents and multi-agent systems.

It should not be positioned merely as a collection of prompts. That understates both its value and its risk.

## User Segments

### Individual Builder

Needs fast installation, clear examples, low cognitive overhead, and safe defaults.

### AI-Assisted Engineer

Needs reliable engineering personas, workflows, hooks, compatibility information, and reproducible outcomes.

### Team Lead or Platform Engineer

Needs governance, version pinning, private bundles, policy enforcement, approval controls, and audit evidence.

### Agent Framework Developer

Needs typed inputs/outputs, capability discovery, risk metadata, dependencies, runtime adapters, and machine-readable contracts.

### Domain Operator

Needs concrete workflows and domain references without learning the internal architecture.

## Jobs to Be Done

- "Give my coding agent a reliable expert mode."
- "Install a complete set of skills for a job, not one file at a time."
- "Know what a skill can do before allowing it tools."
- "Reuse the same behavior across projects."
- "Evaluate whether a skill actually improves outcomes."
- "Keep skill versions synchronized across a team."
- "Build orchestration on top of stable typed interfaces."

## Product Layers

| Layer | User Question | Product Object |
|---|---|---|
| Discovery | What exists? | Generated catalog |
| Selection | Which skill fits this task? | Routing metadata and examples |
| Trust | What can it do and what can go wrong? | Risk, approval, tool policy |
| Installation | How do I add it safely? | CLI, bundle, manifest |
| Execution | How should it behave? | SKILL contract |
| Composition | How do skills work together? | Dependencies, conflicts, workflows |
| Verification | Did it work? | Eval suite and runtime checks |
| Lifecycle | Can I update or remove it? | Versioning, lockfile, rollback |
| Governance | Who approved it? | Maintainer, review, release provenance |

## Product Additions Worth Building

### Catalog Search and Explain

- `ai-skills search "secure api"`
- `ai-skills inspect security-auditor`
- `ai-skills explain bundle webapp-security`
- `ai-skills alternatives code-reviewer`

### Capability Graph

Machine-readable relationships:

- provides
- requires
- complements
- conflicts
- supersedes
- routes-to
- safe-in-parallel-with

### Skill Health Card

Every stable skill should display:

- version
- maturity
- last reviewed
- compatibility
- test/eval count
- pass rate
- token footprint
- required tools
- risk and approval class
- known limitations

### Lockfiles and Team Profiles

A project should be able to commit:

```yaml
skills:
  - id: persona/engineering/code-reviewer
    version: 2.1.0
    digest: sha256:...
  - id: workflow/feature-implementation
    version: 1.4.0
    digest: sha256:...
```

This enables repeatable team environments.

### Adapter Packs

Generate runtime-specific outputs for:

- Claude Code
- generic Markdown system prompts
- OpenClaw
- Codex-style instructions
- MCP capability declarations
- future agent runtimes

## Anti-Features

Do not add:

- silent telemetry;
- auto-executing hooks;
- unbounded autonomous permissions;
- bundle installs that overwrite unknown files;
- popularity scores presented as quality;
- "works everywhere" claims without adapter tests;
- giant skills that absorb unrelated responsibilities.
