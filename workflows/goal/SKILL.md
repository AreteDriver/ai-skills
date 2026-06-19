---
name: goal
description: Manage the build-mode goal-loop — set, inspect, pause, resume, extend, or clear a durable build objective with a budget ceiling. Drives the goal-loop + goal-gate hooks via a repo-root .goal-active sentinel. Invoke with /goal.
lifecycle: experimental
---

# Goal — build-mode goal-loop control

`/goal` manages a durable build objective for the current repo. The state lives in a flat `.goal-active` sentinel at the repo root; the `goal-loop` (UserPromptSubmit) and `goal-gate` (PreToolUse) hooks read it. This skill is the human control surface. Use it for **code/build work only** — it is the opposite of `/exploration`.

## Sentinel schema (`<repo-root>/.goal-active`, flat key:value)

```
objective: <one line — what "done" means>
stop_condition: <falsifiable end state>
budget_ceiling_usd: 10
turn_ceiling: 25
turns: 0
spent_usd: 0
mode: engaged        # engaged | armed | paused
started_at: <ISO8601>
```

`engaged` = hook injects objective + budget each turn and forces a checkpoint at either ceiling; destructive ops require approval. `armed` = advisory only (set by `/specification`). `paused` = inert but preserved.

## Subcommands

- **`/goal`** or **`/goal status`** — read `.goal-active` and report mode, objective, stop condition, turns/ceiling, spent/budget. If absent: "No active goal in this repo."
- **`/goal "<objective>"`** — ENGAGE. Write `.goal-active` with `mode: engaged`, the given objective, `turns: 0`, `spent_usd: 0`, defaults `budget_ceiling_usd: 10` / `turn_ceiling: 25`, and `started_at` = current ISO timestamp (get it via `date -u +%Y-%m-%dT%H:%M:%SZ`). If no stop condition is obvious, ask the user for one before writing. Then ensure `.goal-active` is git-ignored (add to `.gitignore` or `.git/info/exclude`).
- **`/goal pause`** — set `mode: paused` (loop goes inert, state preserved).
- **`/goal resume`** — set `mode: engaged`.
- **`/goal spend <usd>`** — set `spent_usd: <usd>` (log real cost observed from the statusline; honored against `budget_ceiling_usd`).
- **`/goal extend [n]`** — raise `turn_ceiling` by `n` (default +15) and reset `turns: 0`. Use after a checkpoint to authorize another budget window.
- **`/goal clear`** — delete the `.goal-active` sentinel (goal complete or abandoned).

## Rules

- Always operate on the sentinel at `$(git rev-parse --show-toplevel)/.goal-active`. If not in a git repo, tell the user the goal-loop requires one.
- Edit individual fields in place (don't rewrite unrelated fields); preserve `turns` unless the subcommand resets it.
- Never set `mode` to a value other than `engaged` / `armed` / `paused`.
- The checkpoint exists to honor the $10 spend-checkpoint discipline. When the hook reports a checkpoint, stop and report ROI before continuing; only `/goal extend` re-authorizes autonomous progress.
