---
name: session-end
version: "1.0.0"
lifecycle: experimental
type: workflow
category: session-management
risk_level: low
trust: supervised
description: Session wrap-up workflow — captures decisions, syncs memory, reports costs, updates tasks, and commits cleanly. Run before ending any session with meaningful work.
metadata: {"openclaw": {"emoji": "📦", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
---

# Session End

## Role

You are a session wrap-up agent. Your job is to ensure nothing gets lost between sessions: decisions are logged, learnings are captured, work is committed, and the next session can pick up without re-discovery. You prevent the "what did I do last time?" problem.

## When to Use

Use this skill when:
- Finishing a Claude Code session where meaningful work was done
- Switching away from a project mid-day
- Completing a multi-step task that produced decisions or learnings
- Before any extended break from a project

## When NOT to Use

Do NOT use this skill when:
- The session was purely exploratory with no code changes
- Everything is already committed and pushed
- The user explicitly says they will handle wrap-up manually

## Workflow Steps

### Step 1: Inventory the session
- Run `git status` to identify all uncommitted changes
- Run `git diff --stat` to see the scope of changes
- Run `git log --oneline origin/main..HEAD` (or equivalent) to list unpushed commits
- Summarize: what was accomplished, what is pending

### Step 2: Capture decisions
- Review the session for high-leverage decisions (architecture, scope, tooling, tradeoffs)
- If the `/decision-log` skill is available, prompt the user to log key decisions
- Decision candidates:
  - Technology or library choices
  - Scope cuts or expansions
  - Architecture changes
  - Deployment or infrastructure decisions
  - Tradeoffs made under time pressure
- Format: one-line summary per decision, with rationale

### Step 2b: Capture reusable prompts
- Review the session for prompts that worked notably well — got it right first try, used a clever pattern, or solved a class of problem cleanly
- If `/prompt-library` is available, prompt the user to log them
- Prompt candidates:
  - Got the desired outcome in one shot with no rework
  - Demonstrated a reusable pattern (constraint sandwich, output-format spec, negative examples, step-by-step decomposition)
  - Solved a common class of task in a way worth keeping
- Skip when: prompts were one-off, needed multiple corrections, or are too context-heavy to generalize
- Format: P-YYYYMMDD-### in the catalog, with Category + Context fields

### Step 3: Capture learnings
- Identify any gotchas, patterns, or fixes discovered during the session
- Check if these belong in:
  - The project's CLAUDE.md (project-specific patterns)
  - The notes repo topics/ files (cross-project knowledge)
  - Claude Code auto-memory (session continuity)
- Prompt the user: "Any gotchas or patterns worth saving from this session?"

### Step 4: Sync memory
- If Animus MCP is available:
  - Push session summary via `animus_remember`
  - Update or complete any Animus tasks worked on
- If Claude Code auto-memory applies:
  - Save any user preferences, feedback, or project facts discovered
- If `tools/animus_sync.py` is relevant, note that it will run on cron

### Step 5: Commit and report
- If there are uncommitted changes:
  - Stage relevant files (avoid secrets, .env, large binaries)
  - Suggest a conventional commit message based on the work done
  - Ask user for confirmation before committing
- If there are unpushed commits:
  - Report count and ask if user wants to push
  - Respect code freezes — if user mentioned a freeze, remind them
- Do NOT push without explicit user approval

### Step 6: Update task tracking
- If TODO.md or similar exists, update completed/pending items
- If GitHub issues were worked on, note which can be closed
- If new work was discovered, suggest adding it to the task tracker

### Step 6b: Audit key outputs (if signal-audit available)
- If `signal-audit` is installed, audit the session's most important AI-generated outputs
- Candidates: commit messages, generated documentation, narrations, analysis reports
- Run `signal-audit check <file>` on any generated content over 200 words
- Flag outputs with quality score below 6/10 for human review before accepting
- This catches hedging, overconfidence, filler, and weak reasoning before it ships
- If `signal-audit` is not installed, skip this step silently

### Step 6c: Scrub published content
- If the session produced content for publication (README prose, substack drafts, landing pages):
  - Run content-scrubber as the final gate
  - Do NOT scrub technical docs, CLAUDE.md, or code comments
- If no published content was produced, skip this step

### Step 7: Session summary
Present a concise wrap-up:

```
SESSION SUMMARY
===============
Project:    [name]
Duration:   [approximate, if known]
Commits:    [N] local ([N] unpushed)
Changes:    [files changed summary]
Decisions:  [count logged]
Learnings:  [count captured]

QUALITY:    [signal-audit avg score, if run]
DRIFT:      [session drift score, if tracked]
COST:       [estimated token spend, if tracked]

RULES AUDIT
- [rule-name]: applied | skipped | violated | n/a — [one-line basis]
- ...

PENDING
- [ ] [any uncommitted work]
- [ ] [any follow-up items]
- [ ] [any blocked work]

NEXT SESSION
- [suggested starting point]
- [any context to load]
```

The RULES AUDIT block is required, not optional. List every durable feedback rule that was in scope for the actions taken this session — minimum: any rule with a trigger that fired (e.g., `gh repo create` → `feedback_verify_namespace_before_consuming`, `git push` → `feedback_run_preflight_before_push`, content publication → `content-scrubber`, `<system-reminder>` fired → `feedback_harness_reminder_explicit_eval`, subagent returned with conditional verdicts → `feedback_resolve_subagent_conditionals_before_relay`). For each, mark applied / skipped / violated / n/a with one-line basis. If you can't state the basis, the rule was not actually applied. Externalizing this makes skipped rules visible in the transcript so the user can catch drift inside the session, not only days later.

### Step 7b: Length discipline

**Hard caps on wrap output, enforced without carve-outs:**

- **New full session file** (`sessions/YYYY-MM-DD.md`): ≤ 100 lines
- **Addendum to existing session file** (appending to a same-day file): ≤ 40 lines
- **TODO.md changes**: only the items that didn't exist before; never restate carried items
- **User-facing summary output**: ≤ 30 lines including the SESSION SUMMARY block

If a wrap would exceed any of these caps, the **first line** of the over-cap section must justify the length with a specific deliverable (e.g., "Operator queue spans 7 items each requiring distinct action — list cannot compress further" / "5 ADLs landed today, each needs preserved rationale per ADL convention"). Going over without justification is a quality miss — the skill's "scannable, not verbose" guidance failed in 2026-05-28 PM session (80-line addendum on top of 187-line file) and the caps are the corrective.

The cap is a default. Real session size varies. The discipline is: justify in writing, don't drift over silently.

### Step 8: Track session metrics (optional)
If the project has a session log or the notes repo is available:
- Record: project name, date, approximate duration, commits made, test count delta, coverage delta, decisions logged
- AI output quality scores (signal-audit average) if signal-audit was run
- Drift score at session end (drift-monitor) if driftmonitor is installed
- Token spend (ai-spend) if ai-spend is installed and tracking is available
- Append to `~/projects/notes/sessions/YYYY-MM-DD.md` if the file exists
- Format: one-line entry per session

## Output Format

1. Structured summary — scannable, not verbose
2. Action items clearly marked as pending
3. Next-session hints so the engineer (or agent) can resume fast

## Constraints

- Do NOT push to remote without user confirmation
- Do NOT commit files that might contain secrets (.env, credentials, tokens)
- Do NOT create empty commits or meaningless "session end" commits
- Do NOT modify code — this is a wrap-up workflow, not implementation
- If the user says "just commit and go," respect that — skip the full ceremony
- Keep the wrap-up under 2 minutes
