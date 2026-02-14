# Antigravity (Google DeepMind) -- Structural Pattern Analysis

**Date**: 2026-02-14
**Source**: Google/Antigravity (Fast Prompt.txt, planning-mode.txt)

---

## 1. Workflow Definition Format: YAML Frontmatter + Markdown Steps

Workflows live at `.agent/workflows/*.md` and follow a minimal schema:

```
---
description: [short title]
---
[numbered steps in markdown]
```

**Key characteristics:**
- Single YAML frontmatter field: `description` (one-liner)
- Body is freeform markdown -- ordered list of steps
- No explicit schema for step metadata (inputs, outputs, expected results)
- Filename doubles as the slash command name: `.agent/workflows/deploy.md` -> `/deploy`

**Trade-off**: Maximum flexibility (any human can write a workflow), minimum machine-parseability (no way to validate steps, detect dependencies, or auto-parallelize).

**Skill system mapping**: Preserve this simplicity as the authoring format while adding optional structured metadata (inputs, outputs, preconditions, postconditions) as YAML frontmatter fields.

---

## 2. Turbo Annotations: Per-Step and Global Auto-Run Control

Two annotation levels control whether the agent needs user approval:

| Annotation | Scope | Trust Level | Consensus Mapping |
|-----------|-------|-------------|-------------------|
| (none) | per-step default | Requires user approval | `unanimous + user` |
| `// turbo` | single step | Auto-run this step only | `any` for one action |
| `// turbo-all` | entire workflow | Auto-run everything | Blanket `any` delegation |

**Key insight**: Trust is **authored by the workflow writer** and baked into the definition -- a **static consent model**. The person who defines the workflow declares which steps are safe to auto-execute.

**Enhancement opportunity**: Add a third tier distinguishing read-only operations from write operations. The current model does not distinguish between destructive and non-destructive commands.

---

## 3. Planning Mode: Structured Phase Separation

Three-phase execution model via `task_boundary` calls:

| Phase | Purpose | Artifact |
|-------|---------|----------|
| PLANNING | Research, requirements, design approach | `implementation_plan.md` |
| EXECUTION | Write code, implement design | Source files |
| VERIFICATION | Test, validate correctness | `walkthrough.md` |

**Phase transition rules:**
- Always start with PLANNING for new requests
- Can skip to EXECUTION if planning already approved
- Can regress from EXECUTION back to PLANNING if unexpected complexity discovered
- Minor issues in VERIFICATION stay in same task, switch to EXECUTION
- Fundamental design flaws in VERIFICATION trigger return to PLANNING with new task

**State machine:**
```
PLANNING --[approval]--> EXECUTION --[tests pass]--> VERIFICATION
    ^                        |                           |
    |    [unexpected complexity]                  [design flaw]
    +------------------------+---------------------------+
```

**Key design decisions:**
1. Planning produces a **reviewable artifact** that must be approved before execution -- human-in-the-loop gate
2. `TaskStatus` is explicitly **forward-looking** -- describes intent, not history
3. Phase regression is allowed -- the agent can escalate when it discovers it cannot complete

**Skill system mapping:**
- Each skill invocation could follow this three-phase pattern
- Plan output = reviewable artifact before execution
- Walkthrough output = evidence/proof artifact after completion
- Phase regression maps to skill's ability to escalate

---

## 4. Tool Metadata and Dependency Declarations

Tools carry structured metadata beyond basic parameters:

| Field | Purpose |
|-------|---------|
| `Complexity` | 1-10 review importance rating -- drives UI attention |
| `Description` | User-facing explanation (brief, plain language) |
| `Instruction` | Agent-facing explanation (technical detail) |
| `SafeToAutoRun` | Trust flag (boolean, controlled by turbo annotations) |
| `waitForPreviousTools` | Dependency declaration -- sequential vs parallel |
| `ArtifactMetadata` | Typed output classification |
| `TargetLintErrorIds` | Traceability to specific problems |

**Patterns worth extracting:**

1. **Dual description fields** (Description + Instruction): Separating user-facing from agent-facing allows the same action described at two levels. Skill system could use `summary` (humans) and `instruction` (agents).

2. **Complexity as review signal**: The 1-10 rating is a **soft attention mechanism** -- higher complexity gets more user scrutiny. Skills could use this to determine which outputs need human review.

3. **Inline dependency declarations** (`waitForPreviousTools`): Each operation declares its own sequencing needs rather than a DAG upfront. Simpler than a full dependency graph but less optimizable.

---

## 5. Agent Instruction Format: Layered Sections

The system prompt uses XML-tagged sections for distinct instruction domains, revealing a **layered instruction architecture**:

| Layer | Mutability |
|-------|------------|
| Identity | Fixed by system |
| Environment | Set per session |
| Capabilities | Set per workspace |
| Behavior | Fixed by system |
| Domain | Fixed by system |
| User rules | User-controlled |

**Skill system mapping**: Skill definitions (identity + capabilities) should be distinct from execution environment (workspace + tools) and behavioral constraints (communication + modes).

---

## 6. File-Based Workflow Discovery

Discovery is a two-step process:

| Method | Trigger | Lookup |
|--------|---------|--------|
| Explicit | `/slash-command` | Exact filename match |
| Implicit | User request | Semantic match on descriptions |
| Creation | "Create a workflow for X" | Agent writes new `.md` file |

**Key insight**: The registry is **mutable by the agent itself** -- the agent can create new workflows. Powerful but dangerous. Self-extension should be gated behind a trust level.

---

## 7. Knowledge Item (KI) System: Persistent Learning

A **structured memory layer** at `~/.gemini/<project>/knowledge/`:

```
knowledge/
  topic-name/
    metadata.json     -- summary, timestamps, source references
    artifacts/        -- related files, documentation
```

**Usage rules (strictly enforced):**
1. Check KI summaries **before any research** (mandatory first step)
2. Read KI artifacts before doing independent investigation
3. Build upon existing KIs rather than starting fresh
4. KIs are starting points, not ground truth -- always verify

**Skill system mapping:**
- Skills could have associated KIs capturing learned patterns
- Per-skill knowledge directory accumulates domain-specific knowledge across invocations
- "Check KIs first" mandate maps to skill loading context before execution

---

## 8. Summary: Key Takeaways for Gorgon

| Pattern | Antigravity | Gorgon Mapping |
|---------|-------------|----------------|
| Workflow format | YAML frontmatter + markdown | Already using SKILL.md with frontmatter |
| Trust/consent | `// turbo` annotations | Step-level trust flags in schema.yaml |
| Phase separation | PLANNING/EXECUTION/VERIFICATION | Skill execution phases with gate checks |
| Dual descriptions | Description (user) + Instruction (agent) | Add `summary` + `instruction` fields |
| Complexity rating | 1-10 per tool call | Review-attention signals on skill outputs |
| Discovery | Filesystem + semantic matching | Registry with slash commands + fuzzy lookup |
| Self-extension | Agent creates new workflows | Gated skill creation capability |
| Persistent knowledge | KI system with metadata + artifacts | Per-skill knowledge accumulation |
| Dependency declaration | `waitForPreviousTools` per call | Add `parallel: true/false` to capabilities |
| Forward-looking status | Describes intent, not history | Agent declares next action |

### Key Differentiator: Fast Mode vs Planning Mode

The same agent operates under different instruction sets depending on task complexity. This confirms a **modal agent architecture** -- Gorgon could offer lightweight (direct execution) and heavyweight (consensus-gated) modes per skill invocation based on risk level.
