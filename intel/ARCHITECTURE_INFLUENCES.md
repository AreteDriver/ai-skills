# Architecture Influences

How structural patterns from five AI system prompts shaped the v2 skill format.

**Date**: 2026-02-14
**Scope**: SKILL.md v2 template, schema.yaml v2 template, all 54 skill retrofits

## Pattern Adoption Matrix

| v2 Feature | Source | Priority | Where Implemented |
|---|---|---|---|
| `intent` input field | Cursor (`explanation` param) | High | schema.yaml inputs |
| Negative routing (`do_not_use_when`) | Cursor, Claude Code | High | SKILL.md + schema.yaml routing |
| `parallel_safe` flag per capability | Cursor, Antigravity (`waitForPreviousTools`) | Medium | SKILL.md capabilities + schema.yaml |
| `post_execution` guidance | Cursor (read_file completeness protocol) | Medium | schema.yaml capabilities |
| Escalation ladder with bounded retries | Devin (CI 3x rule), Cursor (linter 3x) | Medium | SKILL.md + schema.yaml error_handling |
| Self-correction rules | Cursor Sep 2025 (`<non_compliance>`) | Medium | SKILL.md + schema.yaml error_handling |
| Structured checkpoints | Devin (10 think-triggers) | Medium | SKILL.md verification + schema.yaml |
| Completion checklist | Devin (mandatory pre-completion think) | Medium | SKILL.md + schema.yaml verification |
| Tool restriction sets | Claude Code (per-agent tool access) | Medium | SKILL.md frontmatter `tools` |
| Safety tier per capability | Cursor (read-only/reversible/destructive/external) | High | schema.yaml risk + consensus |
| Inter-agent contracts | Manus (event stream typed events) | Medium | schema.yaml contracts |
| Trust levels | Antigravity (`// turbo` annotations) | Low | SKILL.md frontmatter `trust` |
| "What + When" descriptions | Manus (dual-sentence tool descriptions) | Low | schema.yaml capability descriptions |

## Detailed Influence Map

### From Cursor

**What we adopted:**

1. **Intent/explanation field** — Cursor requires an `explanation: string` on nearly every tool call. We adopted this as the `intent` input on every agent schema. Forces agents to articulate purpose before execution, making logs auditable.

2. **Negative routing examples** — Cursor's tool descriptions include "When NOT to Use" sections with reasoning and alternatives. We elevated this to a first-class section in both SKILL.md (`## When NOT to Use`) and schema.yaml (`routing.do_not_use_when` with `condition`/`instead`/`reason` structure).

3. **Post-execution protocols** — Cursor's `read_file` has a 4-step completeness protocol embedded in the description. We formalized this as `post_execution` arrays on every capability in schema.yaml. Defines what to DO with results, not just the return shape.

4. **Circuit breakers** — Cursor's "DO NOT loop more than 3 times on fixing linter errors" became our `max_retries` field per error class in the escalation ladder.

5. **Self-correction** — Cursor Sep 2025 introduced `<non_compliance>` patterns for protocol violations. We adopted this as `self_correction` arrays in both SKILL.md and schema.yaml error_handling sections.

**What we didn't adopt:**

- `multi_tool_use.parallel` wrapper tool — We use `parallel_safe` flags instead of a meta-tool. The flag approach is simpler for a skill system where the orchestrator decides parallelism.
- Return type `any` — We explicitly define typed outputs per capability. This is a deliberate improvement over Cursor's untyped returns.

### From Devin

**What we adopted:**

1. **Structured think-triggers** — Devin lists 10 specific situations requiring `<think>` (git decisions, mode transitions, completion, uncertainty, etc.). We adopted this as `verification.checkpoints` with trigger/action pairs. Transforms vague "think when needed" into specific situations.

2. **Mandatory pre-completion checklist** — Devin requires `<think>` before reporting completion. We formalized this as `verification.completion_checklist` — a mandatory review before any skill reports done.

3. **Escalation ladder** — Devin's layered error recovery (agent fixes code bugs, escalates environment issues, 3x CI retry limit) became our `error_handling.escalation` with typed error classes, actions, max_retries, and fallbacks.

4. **Location-first planning** — Devin requires enumerating all edit locations during planning. We adopted this as `files_affected` and `interfaces_affected` in analysis skills like intent-author.

**What we didn't adopt:**

- Dual-mode (plan/execute) phase gates — Our skills operate within Gorgon's existing workflow phases rather than imposing their own mode system. The WHY/WHAT/HOW framework already provides phase separation.
- External state management — Devin externalizes all state to the orchestrator. Our skills carry their own state via checkpoint DBs and schema contracts.
- `find_and_edit` delegation — Single-tool multi-site refactoring is powerful but requires tool-level support we don't have. Noted for future consideration.

### From Claude Code

**What we adopted:**

1. **Tool restriction sets per agent** — Claude Code's sub-agent registry restricts tool access by type (`statusline-setup` gets only `Read, Edit`). We adopted this as the `tools` frontmatter field, listing allowed tools per skill.

2. **CAN/CANNOT boundaries** — Claude Code's negative examples for when NOT to use sub-agents (don't delegate reading a known file path). We merged this with Cursor's negative routing into our `do_not_use_when` pattern.

3. **Parallel execution declarations** — Claude Code's explicit "MUST send a single message with multiple Task tool use content blocks." We formalized this as `parallel_safe: true/false` on capabilities.

**What we didn't adopt:**

- System-reminder injection — Claude Code injects `<system-reminder>` tags for ambient context. Our skill loading is explicit (skill referenced in workflow definition), not ambient injection.
- SlashCommand invocation — Interesting for Claude Code's CLI context, but our skills are invoked through Gorgon's workflow engine, not slash commands.

### From Manus

**What we adopted:**

1. **Inter-agent contracts** — Manus's typed event stream (Message, Action, Observation, Plan, Knowledge, Datasource) showed that inter-component communication needs typed boundaries. We formalized this as `contracts.provides` (what a skill outputs with consumer list) and `contracts.requires` (what it needs with provider name) in schema.yaml.

2. **"What + When" dual descriptions** — Manus's tool descriptions use "What it does. Use for [when]." We adopted this for capability descriptions: each includes what it does, when to use it, and when NOT to use it.

3. **Graduated error reasoning** — Manus's verify-fix-pivot-escalate pattern influenced our escalation ladder progression: retry → report → escalate → stop.

**What we didn't adopt:**

- Single-tool-per-iteration constraint — Manus executes exactly one tool per loop cycle for observability. Our skills support parallel execution through `parallel_safe` flags because Gorgon's orchestrator can handle concurrent operations.
- Module injection pattern — Manus uses read-only advisor modules injecting into an event stream. Our skills are active agents with tool access, not passive advisors.
- `idle` sentinel tool — Explicit completion signaling is handled by Gorgon's checkpoint system, not a dedicated tool.

### From Antigravity (Google DeepMind)

**What we adopted:**

1. **Trust levels** — Antigravity's `// turbo` (auto-run one step) and `// turbo-all` (auto-run everything) mapped directly to our `trust: supervised | autonomous` frontmatter field. The workflow author declares trust at definition time.

2. **Three-phase execution** — Antigravity's PLANNING → EXECUTION → VERIFICATION phases influenced our verification section structure. `pre_conditions` map to planning gates, `post_conditions` to execution verification, `completion_checklist` to the verification phase.

3. **Complexity as review signal** — Antigravity's 1-10 complexity rating influenced our `risk_level` field. Higher risk gets more consensus requirements (any → majority → unanimous → unanimous+user).

**What we didn't adopt:**

- YAML-frontmatter-only workflow format — Antigravity's workflows are just `description` + freeform markdown. We kept our structured WHY/WHAT/HOW framework with typed schemas because machine-parseability matters for Gorgon's orchestrator.
- Agent self-extension (creating new workflows) — Antigravity lets agents create new `.md` workflow files. We require human authorship for skills to prevent uncontrolled proliferation.
- Knowledge Item (KI) system — Per-skill persistent learning is interesting but adds complexity. Noted for future consideration.

## Cross-Cutting Patterns

Three patterns appeared independently in 3+ systems:

### 1. Negative Examples Are as Valuable as Positive Examples

- **Cursor**: "When NOT to Use" with 3 negative examples per tool
- **Claude Code**: "Do NOT use for reading a specific known file path"
- **Devin**: "Never try to fix environment issues"
- **Manus**: Tool priority hierarchy (prefer X over Y)

**Our implementation**: Every SKILL.md has `## When NOT to Use` with alternatives and reasoning. Every schema.yaml has `routing.do_not_use_when` with structured `condition`/`instead`/`reason` entries. Every capability description includes "Do NOT use when [scenario]."

### 2. Parallel Execution Needs Both Structure AND Behavior

- **Cursor**: `multi_tool_use.parallel` wrapper + `<maximize_parallel_tool_calls>` behavioral section
- **Claude Code**: "MUST send a single message with multiple Task tool use content blocks"
- **Antigravity**: `waitForPreviousTools` per-tool dependency declaration
- **Devin**: "output multiple commands without dependencies"

**Our implementation**: `parallel_safe: true/false` on every capability (structural) + post_execution guidance on when parallel is appropriate (behavioral). The orchestrator reads the flags; the agent reads the guidance.

### 3. Bounded Retries Prevent Infinite Loops

- **Cursor**: "DO NOT loop more than 3 times" (linter)
- **Devin**: "CI failures: try 3 times, then escalate"
- **Manus**: "Attempt fix, try alternative, then report to user"

**Our implementation**: `error_handling.escalation` with `max_retries` per error class. Different error types get different retry budgets (recoverable: 3, environment: 0, permission: 0).

## What No System Addresses (Future Opportunities)

| Gap | Description | Potential Approach |
|---|---|---|
| Output schema validation | All 5 systems return untyped or loosely typed results | Our schema.yaml defines typed outputs per capability — enforce at runtime |
| Skill composition | No system has one skill formally invoking another | `contracts.requires` names a provider — could become runtime dependency injection |
| Resource budgets per invocation | Only Gorgon has token budget management | Extend schema.yaml with `budget` field per capability |
| Observability / tracing | No structured execution traces across skills | Add `trace_id` propagation through contracts |
| Skill versioning contracts | No system handles breaking changes between skill versions | semver on schemas + consumer compatibility checks |

## What ai-skills Already Did Better Than All 5 Sources

1. **Typed input/output schemas** — All 5 sources use untyped or loosely typed tool returns. Our schema.yaml defines typed inputs AND outputs per capability.
2. **Risk + consensus model** — Per-capability risk levels with graduated consensus requirements. No other system has this granularity.
3. **WHY/WHAT/HOW workflow framework** — Structured intent capture at the workflow level. Manus has numbered pseudocode; we have a typed framework.
4. **Protected paths / deny lists** — Explicit path-level deny lists in schema.yaml. Other systems use behavioral "never" instructions.
5. **Quality gates** — After-step checkpoints with `on_failure` semantics in workflow schemas. Other systems rely on behavioral instructions.

## File Reference

| File | Purpose |
|---|---|
| `intel/claude_code_subagent_patterns.md` | Full analysis of Claude Code patterns |
| `intel/cursor_tool_definition_patterns.md` | Full analysis of Cursor patterns |
| `intel/devin_planning_patterns.md` | Full analysis of Devin patterns |
| `intel/manus_orchestration_patterns.md` | Full analysis of Manus patterns |
| `intel/antigravity_workflow_patterns.md` | Full analysis of Antigravity patterns |
| `intel/SOURCES.md` | Source attribution and legal framework |
| `templates/skill-template-v2.md` | v2 SKILL.md template with inline pattern citations |
| `templates/schema-template-v2.yaml` | v2 schema.yaml template with inline pattern citations |
