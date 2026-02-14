# Devin AI -- Structural Pattern Analysis

**Date**: 2026-02-14
**Source**: Devin AI (Prompt.txt, DeepWiki Prompt.txt)

---

## 1. Autonomous Agent Planning: The Dual-Mode Loop

Devin uses a **two-phase execution model** with explicit mode transitions:

1. **Planning mode** -- gather information, explore codebase, search online, build understanding. No edits allowed. Ends with a `<suggest_plan/>` signal.
2. **Standard mode** -- execute the plan step-by-step. The system shows "current and possible next steps" from the plan.

The mode is set externally ("the user will indicate to you which mode you are in"), not self-selected.

**Structural Details:**
- Planning mode is **read-only by convention**: search, file viewing, LSP inspection, browsing -- but no edits
- Transition gated by a **dedicated command** (`<suggest_plan/>`), not implicit
- In standard mode, the agent sees a **windowed view** of the plan (current step + adjacent) rather than the full plan

**Skill system mapping:**
- Explicit phase gates prevent premature action -- skills could enforce "research phase before execution phase"
- Mode as external state means the orchestrator controls pacing, not the agent
- Windowed plan visibility prevents agents from getting distracted by future steps

---

## 2. Task Decomposition: Plan-Centric with Step Visibility

Plans are **location-aware**: the agent must enumerate all edit locations during planning, not discover them during execution. No hierarchical subtask nesting -- steps are sequential. The orchestrator manages "current step" externally.

**Skill system mapping:**
- Location-first planning: skills that modify code should enumerate all files/locations before touching any
- External plan tracking simplifies agent logic but requires a capable orchestrator
- Skills could declare a `plan_schema` (plan output format) and `step_executor` (per-step logic)

---

## 3. Tool Usage Patterns: Category-Grouped with Behavioral Constraints

Tools are organized into **seven named categories**, each with category-level behavioral rules:

1. **Reasoning** -- `<think>` scratchpad
2. **Shell** -- `<shell>`, `<view_shell>`, `<write_to_shell_process>`, `<kill_shell_process>`
3. **Editor** -- `<open_file>`, `<str_replace>`, `<create_file>`, `<undo_edit>`, `<insert>`, `<remove_str>`, `<find_and_edit>`
4. **Search** -- `<find_filecontent>`, `<find_filename>`, `<semantic_search>`
5. **LSP** -- `<go_to_definition>`, `<go_to_references>`, `<hover_symbol>`
6. **Browser** -- `<navigate_browser>`, `<view_browser>`, `<click_browser>`, `<type_browser>`, etc.
7. **Deployment** -- `<deploy_frontend>`, `<deploy_backend>`, `<expose_port>`

Each category has a **"When using X commands:"** block with behavioral rules -- not per-command but per-category.

**Tool exclusivity is strictly enforced:**
- Shell cannot be used for file operations (editor only)
- grep/find cannot be used (search commands only)
- Repeated 3 times across the prompt

**Skill system mapping:**
- Category-level rules are more maintainable than per-tool rules
- Tool exclusivity prevents workarounds -- enforce by not providing shell access when editor tools exist
- "When using X" pattern is a good template for skill `constraints` sections
- Parallel execution hints are explicit throughout: "output multiple commands without dependencies"

---

## 4. State Management: External Tracking with Think-Scratchpad

**Dual state model:**
1. **External state** (orchestrator): current mode, current plan step, shell process state per ID, browser tab state
2. **Internal state** (agent): the `<think>` scratchpad for reasoning (invisible to user)

### Think Command as Structured Checkpoint

10 specific situations where `<think>` is mandatory or recommended:

| Category | Trigger |
|----------|---------|
| Git safety | Before git/GitHub decisions |
| Transition gate | Before switching from reading to writing code |
| Completion verification | Before reporting "done" to user |
| Uncertainty | No clear next step |
| Detail clarity | Clear step but unclear details |
| Difficulty | Unexpected obstacles |
| Exhaustion | Multiple failed approaches |
| Critical decision | High-impact choice |
| Failure analysis | Tests/lint/CI failed |
| Environment triage | Possible setup issue |

**Skill system mapping:**
- Externalized state makes the agent stateless between turns -- replaceable/restartable
- Structured think triggers turn reflection into a systematic checkpoint system
- Named resource IDs (shell IDs, tab indices) are simple but effective state management
- Skills could include a `checkpoints` field listing when the agent should pause and reflect

---

## 5. Error Recovery: Escalation Ladder with Bounded Retries

**Layered error recovery:**

| Agent fixes | Agent escalates |
|-------------|----------------|
| Code bugs | Environment setup |
| Test failures (by fixing code) | Missing auth/credentials |
| Lint violations | Push conflicts |
| Reference updates | CI failures after 3 attempts |

**Key rules:**
- Never try to fix environment issues -- report immediately, use CI instead
- CI failures: try 3 times, then escalate
- Never modify tests unless explicitly asked (code-first blame)
- Never force push

**Skill system mapping:**
- Bounded retry counts prevent infinite loops -- `max_retries` parameter
- "Never fix environment" is a strong separation of concerns
- Report-and-continue is healthier than report-and-stop -- define `fallback_strategies`
- Code-first blame: mark certain files as `read_only` to enforce

---

## 6. Self-Verification: Multi-Point Checking

Three verification levels:

1. **Pre-completion reflection**: `<think>` is mandatory before reporting completion
2. **Tool-based verification**: Run lint, unit tests, other checks before submitting
3. **Reference completeness**: Verify all relevant locations were edited

**DeepWiki citation pattern** forces grounded reasoning:
- Every sentence must end with a citation tag linking to specific code lines (max 5 lines)
- If no evidence exists, output an empty cite tag
- Transforms verification from behavioral suggestion to structural output format requirement

**Skill system mapping:**
- Mandatory pre-completion think: skills could include `completion_checklist`
- Citation-forcing for analytical tasks: `evidence_format: citation`
- LSP as verification tool is underused -- type checking and reference finding catch real errors

---

## 7. Cross-Cutting Patterns

### Negative Instructions (Never-Do Lists)
Prohibitions are more heavily emphasized than positive instructions. The prompt assumes correct positive action but warns against common anti-patterns. Skills should support `constraints` or `never` fields.

### Parallel Execution as Default
Independent operations should always be batched. Appears across shell, search, LSP, and editor categories. Skills could signal which operations are safe to parallelize.

### Convention Matching Over Invention
"First understand the file's code conventions. Mimic code style." The agent should be a chameleon, not an innovator. Skills could require a `context_gathering` pre-step.

### The `find_and_edit` Delegation Pattern
One-to-many delegation within a single tool call: the agent describes a change in natural language, provides a regex, and a sub-agent handles each location independently. Multi-site refactoring delegated to specialized sub-agents with shared instructions but independent context.

---

## 8. What Devin Does NOT Have (Gorgon Advantages)

| Absent in Devin | Gorgon Has |
|-----------------|------------|
| No memory across sessions | Checkpoint/resume with SQLite |
| No multi-agent coordination | Triumvirate consensus |
| No explicit cost tracking | Token budget management |
| No skill/persona system | SKILL.md + schema.yaml modular loading |
| No task-level rollback | Checkpoint system enables step-N recovery |
| No self-modification | Potential for agent-created skills (gated) |

---

## 9. Summary: Key Takeaways for Gorgon

| Pattern | Value | Effort |
|---------|-------|--------|
| Dual-mode (plan/execute) with explicit gate | Prevents premature action | Medium |
| Location-first planning | Prevents incomplete edits | Low |
| Category-grouped tools with category-level rules | Cleaner tool governance | Medium |
| Structured think triggers (10 situations) | Targeted reflection | Low |
| Layered error escalation with bounded retries | Prevents infinite loops | Low |
| Mandatory pre-completion think | Catches incomplete work | Low |
| Citation-forced grounding | Prevents hallucinated analysis | Medium |
| Negative constraints (never-do lists) | Prevents anti-patterns | Low |
| Parallel-by-default execution hints | Reduces latency | Low |
| find_and_edit delegation | Efficient multi-site refactoring | High |
| Convention matching pre-step | Reduces code style drift | Low |
