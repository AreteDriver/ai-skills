# Claude Code Structural Patterns Analysis

**Date**: 2026-02-14
**Source**: Anthropic/Claude Code (Prompt.txt, Tools.json, Claude Code 2.0.txt)

---

## 1. Sub-Agent Decomposition: Typed Agent Registry

The Task tool defines sub-agents as a registry of typed agents, each with:
- **name** (string identifier): `general-purpose`, `statusline-setup`, `output-style-setup`
- **description** (natural language): what the agent does and when to use it
- **tool access list**: explicit enumeration of available tools per agent type
  - `general-purpose` gets `*` (all tools)
  - Specialized agents get restricted sets: `Read, Edit` or `Read, Write, Edit, Glob, Grep`

### Structural Fields

```
subagent_type: string      # Agent type selector (required)
description: string        # 3-5 word task summary (required)
prompt: string             # Full task brief (required)
```

### CAN/CANNOT Boundaries

Negative examples (when NOT to use sub-agents):
- Do NOT use for reading a specific known file path
- Do NOT use for searching a specific class definition
- Do NOT use for searching within 2-3 known files
- Sub-agents are for open-ended, multi-step exploration; direct tools for deterministic single-step operations

**Skill system mapping**: Tool restrictions per agent type prevent privilege escalation. A `statusline-setup` agent cannot run Bash commands. Skills should define allowed tool sets.

**Gap**: No input/output schema validation on agent results. No retry/error-handling semantics. No timeout per invocation. Sub-agent returns free-text.

---

## 2. Tool Definition Schema: JSON Schema 7 + Behavioral Descriptions

Each tool has two distinct layers:
1. **Input schema** -- Standard JSON Schema draft-07 with `additionalProperties: false`
2. **Description** -- Dense natural-language behavioral instructions

### Key Schema Patterns

| Pattern | Example | Purpose |
|---------|---------|---------|
| Enum constraints | `output_mode: enum [content, files_with_matches, count]` | Restrict valid operations |
| Default values | `replace_all: {default: false}` | Safe defaults |
| Format validators | `url: {format: "uri"}` | Input validation at schema level |
| minLength | `query: {minLength: 2}` | Prevent degenerate inputs |
| minItems | `edits: {minItems: 1}` | Prevent no-op calls |
| Nested objects | MultiEdit's `edits` array | Compose operations atomically |

### Behavioral Description Conventions

Tool descriptions contain:
- **Usage rules** (MUST/NEVER/IMPORTANT directives)
- **When-to-use heuristics** (prefer X over Y)
- **Safety constraints** (never run destructive commands)
- **Cross-tool routing** (use Grep not bash grep, use Read not cat)
- **Examples** (good/bad pairs)
- **Workflow templates** (multi-step git commit procedure embedded in Bash description)

**Key insight**: Complex workflows (git commit, PR creation) are embedded as multi-step procedures in tool descriptions rather than separate workflow definitions.

**Gap**: No output schema. Tools define inputs rigorously but outputs are untyped.

---

## 3. Task Delegation: Complexity-Based Routing

### Decision Heuristic

```
IF task matches specialized agent description -> delegate (Task tool)
ELIF searching for unknown location -> delegate (general-purpose agent)
ELIF reading specific known file -> Read tool directly
ELIF searching specific 2-3 files -> Read tool directly
ELIF searching for class/function name -> Glob tool directly
ELSE -> handle with direct tools
```

### v2.0 Additions

- Explicit parallel agent launching: "MUST send a single message with multiple Task tool use content blocks"
- Proactive agent use: "If the agent description mentions proactive use, try to use it without user asking"

**Skill system mapping**: Skills need metadata that enables routing decisions -- complexity hints, confidence requirements, proactive-use flags. Negative routing examples prevent over-delegation.

---

## 4. Skill/Capability Loading: Lazy Injection

Context is loaded via `<system-reminder>` tags injected into tool results and user messages:

- Tags appear inline in conversation, not as separate system messages
- Explicitly marked as potentially irrelevant: "this context may or may not be relevant"
- Sources: CLAUDE.md files, memory files, git status, environment info
- Injection is automatic -- system decides when to inject

### v2.0: SlashCommand Tool

Named commands invoked within conversation:
- Available commands listed dynamically per session
- Commands take arguments: `/review-pr 123`
- Guard against re-invocation of same command

**Skill system mapping**: Lazy loading via injection prevents context bloat. Skills should define injection trigger conditions and relevance scope. SlashCommand provides typed invocation interface.

---

## 5. Safety/Permission Model: Defense in Depth

Four layers of safety enforcement:

| Layer | Scope | Mechanism |
|-------|-------|-----------|
| Global behavioral | System-wide | Defensive security only, never hardcode credentials |
| Tool-level | Per tool | NEVER directives in descriptions (no force push, read before edit) |
| Operation-specific | Per workflow | Multi-step protocols (git commit: status+diff+log -> analyze -> stage+commit+verify) |
| v2.0 escalation | Per action | Authorship check before amend, secret file detection |

**Comparison to ai-skills**: The existing `schema.yaml` per-capability risk/consensus model is more structurally rigorous than Claude Code's prose-based safety. Claude Code implements defense-in-depth through overlapping behavioral instructions; ai-skills has typed risk levels.

---

## 6. System-Reminder Injection Pattern

### Structural Properties

```xml
<system-reminder>
  {context content}
  IMPORTANT: this context may or may not be relevant to your tasks.
</system-reminder>
```

- **Non-authoritative**: Agent may ignore irrelevant reminders
- **Additive**: Never remove or contradict prior instructions
- **Ambient**: Injected without agent request
- **Provenance-marked**: "automatically added by the system" prevents prompt injection

### v1 -> v2 Evolution

v1: "NOT part of the user's provided input or the tool result"
v2: "bear no direct relation to the specific tool results or user messages" (stronger decoupling)

**Skill system mapping**: Skills should define how their context gets injected -- trigger conditions, relevance scope, provenance markers. XML tags provide structured parsing boundaries.

---

## 7. Verification Loops: Multi-Phase with Parallel Checks

Three levels of verification:

### Task-Level (TodoWrite)
- States: `pending`, `in_progress`, `completed`
- v2.0 adds `activeForm` for present-continuous display ("Fixing authentication bug")
- Single in-progress constraint prevents context-switching without completion

### Operation-Level (Git Workflows)
- Git commit: status+diff+log (parallel) -> analyze -> stage+commit+status (parallel)
- PR creation: status+diff+remote+log (parallel) -> analyze -> branch+push+create (parallel)
- Post-commit hook handling: retry once, check modifications, verify authorship

### Code-Level (Lint/Test)
- Verification commands discovered from project, not hardcoded
- Suggestion to write discovered commands to CLAUDE.md for future sessions

**Skill system mapping**: Skills need pre-conditions, acceptance criteria, and post-conditions. The ai-skills workflow-schema already defines these. The activeForm dual-form pattern (imperative + continuous) is worth adopting for status display.

---

## 8. Cross-Cutting Patterns

### Parallel Execution
Both v1 and v2 emphasize parallel tool calls. Sub-agents should be launched concurrently when independent. Steps should declare independence for parallel scheduling.

### Token Economy
- "Minimize output tokens"
- Sub-agent delegation is partly a context management strategy -- keeps search results out of main context
- "Fewer than 4 lines" default response length

### Convention Discovery Over Prescription
- Never assume libraries are available
- Check existing codebase usage first
- Skills should discover project conventions rather than assuming them

### Edit-Over-Create Principle
- Always prefer editing existing files
- Never write new files unless required
- Never proactively create documentation

---

## 9. v1 to v2 Key Changes

| Dimension | v1 | v2 |
|-----------|----|----|
| Identity | "interactive CLI tool" | "Claude agent, built on Claude Agent SDK" |
| Git safety | Basic "never force push" | Full authorship check before amend |
| TodoWrite | id field, no activeForm | activeForm field, no id field |
| SlashCommand | Not present | New tool for skill invocation |
| System-reminder | "NOT part of input" | "no direct relation" (stronger decoupling) |
| Parallel agents | Implicit | Explicit "MUST" with user-trigger |

---

## 10. Summary: Key Takeaways for Gorgon

### What ai-skills Already Does Better

1. **Typed schemas** (schema.yaml) with inputs/outputs -- more rigorous than untyped tool outputs
2. **Risk + consensus model** -- per-capability risk levels with consensus requirements
3. **WHY/WHAT/HOW workflow framework** -- structured intent capture
4. **Protected paths** -- explicit deny-lists
5. **Quality gates** -- after_step checkpoints with on_failure semantics

### What to Adopt from Claude Code

| Pattern | Priority | Effort |
|---------|----------|--------|
| Tool restriction sets per agent type | High | Medium |
| Negative routing examples (when NOT to use) | High | Low |
| Parallel execution declarations | Medium | Low |
| System-reminder injection pattern | Medium | Medium |
| Convention discovery over prescription | Medium | Low |
| SlashCommand invocation interface | Medium | Medium |
| activeForm dual-form status display | Low | Low |

### Gaps Neither System Addresses

1. Output schema contracts for sub-agent results
2. Structured retry policies
3. Agent-to-agent communication (beyond fire-and-forget)
4. Skill composition (one skill invoking another)
5. Resource budgets per invocation (Gorgon has this -- advantage)
6. Observability / structured tracing of skill execution
