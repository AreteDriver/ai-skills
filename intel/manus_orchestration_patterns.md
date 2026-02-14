# Manus Agent System -- Structural Pattern Analysis

**Date**: 2026-02-14
**Source**: Manus Agent Tools & Prompt (Prompt.txt, tools.json, Modules.txt, Agent loop.txt)

---

## 1. Multi-Agent Orchestration: The Module Injection Pattern

Manus does **not** use a peer-to-peer multi-agent model. Instead, it uses a **single-agent core with injected module advisors**. The architecture has one execution agent ("Manus") that receives guidance from three system-level modules:

| Module | Role | Injection Mechanism |
|--------|------|---------------------|
| **Planner** | Decomposes tasks into numbered pseudocode steps | Injects `Plan` events into the event stream |
| **Knowledge** | Provides scoped best-practice references | Injects `Knowledge` events into the event stream |
| **Datasource** | Supplies API documentation for authorized data sources | Injects `Datasource` events into the event stream |

**Structural Pattern**: There is no agent-to-agent handoff. The orchestration is **event-stream-mediated**: modules write advisory events into a shared chronological stream, and the single executing agent reads from that stream to decide its next action. The agent never calls another agent -- it only calls tools.

**Why this matters**: This avoids the complexity of inter-agent negotiation, routing, and state synchronization. The "multi-agent" behavior is simulated by having specialized modules inject context at the right time. The executing agent treats module outputs the same way it treats user messages and tool results -- as events in a timeline.

**Key difference from naive approaches**: A simple "agent A calls agent B" delegation model requires explicit handoff protocols, return contracts, and error propagation. Manus sidesteps all of this by making modules non-interactive advisors. They push context; they never pull or block.

---

## 2. Inter-Agent Communication: The Event Stream Contract

The central data structure is the **event stream** -- a chronological, append-only log of typed events. Seven event types are defined:

1. `Message` -- User input
2. `Action` -- Tool calls (function invocations)
3. `Observation` -- Results from tool execution
4. `Plan` -- Step-level task planning from the Planner module
5. `Knowledge` -- Scoped best practices from the Knowledge module
6. `Datasource` -- API documentation from the Datasource module
7. Miscellaneous system events

**Structural Pattern**: The event stream is a **typed, ordered, possibly-truncated log**. The explicit mention that it "may be truncated or partially omitted" tells us the system handles context window overflow by dropping older events. This is a critical design decision: the agent must be resilient to missing history.

**Boundary validation**: There is no explicit schema validation between modules. Instead, validation happens through behavioral rules:
- The agent must not fabricate Datasource APIs that don't appear in the stream
- The agent must follow Plan step numbering and reach the final step
- Knowledge items have "scope" metadata and should only be adopted when conditions match

**Why this matters for a skill system**: This pattern shows that inter-component communication doesn't need rigid request/response schemas. A shared append-only log with typed entries is sufficient, provided each consumer knows which event types it should react to and which to ignore.

---

## 3. Tool Definition Structure

Tools follow a strict JSON schema with the `function` wrapper pattern:

```
{
  "type": "function",
  "function": {
    "name": "<verb>_<noun>",
    "description": "<what it does>. Use for <when to use it>.",
    "parameters": {
      "type": "object",
      "properties": { ... },
      "required": [...]
    }
  }
}
```

### Naming Convention: `domain_action`

Tools are namespaced by domain, using underscore-delimited compound names:

| Domain | Tools |
|--------|-------|
| `message_` | `notify_user`, `ask_user` |
| `file_` | `read`, `write`, `str_replace`, `find_in_content`, `find_by_name` |
| `shell_` | `exec`, `view`, `wait`, `write_to_process`, `kill_process` |
| `browser_` | `view`, `navigate`, `restart`, `click`, `input`, `move_mouse`, `press_key`, `select_option`, `scroll_up`, `scroll_down`, `console_exec`, `console_view` |
| `info_` | `search_web` |
| `deploy_` | `expose_port`, `apply_deployment` |

### Description Pattern: "What + When"

Every tool description follows a two-sentence structure: the first clause says **what** it does, and the second says **when** to use it. This dual-purpose description serves both the LLM (for tool selection) and documentation.

### Parameter Features Worth Noting

- **`sudo` flag**: File operations include an optional `sudo: boolean` for privilege escalation -- a capability-gating pattern
- **`id` for shell sessions**: Shell tools use a session identifier, enabling multiple concurrent shell sessions -- a **stateful resource handle** pattern
- **Dual targeting (index vs. coordinates)**: Browser tools accept either DOM element index OR x/y coordinates -- a resilience/fallback pattern
- **`suggest_user_takeover`**: Lets the agent suggest the user take manual control -- a **graceful degradation** escape hatch
- **`idle` tool with no parameters**: A terminal sentinel tool that signals task completion explicitly

**Why this matters**: The tool system is flat (no nesting, no tool composition, no tool chaining at the schema level). All composition happens in the agent loop. Tools are deliberately low-level primitives.

---

## 4. Workflow Step Format: Planner-Driven Numbered Pseudocode

Workflows are **not** defined as static DAGs or YAML pipelines. Instead:

- The Planner module generates **numbered pseudocode steps**
- Each planning update includes: current step number, status, and reflection
- The pseudocode updates dynamically when the overall task objective changes
- The agent must reach the final step number to be considered complete

Additionally, the agent maintains a `todo.md` file as a detailed checklist that mirrors the Planner's steps. Rules:
- `todo.md` is subordinate to Planner output (planning takes precedence)
- Progress markers updated immediately after completing each item
- Checklist rebuilt when planning changes significantly
- Mandatory for information-gathering tasks

**Structural Pattern**: A **two-tier planning system**. The Planner provides coarse-grained numbered steps (the "what"), while `todo.md` provides fine-grained checkboxes (the "how"). The agent bridges the two.

---

## 5. Agent Loop Architecture

The core loop has six phases with strict constraints:

```
1. ANALYZE  -- Read event stream, focus on latest user messages + execution results
2. SELECT   -- Choose exactly ONE tool call (never multiple, never zero mid-task)
3. WAIT     -- Sandbox executes the tool; observation appended to stream
4. ITERATE  -- Return to step 1
5. SUBMIT   -- Send results to user via message tools with file attachments
6. IDLE     -- Call the `idle` tool to enter standby
```

### Critical Constraints

- **One tool per iteration**: Exactly one tool call per loop cycle. No parallel tool calls. Forces sequential, observable execution.
- **No plain text responses**: All communication goes through `message_notify_user` or `message_ask_user`.
- **Mandatory delivery before idle**: Must send results via message tools before calling `idle`.

### Decision Points

The ANALYZE phase synthesizes:
1. Latest user message (primary intent)
2. Planner output (what step to execute)
3. Knowledge output (how to execute, scoped to conditions)
4. Datasource output (what APIs are available)
5. Previous observations (what has been tried/completed)
6. Error events (what went wrong)

The SELECT phase applies a priority ordering:
- Datasource APIs > web search > internal knowledge (for information retrieval)
- Dedicated search tools > browser-based search (for web queries)
- File tools > shell commands (for file manipulation)

**Why this matters**: The single-tool-per-iteration constraint trades throughput for observability and debuggability. Every action is individually logged, every result individually assessed.

---

## 6. Module System: Scoped Knowledge Injection

Three fixed slots, all **read-only advisors**:

| Module | Output | Key Constraint |
|--------|--------|----------------|
| Planner | Numbered pseudocode steps | Agent must complete all steps |
| Knowledge | Scoped knowledge items | Advisory only; must check scope conditions |
| Datasource | API documentation events | Only use APIs that appear in stream (no fabrication) |

**Structural Pattern**: Modules are **read-only advisors** that inject typed events. They cannot call tools, cannot interact with the user, and cannot modify each other's output. A spoke-and-hub model where the agent is the hub.

---

## 7. Cross-Cutting Patterns

### Information Priority Hierarchy
```
1. Datasource APIs (authoritative, structured)
2. Web search results (must visit original pages, not snippets)
3. Model internal knowledge (last resort)
```

### Human-in-the-Loop Escape Hatches
1. `message_ask_user` -- blocks execution until user responds
2. `suggest_user_takeover: "browser"` -- suggests manual browser control
3. Error escalation -- report to user after multiple failed approaches

### Error Recovery Strategy
```
1. Verify tool names and arguments
2. Attempt fix based on error message
3. Try alternative methods
4. Report to user with failure reasons
```

A **graduated retry with fallback** pattern. No automatic retry -- the agent must reason about the error.

---

## 8. Summary: Key Takeaways for Gorgon

| Dimension | Manus Pattern | Gorgon Mapping |
|-----------|---------------|----------------|
| Agent coordination | Modules inject events into shared stream | Zorya trio could inject advisory events rather than blocking consensus |
| Tool composition | Agent composes flat primitives in loop | Skill capabilities as flat primitives, workflow composes them |
| Workflow definition | Dynamic numbered pseudocode + live checklist | WHY/WHAT/HOW framework with checkpoint tracking |
| Error handling | Graduated reasoning: verify, fix, pivot, escalate | Feedback loops already support rejection back to previous stages |
| Task lifecycle | Explicit sentinel (`idle` tool) | Add explicit completion signaling to skill execution |
| Tool descriptions | "What + When" dual-sentence format | Adopt for all capability descriptions |
| Tool naming | `domain_action` namespacing | Already using category/skill structure |
| Human involvement | Notify (non-blocking) vs Ask (blocking) + takeover | Maps to consensus levels |
