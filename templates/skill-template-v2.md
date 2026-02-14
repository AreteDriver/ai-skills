# SKILL.md v2 Template

This template incorporates structural patterns from Cursor, Claude Code, Devin, Manus,
and Antigravity. See `intel/` for full pattern analysis.

**Key changes from v1:**
- Extended frontmatter with version, type, risk, and trust metadata
- "When to Use / When NOT to Use" replaces generic "Trigger Contexts"
- Explicit "Never" section elevated from sub-list to full section (Devin pattern)
- Capabilities section adds intent, parallel safety, and post-execution guidance (Cursor)
- Verification section adds structured checkpoints (Devin think-triggers)
- Error handling adds escalation ladder with bounded retries (Devin/Cursor)
- Self-correction rules for protocol violations (Cursor Sep 2025)

---

## Template

```markdown
---
name: skill-name
version: "1.0.0"
description: "One-line description under 300 characters"
# --- Type & Classification ---
type: persona | agent | workflow
category: engineering | data | devops | security | domain | orchestration | analysis
risk_level: low | medium | high | critical
# --- Trust & Execution ---
trust: supervised | autonomous
parallel_safe: true | false
# --- Agent-only fields (omit for personas) ---
agent: system | browser | email | app | file
consensus: any | majority | unanimous | unanimous+user
# --- Optional ---
tools: ["*"] | ["Read", "Edit", "Glob", "Grep"]
---

# Skill Name

Brief one-sentence summary of what this skill does and when it activates.

## Role

You are a [role description]. You specialize in [domain]. Your approach is [disposition].

## When to Use

Use this skill when:
- Condition 1 — specific scenario where this skill is the right choice
- Condition 2 — another scenario
- Condition 3 — another scenario

## When NOT to Use

Do NOT use this skill when:
- Condition 1 — use [alternative skill] instead, because [reasoning]
- Condition 2 — use [alternative skill] instead, because [reasoning]

> Negative routing examples prevent over-delegation and misuse.
> Every "when not" should name the better alternative and explain why.

## Core Behaviors

**Always:**
- Behavior 1
- Behavior 2
- Behavior 3

**Never:**
- Anti-pattern 1 — [why this is dangerous]
- Anti-pattern 2 — [why this is dangerous]
- Anti-pattern 3 — [why this is dangerous]

> Every "never" should explain the consequence, not just state the rule.

## Capabilities

### capability_name
What it does. Use when [specific scenario]. Do NOT use when [specific scenario].

- **Risk:** low | medium | high | critical
- **Consensus:** any | majority | unanimous | unanimous+user
- **Parallel safe:** yes | no
- **Intent required:** yes — agent must state WHY before invoking
- **Inputs:**
  - `param_name` (type, required) — description
  - `param_name` (type, optional, default: value) — description
- **Outputs:**
  - `field_name` (type) — description
- **Post-execution:** [What to do with the result — verify, check completeness, retry if insufficient]

### another_capability
[Same structure as above]

> The "Intent required" field forces the agent to articulate purpose before
> execution (Cursor's `explanation` parameter pattern).
>
> "Post-execution" defines what to DO with results, not just the return shape
> (Cursor's read_file completeness protocol).

## Verification

### Pre-completion Checklist
Before reporting this skill's work as complete, verify:
- [ ] All acceptance criteria met
- [ ] No partial implementations left behind
- [ ] [Domain-specific check 1]
- [ ] [Domain-specific check 2]

### Checkpoints
Pause and reason explicitly (use a think step) when:
- About to switch from reading/research to writing/execution
- Encountering unexpected complexity mid-task
- Multiple approaches have failed
- About to perform a destructive or irreversible operation
- Before reporting completion

> Structured checkpoint triggers replace vague "think when needed" with
> specific situations (Devin's 10-trigger pattern).

## Error Handling

### Escalation Ladder

| Error Type | Action | Max Retries |
|------------|--------|-------------|
| Recoverable (code bug, lint failure) | Self-fix, re-verify | 3 |
| Environment (missing dependency, config) | Report, use fallback | 0 |
| Permission/auth | Escalate to user immediately | 0 |
| Repeated failure (same error 3x) | Stop, report what was tried | — |

### Self-Correction
If you violate this skill's protocol (skip verification, miss a checkpoint, use
wrong tool for the job):
- Acknowledge the violation on the next turn
- Self-correct before proceeding
- Do not repeat the violation

> Bounded retries prevent infinite loops. Error categories get different
> strategies (Devin/Cursor pattern). Self-correction rules handle protocol
> violations (Cursor Sep 2025).

## Output Format

### [Format Name]
Use when: [condition]

```
[Template or example output structure]
```

## Constraints

- Constraint 1
- Constraint 2
- Constraint 3

## Examples

### Example 1: [Scenario]

**Input:** [Sample input]

**Expected behavior:** [What the skill should do, step by step]

**Output:** [Sample output]
```

---

## Frontmatter Field Reference

| Field | Required | Values | Purpose |
|-------|----------|--------|---------|
| `name` | Yes | string | Skill identifier, kebab-case |
| `version` | Yes | semver | Track breaking changes |
| `description` | Yes | string (<300 chars) | Skill discovery and auto-loading |
| `type` | Yes | persona, agent, workflow | Determines which optional fields apply |
| `category` | Yes | see enum | Registry grouping |
| `risk_level` | Yes | low, medium, high, critical | Default risk for the skill as a whole |
| `trust` | No | supervised, autonomous | Default execution mode (maps to Antigravity turbo) |
| `parallel_safe` | No | boolean | Can this skill run concurrently with others? |
| `agent` | Agent only | system, browser, email, app, file | Which agent type executes this skill |
| `consensus` | Agent only | any, majority, unanimous, unanimous+user | Default consensus requirement |
| `tools` | No | string[] | Allowed tool set (Claude Code sub-agent pattern) |

## Section Applicability

| Section | Persona | Agent | Workflow |
|---------|---------|-------|----------|
| Role | Required | Required | Optional |
| When to Use | Required | Required | Required |
| When NOT to Use | Required | Required | Required |
| Core Behaviors | Required | Required | Optional |
| Capabilities | Optional | Required | Required |
| Verification | Recommended | Required | Required |
| Error Handling | Optional | Required | Required |
| Output Format | Optional | Optional | Optional |
| Constraints | Required | Required | Required |
| Examples | Recommended | Recommended | Optional |
