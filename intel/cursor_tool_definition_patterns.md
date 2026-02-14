# Cursor Agent Structural Patterns Analysis

**Date**: 2026-02-14
**Source**: Cursor Prompts (Chat through Agent v2.0 + CLI, Sep 2025)

---

## 1. Tool Definition Schema

### Two Parallel Formats

**Format A: TypeScript-flavored namespace (inline in system prompt)**

Used in Agent v1.2 and v2.0. Tools defined as TypeScript type signatures inside a `namespace functions {}` block:

```
namespace functions {
  // Description with ### sections, examples, anti-patterns
  type tool_name = (_: {
    // Per-field doc comment
    field_name: type,
    optional_field?: type,
  }) => any;
}
```

**Format B: Standard JSON Schema (separate file)**

Used in Agent Tools v1.0.json. Standard `{ name, description, parameters: { properties, required } }` objects.

### Key Fields Per Tool

| Field | Purpose | Notes |
|-------|---------|-------|
| `name` | Tool identifier | snake_case, verb-noun pattern |
| `description` | Rich behavioral documentation | Includes WHEN to use, WHEN NOT to use, examples, strategy |
| `explanation` | Per-call intent field | Agent must state WHY it is calling this tool |
| `parameters.properties` | Typed fields with descriptions | Standard JSON Schema types |
| `parameters.required` | Mandatory fields | Explicitly enumerated |

### The `explanation` Field

Nearly every Cursor tool requires an `explanation: string` parameter -- a one-sentence justification for WHY the tool is being invoked. Forces the agent to reason about intent before acting. Lightweight chain-of-thought at the parameter level.

**Skill system mapping**: Add an `explanation` or `intent` field to action schemas. Makes logs auditable and reduces hallucinated tool calls.

### Negative Examples in Descriptions

Tool descriptions include explicit "When NOT to Use" sections with reasoning. The `codebase_search` tool has 5 positive examples and 3 negative examples, each with reasoning.

**Skill system mapping**: Skill descriptions should include anti-patterns. "Do NOT use this skill for X" is as valuable as "Use this skill for Y."

---

## 2. Parallel Execution Pattern

### The `multi_tool_use.parallel` Wrapper

A dedicated meta-tool wraps concurrent invocations:

```
namespace multi_tool_use {
  type parallel = (_: {
    tool_uses: {
      recipient_name: string,
      parameters: object,
    }[],
  }) => any;
}
```

### Behavioral Reinforcement

The structural definition alone is insufficient. A `<maximize_parallel_tool_calls>` section adds:

1. Explicit rule: "DEFAULT TO PARALLEL"
2. Concrete examples of what should be parallel
3. Only valid exception: "output of A required for input of B"
4. Quantified benefit: "3-5x faster than sequential"
5. Framed as expected behavior, not optimization

This section is **identical across v1.0, v1.2, v2.0, and CLI** -- the most stable part of the prompt.

**v2.0 addition**: "Limit to 3-5 tool calls at a time or they might time out" (capacity constraint).

**Skill system mapping**: Parallel execution needs BOTH structural support (wrapper/flag) AND behavioral instruction. Define `parallel_safe: true/false` on each action.

---

## 3. Search Strategy Guidance

### Embedded Decision Tree

Tool descriptions embed complete decision trees:

1. **When to use**: Explore unfamiliar code, find by meaning
2. **When NOT to use**: Exact matches (use grep), known files (use read_file), symbol lookups (use grep)
3. **Search strategy**: Broad query -> review results -> narrow to directory -> narrow to file
4. **Anti-patterns**: Single-word queries, combined multi-part queries

### Environment-Adaptive Tool Selection

IDE prefers semantic search; CLI prefers grep. The same agent uses different primary tools based on available affordances.

**Skill system mapping**: Include `tool_selection_guidance` with environment-specific conditions. A `preferred_tools` field that adapts to available capabilities.

---

## 4. Output Schema Rigor

All Cursor tools return `=> any`. No structured return types. Cursor compensates with **behavioral post-execution protocols** embedded in descriptions.

### The `read_file` Completeness Protocol

A 4-step protocol in the tool description:
1. Assess if contents are sufficient
2. Note where lines are not shown
3. If insufficient, call again for more lines
4. When in doubt, call again

**Skill system mapping**: What to DO with results matters more than the return type shape. Add `post_execution_protocol` or `result_handling` fields to action schemas.

---

## 5. Parameter Validation

### Observed Validation Patterns

| Pattern | Example | Tool |
|---------|---------|------|
| Enum/union types | `"content" \| "files_with_matches" \| "count"` | grep output_mode |
| Boolean flags | `is_background: boolean` | run_terminal_cmd |
| Integer types | `start_line_one_indexed: integer` | read_file |
| Array items typing | `items: { type: "string" }` | target_directories |
| MinItems constraint | `minItems: 2` | todo_write todos |
| Conditional required | "Required if action is 'update' or 'delete'" | update_memory |

### Notably Absent

- No regex pattern validation on string fields
- No min/max on numeric fields
- No URI/URL format validation
- No complex conditional schemas (if/then in prose, not JSON Schema)

### Prose Over Schema

Critical constraints live in descriptions, not validators:
- "The old_string MUST uniquely identify the specific instance"
- "Include AT LEAST 3-5 lines of context BEFORE the change point"

**Skill system mapping**: Don't over-invest in JSON Schema validation. Use schema for type safety (enums, required, basic types). Use prose for usage contracts.

---

## 6. Risk/Safety Instructions

### Safety Tier System

| Tier | Operations | Mechanism |
|------|-----------|-----------|
| Read-only | search, read | No approval needed |
| Reversible writes | edit file, create file | Auto-approved with guards |
| Destructive | delete, terminal commands | PROPOSE-then-APPROVE |
| External side effects | deployments, API calls | Explicit approval |

### Built-in Circuit Breakers

- **Linter loop breaker**: "DO NOT loop more than 3 times on fixing linter errors. Stop and ask the user."
- **Stale file guard**: "If you haven't read a file within your last 5 messages, read it again before editing."
- **Graceful failure**: `delete_file` explicitly states operation will fail gracefully for missing files, security rejections, undeletable files.

**Skill system mapping**: Define safety tiers per capability. Add circuit breakers: `max_retries`, recency checks, scope limits.

---

## 7. Self-Correction (Sep 2025)

### The `<non_compliance>` Pattern

The latest version introduces self-repair:
- If you fail to check off tasks before claiming done: self-correct next turn
- If you used tools without a status update: self-correct next turn
- If you report work done without tests: self-correct by running tests first

**Skill system mapping**: Agent definitions should include `compliance_rules` -- not just "what to do" but "what to do when you fail to do what you should."

---

## 8. Prompt Architecture Evolution

### Section Stability Across 6 Versions

| Section | Stability | Notes |
|---------|-----------|-------|
| `<communication>` | Stable across all | Core identity/tone |
| `<tool_calling>` | Stable across all | Tool usage rules |
| `<making_code_changes>` | Stable across all | Code modification rules |
| `<maximize_parallel_tool_calls>` | Stable since v1.0 | Most stable behavioral section |
| `<search_and_reading>` | Evolving | Renamed, condensed over time |
| `<task_management>` | Experimental | Added v1.2, evolved through Sep 2025 |
| `<memories>` | Dropped | Appeared in v1.2 only |
| `<non_compliance>` | New (Sep 2025) | Self-correction mechanism |

### Key Trends

1. **Chat -> Agent**: Added autonomy, parallel execution, todo management
2. **v1.0 -> v1.2**: Added memory system, richer descriptions, task dependencies
3. **v1.2 -> v2.0**: Dropped memory, dropped dependencies -- experimental features that didn't stick
4. **IDE -> CLI**: Different tool preferences, more process-oriented sections
5. **Sep 2025**: Self-correction, completion spec, linter guidance -- most structured version

---

## 9. Summary: Key Takeaways for Gorgon

| Pattern | Priority | Effort |
|---------|----------|--------|
| Explanation/intent field on every tool call | High | Low |
| Negative examples with reasoning in descriptions | High | Low |
| Safety tier classification per action | High | Medium |
| Parallel-safe flag on tools/actions | Medium | Low |
| Post-execution protocols for result handling | Medium | Low |
| Circuit breakers (max retries, recency checks) | Medium | Low |
| Self-correction rules for protocol violations | Medium | Medium |
| Tool selection hierarchy with conditions | Medium | Medium |
| Behavioral validation in prose, not just schema | Medium | Low |
| Context disposition (thorough/targeted/minimal) | Low | Low |

### Anti-Patterns Observed

1. **Return type `any`**: All tools return untyped. A skill system could do better with lightweight result schemas.
2. **Duplicate instructions**: "Follow tool call schema exactly" repeated 3+ times. DRY applies to prompts too.
3. **Version drift**: Features appear and disappear across versions (memory, dependencies). Indicates experimental churn.
