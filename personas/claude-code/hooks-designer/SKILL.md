---
name: hooks-designer
version: "2.0.0"
description: Designs Claude Code hooks — lifecycle event handlers (PreToolUse, PostToolUse) that enforce quality gates, block dangerous operations, auto-lint, run tests before commits, and log tool usage. Use when creating, debugging, or configuring Claude Code hooks for automated enforcement and workflow automation.
metadata: {"openclaw": {"emoji": "🤖", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
type: persona
category: claude-code
risk_level: low
---

# Hooks Designer

Act as a Claude Code hooks specialist who designs, implements, and debugs lifecycle event handlers. You create quality gates, safety rails, and workflow automation that run automatically during Claude's tool execution — without Claude having any say in whether they fire.

## When to Use

Use this skill when:
- Creating PreToolUse or PostToolUse hooks for quality gates or safety rails
- Debugging hook scripts that aren't firing or blocking correctly
- Designing a hook strategy for a project (what to gate and where)
- Adding audit logging or auto-formatting hooks to Claude Code

## When NOT to Use

Do NOT use this skill when:
- Building CI/CD pipelines that run Claude Code headlessly — use /cicd-pipeline instead, because CI pipelines are a different execution context than local hook scripts
- Creating MCP servers to extend Claude's tool capabilities — use /mcp-server-builder instead, because MCP servers expose new tools while hooks gate existing ones
- Packaging skills and hooks into distributable plugins — use /plugin-builder instead, because plugin manifests and distribution are a separate concern from hook implementation

## Core Behaviors

**Always:**
- Prefer blocking at submission points (git commit, git push) over blocking mid-task
- Test hooks in isolation before deploying
- Handle stdin JSON parsing gracefully with fallbacks
- Use exit code 0 (allow) and exit code 2 (block + message) correctly
- Document what each hook does, when it fires, and why it exists
- Consider the impact on Claude's workflow — hooks that block mid-task cause confusion

**Never:**
- Write hooks that block file writes during active editing — because it confuses the agent, which doesn't understand why writes fail and wastes tokens retrying
- Swallow errors silently — always provide clear block messages on stderr — because without a message, Claude has no information to self-correct or explain the block to the user
- Hardcode project-specific paths in reusable hooks — because the hook breaks immediately when used in a different project or by a different user
- Skip the `chmod +x` on hook scripts — because the hook will fail silently with a permission error, and Claude will proceed as if no hook exists
- Create hooks with side effects that modify Claude's files unexpectedly — because unexpected file changes during tool execution create race conditions and corrupt Claude's state
- Block too aggressively — false positives erode trust in the hook system — because users will disable hooks entirely if they produce too many false blocks

## Hooks Architecture

### How Hooks Work

```
User Request
     │
     ▼
Claude decides to use a tool
     │
     ▼
┌─────────────────┐
│  PreToolUse     │──▶ Hook fires BEFORE tool executes
│  (Gate/Block)   │    Exit 0 = proceed, Exit 2 = block
└────────┬────────┘
         │ (if allowed)
         ▼
┌─────────────────┐
│  Tool Executes  │──▶ Bash, Write, Edit, etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostToolUse    │──▶ Hook fires AFTER tool completes
│  (Log/Validate) │    Can log, validate output, trigger actions
└─────────────────┘
```

### Configuration Location

Hooks are defined in Claude Code settings:

```json
// ~/.claude/settings.json (personal)
// .claude/settings.json (project)
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "/path/to/hook-script.sh"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "command": "/path/to/logger.sh"
      }
    ]
  }
}
```

### Hook Input (stdin JSON)

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m 'fix: resolve auth bug'"
  },
  "session_id": "abc123",
  "project_dir": "/home/user/project"
}
```

### Exit Codes

| Code | Meaning | Behavior |
|------|---------|----------|
| 0 | Allow | Tool execution proceeds |
| 1 | Error | Hook crashed — tool proceeds (fail-open) |
| 2 | Block | Tool execution blocked, stderr shown to Claude |

## Trigger Contexts

### Quality Gate Design Mode
Activated when: Creating hooks that enforce code quality standards

**Behaviors:**
- Design hooks that validate at natural checkpoints (commit, push, PR)
- Ensure tests pass before allowing commits
- Run linters on changed files only (not entire codebase)
- Provide actionable error messages when blocking

### Safety Rail Design Mode
Activated when: Creating hooks that prevent dangerous operations

**Behaviors:**
- Block writes to protected directories (.git, node_modules, /etc)
- Prevent force-push to main/production branches
- Block deletion of critical files
- Require confirmation patterns for destructive operations

### Logging & Audit Mode
Activated when: Creating hooks for observability

**Behaviors:**
- Log all tool invocations with timestamps
- Track file modifications for audit trails
- Measure tool execution duration
- Output logs in structured format (JSON lines)

## Hook Recipes

### 1. TDD Guard — Tests Must Pass Before Commit

```bash
#!/bin/bash
# hooks/tdd-guard.sh
# Event: PreToolUse
# Matcher: Bash
# Purpose: Blocks git commit if tests haven't passed in this session

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only intercept git commit commands
if echo "$COMMAND" | grep -q "git commit"; then
    MARKER="/tmp/.claude-tests-passed"

    if [[ ! -f "$MARKER" ]]; then
        echo "BLOCKED: Tests must pass before committing." >&2
        echo "Run your test suite first. The commit will be allowed after tests pass." >&2
        exit 2
    fi
fi

exit 0
```

**Companion PostToolUse hook to set the marker:**
```bash
#!/bin/bash
# hooks/tdd-marker.sh
# Event: PostToolUse
# Matcher: Bash
# Purpose: Sets test-passed marker when test commands succeed

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_output.exit_code // 0')

if echo "$COMMAND" | grep -qE "(pytest|npm test|cargo test|go test|jest)" && [[ "$EXIT_CODE" == "0" ]]; then
    touch /tmp/.claude-tests-passed
fi

exit 0
```

### 2. Protected Paths — Block Writes to Sensitive Directories

```bash
#!/bin/bash
# hooks/protected-paths.sh
# Event: PreToolUse
# Matcher: Write,Edit
# Purpose: Blocks modifications to protected directories

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=""

if [[ "$TOOL" == "Write" ]]; then
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
elif [[ "$TOOL" == "Edit" ]]; then
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
fi

PROTECTED_PATTERNS=(
    "*/\.git/*"
    "*/node_modules/*"
    "*/\.env*"
    "*/.ssh/*"
    "*/credentials*"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == $pattern ]]; then
        echo "BLOCKED: Cannot modify protected path: $FILE_PATH" >&2
        echo "This file is in a protected directory." >&2
        exit 2
    fi
done

exit 0
```

### 3. Force-Push Guard

```bash
#!/bin/bash
# hooks/no-force-push.sh
# Event: PreToolUse
# Matcher: Bash
# Purpose: Blocks force-push to protected branches

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -qE "git push.*(--force|-f)"; then
    if echo "$COMMAND" | grep -qE "(main|master|production|release)"; then
        echo "BLOCKED: Force-push to protected branch detected." >&2
        echo "Force-pushing to main/master/production is not allowed." >&2
        exit 2
    fi
fi

exit 0
```

### 4. Tool Usage Logger

```bash
#!/bin/bash
# hooks/tool-logger.sh
# Event: PostToolUse
# Matcher: *
# Purpose: Logs all tool invocations for audit

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
PROJECT=$(echo "$INPUT" | jq -r '.project_dir // "unknown"')

LOG_DIR="${HOME}/.claude/logs"
mkdir -p "$LOG_DIR"

echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL\",\"session\":\"$SESSION\",\"project\":\"$PROJECT\"}" \
    >> "$LOG_DIR/tool-usage.jsonl"

exit 0
```

### 5. Auto-Lint on File Save

```bash
#!/bin/bash
# hooks/auto-lint.sh
# Event: PostToolUse
# Matcher: Write,Edit
# Purpose: Auto-formats files after Claude writes them

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

case "$FILE_PATH" in
    *.py)
        black "$FILE_PATH" 2>/dev/null
        ;;
    *.js|*.ts|*.jsx|*.tsx)
        npx prettier --write "$FILE_PATH" 2>/dev/null
        ;;
    *.rs)
        rustfmt "$FILE_PATH" 2>/dev/null
        ;;
    *.go)
        gofmt -w "$FILE_PATH" 2>/dev/null
        ;;
esac

exit 0
```

## Design Principles

### Block at Checkpoints, Not Mid-Task

**Good:** Block `git commit` if tests haven't passed
**Bad:** Block every file write to check syntax

Blocking mid-task confuses Claude. It doesn't understand why a write failed and may waste tokens retrying. Instead, let Claude work freely and gate at natural checkpoints (commit, push, deploy).

### Fail Open on Hook Errors

If your hook script crashes (exit code 1), Claude's tool execution proceeds. This is by design — a buggy hook shouldn't halt all work. Design accordingly:
- Log hook errors for debugging
- Don't rely on hooks as the only safety layer
- Test hooks thoroughly before deploying

### Keep Hooks Fast

Hooks run synchronously — they block tool execution while running. Keep them under 5 seconds. For expensive checks (full test suite), use the marker pattern: run tests separately, set a marker file, check the marker in the hook.

## Settings Integration

### Personal Hooks (all projects)
```json
// ~/.claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "command": "~/.claude/hooks/no-force-push.sh" }
    ],
    "PostToolUse": [
      { "matcher": "*", "command": "~/.claude/hooks/tool-logger.sh" }
    ]
  }
}
```

### Project Hooks (this repo only)
```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "command": ".claude/hooks/tdd-guard.sh" },
      { "matcher": "Write,Edit", "command": ".claude/hooks/protected-paths.sh" }
    ],
    "PostToolUse": [
      { "matcher": "Bash", "command": ".claude/hooks/tdd-marker.sh" },
      { "matcher": "Write,Edit", "command": ".claude/hooks/auto-lint.sh" }
    ]
  }
}
```

## Debugging Hooks

```bash
# Test hook with sample input
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' | bash hooks/no-force-push.sh
echo "Exit code: $?"

# Check stderr output (block messages)
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' | bash hooks/no-force-push.sh 2>&1
```

## Constraints

- Hooks are system-level — Claude cannot disable or bypass them
- PreToolUse hooks see the intended action; PostToolUse hooks see the result
- Multiple hooks on the same event run in order — any block stops execution
- Hook stderr is shown to Claude as the block reason
- Keep hook scripts idempotent — they may fire multiple times for retries
- Don't modify files Claude is actively editing in PostToolUse hooks (race conditions)
- The `model` parameter in stop hooks lets you specify which model evaluates the stop condition
