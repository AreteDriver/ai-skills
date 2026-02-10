# Claude Code Hooks

Reusable hook scripts for Claude Code lifecycle events.

## What Are Hooks?

Hooks are shell scripts that run automatically during Claude Code's tool execution lifecycle. They fire on `PreToolUse` (before a tool runs) and `PostToolUse` (after a tool runs). Claude has no control over whether hooks execute.

## Available Hooks

| Hook | Event | Matcher | Purpose |
|------|-------|---------|---------|
| `tdd-guard.sh` | PreToolUse | Bash | Blocks git commit if tests haven't passed |
| `no-force-push.sh` | PreToolUse | Bash | Blocks force-push to protected branches |
| `protected-paths.sh` | PreToolUse | Write,Edit | Blocks writes to sensitive directories |
| `tool-logger.sh` | PostToolUse | * | Logs all tool invocations for audit |

## Installation

1. Copy the hooks you want to your project or personal Claude config:

```bash
# Project-level
cp hooks/tdd-guard.sh .claude/hooks/
chmod +x .claude/hooks/tdd-guard.sh

# Personal (all projects)
cp hooks/tdd-guard.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/tdd-guard.sh
```

2. Add to your Claude Code settings:

```json
// .claude/settings.json (project) or ~/.claude/settings.json (personal)
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "command": ".claude/hooks/tdd-guard.sh" },
      { "matcher": "Bash", "command": ".claude/hooks/no-force-push.sh" },
      { "matcher": "Write,Edit", "command": ".claude/hooks/protected-paths.sh" }
    ],
    "PostToolUse": [
      { "matcher": "*", "command": ".claude/hooks/tool-logger.sh" }
    ]
  }
}
```

## Exit Codes

| Code | Meaning | Behavior |
|------|---------|----------|
| 0 | Allow | Tool execution proceeds |
| 1 | Error | Hook crashed — tool proceeds (fail-open) |
| 2 | Block | Tool execution blocked, stderr shown to Claude |

## Testing Hooks

```bash
# Test a PreToolUse hook
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' | bash hooks/no-force-push.sh
echo "Exit code: $?"

# Test with stderr output visible
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}' | bash hooks/tdd-guard.sh 2>&1
echo "Exit code: $?"
```

## Creating Custom Hooks

See the `hooks-designer` skill for comprehensive guidance on designing and implementing custom hooks.
