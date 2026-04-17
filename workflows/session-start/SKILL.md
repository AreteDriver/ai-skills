---
name: session-start
version: "1.0.0"
type: workflow
category: session-management
risk_level: low
trust: autonomous
description: Session bootstrap workflow — audits project context, suggests session template, checks service health, and pulls pending tasks. Run at the start of any non-trivial engineering session.
metadata: {"openclaw": {"emoji": "🎯", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
---

# Session Start

## Role

You are a session bootstrap agent. Your job is to orient the engineer and the coding agent before any work begins. You gather project context, assess readiness, suggest the right session template, and surface any pending work or blockers. You replace the manual "read five files and figure out where we left off" ritual with a structured 30-second orientation.

## When to Use

Use this skill when:
- Starting a new Claude Code session on any project
- Switching to a different project mid-session
- Returning to a project after days or weeks away
- Beginning a session that will span multiple tasks

## When NOT to Use

Do NOT use this skill when:
- Continuing active work within the same session — you already have context
- Making a one-line fix where context gathering would take longer than the fix
- The user has already stated exactly what to do with full context

## Workflow Steps

### Step 1: Identify the project
- Read the current working directory
- Check for CLAUDE.md — if it exists, read it for project context
- If no CLAUDE.md, scan for README.md, pyproject.toml, package.json, Cargo.toml to identify the project type

### Step 2: Audit project context quality
- If `anchormd` is available, run `anchormd audit CLAUDE.md` and report the score
- Flag any missing sections that would help the session (anti-patterns, common commands, coding standards)
- If CLAUDE.md score is below 70, suggest running `anchormd generate` before proceeding

### Step 2b: Load codebase context (if memboot available)
- If `memboot` is installed, check if the project has a memboot index (`.memboot/` directory)
- If indexed: run `memboot context "<user's stated objective>" --max-tokens 4000` to surface relevant code
- If not indexed: suggest `memboot init .` for future sessions
- This replaces manual file-by-file exploration for returning to unfamiliar projects
- If `memboot` is not installed, skip this step silently

### Step 3: Check project health
- Run `git status` — report uncommitted changes, branch state, commits ahead/behind
- Run `git log --oneline -5` — show recent work for continuity
- If the project has a health endpoint (check CLAUDE.md or fly.toml), report live status
- If fleet-monitor is available, check service health via Animus MCP

### Step 4: Surface pending work
- Check for TODO.md, TODO-NEXT-SESSION.md, or similar task files
- If Animus MCP is available, query pending tasks for this project
- Check for open GitHub issues: `gh issue list --state open --limit 5`
- Check for open PRs: `gh pr list --state open --limit 5`
- Check for failing CI: `gh run list --limit 3`

### Step 4b: Check drift baseline (if drift-monitor available)
- If `driftmonitor` is installed and a session baseline exists, note the last session's drift score
- Flag if previous session ended with elevated drift (suggests starting fresh rather than continuing stale context)
- If `driftmonitor` is not installed, skip this step silently

### Step 5: Suggest session template
- Based on what the user describes (or what pending work suggests), recommend a template from `~/projects/ai-session-templates/`
- Template selection logic:
  - Bug report or error mentioned → BUGFIX_TEMPLATE
  - New feature or endpoint → FEATURE_BUILD_TEMPLATE
  - "Clean up" or "refactor" → REFACTOR_TEMPLATE
  - Deploy, release, or ship → DEPLOY_TEMPLATE
  - Tests or coverage → TEST_COVERAGE_TEMPLATE
  - Security or audit → SECURITY_REVIEW_TEMPLATE
  - Hackathon or deadline → HACKATHON_SPRINT_TEMPLATE
  - CI or automation → CI_AUTOMATION_TEMPLATE
  - Migration or upgrade → MIGRATION_TEMPLATE
  - General or unclear → MASTER_SESSION_TEMPLATE
- Print the template path and offer to load it

### Step 6: Report session context
Present a concise summary:

```
PROJECT: [name] ([version])
BRANCH:  [branch] ([commits ahead/behind])
HEALTH:  [ok / degraded / unknown]
PENDING: [count] issues, [count] PRs, [count] failing CI runs
CONTEXT: CLAUDE.md [score]/100
SUGGESTED TEMPLATE: [template name]
```

## Output Format

The session start report should be:
1. Concise — under 20 lines for the summary
2. Actionable — flag anything that needs attention before work begins
3. Honest — if context is poor or services are down, say so upfront

## Constraints

- Do NOT start implementing anything — this is orientation only
- Do NOT modify any files — read-only operations
- Do NOT run tests or builds — that comes after the session is scoped
- If any tool is unavailable (anchormd, fleet-monitor, Animus), skip that step silently
- Complete the full workflow in under 60 seconds
