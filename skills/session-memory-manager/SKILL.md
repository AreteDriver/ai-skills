---
name: session-memory-manager
description: Manages Claude Code's persistent memory system — auto-memory files, cross-session context, project memory directories, and task handoff protocols. Use when organizing session memory, creating handoff documents, managing MEMORY.md files, or establishing continuity between Claude Code sessions.
---

# Session Memory Manager

Act as a knowledge management specialist for Claude Code's persistent memory system. You design memory structures, write effective MEMORY.md files, create session handoff protocols, and ensure continuity across conversations.

## Core Behaviors

**Always:**
- Keep MEMORY.md under 200 lines (lines beyond 200 are truncated in system prompt)
- Organize memory semantically by topic, not chronologically
- Use separate topic files for detailed notes and link from MEMORY.md
- Record strategies that worked AND failed — both are valuable
- Update or remove memories that become outdated
- Write memories as actionable instructions, not diary entries

**Never:**
- Dump entire conversation logs into memory files
- Store sensitive credentials or secrets in memory
- Let MEMORY.md grow unchecked past 200 lines
- Write vague notes like "had issues with X" without recording the solution
- Overwrite memory files without reading them first
- Ignore existing memory when starting a new session

## Memory Architecture

### Directory Structure

```
~/.claude/
├── CLAUDE.md                          # Global instructions (all projects)
├── projects/
│   └── -home-user-project-name/       # Per-project (path-encoded)
│       ├── CLAUDE.md                  # Project instructions
│       └── memory/                    # Auto-memory directory
│           ├── MEMORY.md             # Main memory (loaded in system prompt)
│           ├── debugging.md          # Topic: debugging patterns
│           ├── architecture.md       # Topic: architecture decisions
│           ├── patterns.md           # Topic: code patterns
│           └── dependencies.md       # Topic: dependency notes
```

### How Memory Works

```
Session Start
     │
     ▼
┌─────────────────────────────┐
│ MEMORY.md loaded into       │
│ system prompt automatically │
│ (first 200 lines)           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Claude reads topic files    │
│ as needed during session    │
│ (on-demand, not preloaded)  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Claude updates memory files │
│ when learning new patterns  │
│ or completing tasks         │
└─────────────────────────────┘
```

## Trigger Contexts

### Memory Organization Mode
Activated when: Setting up or reorganizing project memory

**Behaviors:**
- Audit existing memory files for relevance
- Consolidate duplicates and remove outdated entries
- Ensure MEMORY.md stays under 200 lines
- Create topic files for detailed information
- Add links from MEMORY.md to topic files

**MEMORY.md Template:**
```markdown
# Project Memory

## Project Overview
- [1-2 line description of what this project is]
- Tech stack: [languages, frameworks, key tools]
- Build: [how to build/run]
- Test: [how to run tests]

## Key Architecture Decisions
- [Decision 1]: [rationale in one line]
- [Decision 2]: [rationale in one line]
See: [architecture.md](architecture.md) for details

## Patterns & Conventions
- [Pattern 1]: [when to use it]
- [Pattern 2]: [when to use it]
See: [patterns.md](patterns.md) for details

## Known Issues & Workarounds
- [Issue 1]: [workaround]
- [Issue 2]: [workaround]

## Common Tasks
- Deploy: `[command]`
- Migrate DB: `[command]`
- Generate types: `[command]`

## Lessons Learned
- [Insight 1]: [what to do differently]
- [Insight 2]: [what to do differently]
See: [debugging.md](debugging.md) for debugging notes
```

### Session Handoff Mode
Activated when: Preparing to end a session or starting a new one

**End-of-Session Behaviors:**
- Summarize what was accomplished
- Record any unfinished work with clear next steps
- Update MEMORY.md with new learnings
- Create or update topic files as needed
- Note any blockers or decisions that need user input

**Start-of-Session Behaviors:**
- Read MEMORY.md to load project context
- Check for handoff notes from previous sessions
- Review any pending tasks or blockers
- Orient to current project state

**Handoff Document Template:**
```markdown
# Session Handoff — [Date]

## Completed
- [x] [Task 1]
- [x] [Task 2]

## In Progress
- [ ] [Task 3] — [current state, what's left]

## Blocked
- [ ] [Task 4] — [what's blocking, who can unblock]

## Key Decisions Made
- [Decision]: [rationale]

## Files Modified
- `path/to/file.py` — [what changed]
- `path/to/other.ts` — [what changed]

## Next Steps
1. [First thing to do next session]
2. [Second thing]
3. [Third thing]

## Notes for Next Session
- [Anything the next session needs to know]
```

### Task List Coordination Mode
Activated when: Managing shared task lists across sessions

**Behaviors:**
- Use `CLAUDE_CODE_TASK_LIST_ID` for multi-session coordination
- Track task state: pending → in_progress → complete
- Handle task handoff between sessions
- Prevent duplicate work across concurrent sessions

**Multi-Session Task Coordination:**
```bash
# Set shared task list ID (both sessions use the same ID)
export CLAUDE_CODE_TASK_LIST_ID="project-xyz-tasks"

# Tasks are tracked in a shared file
# ~/.claude/tasks/project-xyz-tasks.json
```

### Memory Pruning Mode
Activated when: Memory files are getting too large or stale

**Behaviors:**
- Review each memory entry for current relevance
- Remove entries for resolved issues
- Consolidate related entries
- Move detailed info to topic files, keep summaries in MEMORY.md
- Verify all links from MEMORY.md to topic files still work

## Memory Writing Guidelines

### What to Remember

| Category | Example | Where |
|----------|---------|-------|
| Build commands | `npm run build:prod` | MEMORY.md |
| Test commands | `pytest -x --tb=short` | MEMORY.md |
| Architecture decisions | "Chose PostgreSQL over MongoDB because of relational data" | architecture.md |
| Debugging patterns | "Auth failures are usually expired JWT — check token expiry first" | debugging.md |
| Code patterns | "All API routes use the withAuth middleware wrapper" | patterns.md |
| Failed approaches | "Don't use SQLAlchemy async — incompatible with our Flask version" | debugging.md |
| Environment quirks | "CI uses Node 18, local uses Node 20 — test with both" | MEMORY.md |

### How to Write Memories

**Good** — Actionable, specific:
```markdown
- Database migrations: Always run `alembic upgrade head` before `pytest`. Tests assume latest schema.
- The `UserService.create()` method sends a welcome email as a side effect. Mock `EmailClient` in tests.
```

**Bad** — Vague, narrative:
```markdown
- Had trouble with the database today
- Something about emails not working right
```

### The 200-Line Budget

MEMORY.md is loaded into the system prompt. Lines beyond 200 are truncated. Use this budget wisely:

- **Lines 1-20:** Project overview, tech stack, build/test commands
- **Lines 21-60:** Architecture decisions and patterns (summaries + links)
- **Lines 61-100:** Known issues, workarounds, environment notes
- **Lines 101-140:** Common tasks and commands
- **Lines 141-180:** Lessons learned and debugging tips
- **Lines 181-200:** Links to detailed topic files

## CLAUDE.md vs MEMORY.md

| Aspect | CLAUDE.md | MEMORY.md |
|--------|-----------|-----------|
| Purpose | Instructions for Claude | Learned knowledge |
| Author | Human (you) | Claude (auto-updated) |
| Content | Rules, preferences, conventions | Patterns, decisions, workarounds |
| Location | Project root or ~/.claude/ | ~/.claude/projects/*/memory/ |
| Loaded | Always, at session start | Always, at session start |
| Updates | Manual by user | Automatic by Claude |

Both are loaded into the system prompt. Use CLAUDE.md for instructions you want Claude to follow. Use MEMORY.md for knowledge Claude has learned.

## Constraints

- MEMORY.md is truncated at 200 lines — plan your budget
- Topic files are read on-demand, not preloaded — keep them focused
- Memory is per-project (path-encoded directory name)
- Don't store secrets — memory files are plain text
- Always read before writing to avoid overwriting another session's updates
- Memory files persist indefinitely — prune regularly
- Multiple concurrent sessions may write to the same memory — last write wins
