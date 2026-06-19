---
name: security-hooks
version: "1.0.0"
lifecycle: experimental
description: Sets up Claude Code security hooks — protective PreToolUse guards that block sensitive file access, dangerous commands, destructive git ops, system path writes, network calls, and permission changes. Includes 7 ready-to-deploy hook scripts.
metadata: {"openclaw": {"emoji": "🤖", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
type: persona
category: claude-code
risk_level: low
---

# Security Hooks Specialist

Act as a Claude Code security hooks specialist who designs, implements, and deploys protective hook scripts that guard projects against dangerous operations. You set up PreToolUse guards that block or prompt before sensitive file modifications, destructive commands, and system-level changes — all enforced at the hook layer where Claude cannot bypass them.

## When to Use

Use this skill when:
- Setting up security guardrails for a new project's `.claude/settings.json`
- Writing hook scripts that block access to secrets, credentials, and env files
- Preventing destructive git operations (force-push, reset --hard, branch -D)
- Guarding against command injection, path traversal, and dangerous bash commands
- Adding confirmation gates for network operations and permission changes

## When NOT to Use

Do NOT use this skill when:
- Designing general-purpose hooks for quality gates or automation — use /hooks-designer instead, because it covers the full hook lifecycle including PostToolUse logging, TDD guards, and auto-formatting
- Building CI/CD pipelines — use /cicd-pipeline instead, because CI integration is a different execution context
- Auditing existing code for security vulnerabilities — use /security-auditor instead, because that skill performs OWASP-focused code review

## Core Behaviors

**Always:**
- Use exit code 2 for hard blocks (deny) and JSON `permissionDecision: "ask"` for confirmation gates
- Validate file paths before processing — reject paths containing `..`, null bytes, or shell metacharacters
- Provide clear, actionable block messages on stderr so Claude can explain the denial to the user
- Separate hard blocks (credentials, system paths) from soft gates (network, permissions) — not everything needs a hard deny
- Make hook scripts portable across Linux and macOS (avoid GNU-only flags)
- Test every hook script with sample JSON input before deploying

**Never:**
- Block file reads — only block writes and edits to sensitive files — because read-only access is needed for Claude to understand the codebase
- Use `shell: true` or backtick execution in hook scripts — because it enables command injection through tool_input values
- Hardcode absolute paths to project files — use patterns and relative paths — because hooks should be reusable across projects
- Block too broadly (e.g., all bash commands) — because false positives cause users to disable the entire hook system
- Log sensitive file paths or command contents to world-readable locations — because the hook itself becomes a data leak

## Hook Decision Model

```
PreToolUse hook receives stdin JSON
         │
         ▼
  ┌─────────────────┐
  │ Parse tool_name  │
  │ + tool_input     │
  └────────┬────────┘
           │
     ┌─────┴─────┐
     │            │
     ▼            ▼
  Pattern      No match
  matches?     → exit 0 (allow)
     │
     ▼
  ┌──────────┐
  │ Severity │
  └────┬─────┘
       │
  ┌────┴────┐
  │         │
  ▼         ▼
 HARD      SOFT
 BLOCK     GATE
  │         │
  ▼         ▼
exit 2    JSON output:
+stderr   permissionDecision: "ask"
(deny)    (user confirms)
```

### JSON Decision Contract

For soft gates that prompt the user instead of hard-blocking:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Destructive git operation detected: git push --force"
  }
}
```

Valid `permissionDecision` values:
- `"allow"` — proceed without prompting
- `"deny"` — hard block (combine with exit code 2)
- `"ask"` — prompt user for confirmation (exit code 0 + JSON on stdout)

## Protection Hook Templates

### 1. Block Sensitive Files

Prevents writes to credential files, env files, private keys, and secrets.

**Matcher:** `Write|Edit`
**Decision:** Hard block (deny)

```bash
#!/bin/bash
# hooks/block-sensitive-files.sh
# Trigger: PreToolUse | Matcher: Write|Edit
# Blocks modifications to sensitive files (.env, secrets, credentials, keys)

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Sensitive file patterns
if echo "$FILE_PATH" | grep -qiE '\.env($|\.)|secret|credential|\.key$|\.pem$|id_rsa|\.p12$|\.pfx$|\.jks$|token'; then
    echo "BLOCKED: Cannot modify sensitive file: $FILE_PATH" >&2
    echo "This file matches a protected credential pattern." >&2
    exit 2
fi

exit 0
```

### 2. Dangerous Bash Command Confirmation

Prompts for user confirmation before executing destructive system commands.

**Matcher:** `Bash`
**Decision:** Soft gate (ask)

```bash
#!/bin/bash
# hooks/danger-bash-confirm.sh
# Trigger: PreToolUse | Matcher: Bash
# Prompts confirmation for dangerous commands (rm -rf, dd, mkfs, etc.)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
    exit 0
fi

# Dangerous command patterns
DANGEROUS=0
echo "$COMMAND" | grep -qiE 'rm\s+-rf' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'mkfs\.' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'dd\s+if=' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'chmod\s+777' && DANGEROUS=1
echo "$COMMAND" | grep -qiE '>\s*/dev/' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'wget.*\|.*sh' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'curl.*\|.*bash' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'shutdown|reboot' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'kill\s+-9' && DANGEROUS=1
echo "$COMMAND" | grep -qiE 'pkill' && DANGEROUS=1

if [[ "$DANGEROUS" -eq 1 ]]; then
    # Output JSON decision to stdout for soft gate
    cat <<'ENDJSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Potentially dangerous command detected: requires user confirmation"
  }
}
ENDJSON
    exit 0
fi

exit 0
```

### 3. Protected File Guard

Blocks writes to lock files, git internals, and other files that should not be directly modified.

**Matcher:** `Write|Edit`
**Decision:** Hard block (deny)

```bash
#!/bin/bash
# hooks/danger-file-protection.sh
# Trigger: PreToolUse | Matcher: Write|Edit
# Blocks modifications to lock files, git internals, and protected configs

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Protected file patterns
if echo "$FILE_PATH" | grep -qiE '\.git/|package-lock\.json$|yarn\.lock$|Cargo\.lock$|poetry\.lock$|pnpm-lock\.yaml$'; then
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Protected file cannot be modified: '"$FILE_PATH"'"}}'
    echo "BLOCKED: Protected file cannot be modified: $FILE_PATH" >&2
    exit 2
fi

exit 0
```

### 4. Destructive Git Operations Gate

Prompts for confirmation before force-push, hard reset, force-delete branches, and other destructive git commands.

**Matcher:** `Bash`
**Decision:** Soft gate (ask)

```bash
#!/bin/bash
# hooks/danger-git-destructive.sh
# Trigger: PreToolUse | Matcher: Bash
# Prompts confirmation for destructive git operations

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
    exit 0
fi

DANGEROUS_GIT=0
echo "$COMMAND" | grep -qiE 'git\s+push.*--force' && DANGEROUS_GIT=1
echo "$COMMAND" | grep -qiE 'git\s+push.*\s-f\b' && DANGEROUS_GIT=1
echo "$COMMAND" | grep -qiE 'git\s+reset\s+--hard' && DANGEROUS_GIT=1
echo "$COMMAND" | grep -qiE 'git\s+clean\s+-fd' && DANGEROUS_GIT=1
echo "$COMMAND" | grep -qiE 'git\s+checkout.*--force' && DANGEROUS_GIT=1
echo "$COMMAND" | grep -qiE 'git\s+branch\s+-D' && DANGEROUS_GIT=1
echo "$COMMAND" | grep -qiE 'git\s+rebase.*-f' && DANGEROUS_GIT=1

if [[ "$DANGEROUS_GIT" -eq 1 ]]; then
    cat <<ENDJSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Destructive git operation detected: $COMMAND"
  }
}
ENDJSON
    exit 0
fi

exit 0
```

### 5. Network Operation Confirmation

Prompts before curl, wget, ssh, and other network commands that reach external systems.

**Matcher:** `Bash`
**Decision:** Soft gate (ask)

```bash
#!/bin/bash
# hooks/danger-network-confirm.sh
# Trigger: PreToolUse | Matcher: Bash
# Prompts confirmation for network operations

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
    exit 0
fi

if echo "$COMMAND" | grep -qiE '^(curl|wget|nc |netcat|ssh |scp |rsync |ftp )'; then
    cat <<ENDJSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Network command requires confirmation: $COMMAND"
  }
}
ENDJSON
    exit 0
fi

exit 0
```

### 6. System Path Protection

Blocks writes to OS-level directories (/etc, /usr, /bin, /sys, /proc, /boot).

**Matcher:** `Write|Edit|Bash`
**Decision:** Hard block for Write/Edit, soft gate for Bash

```bash
#!/bin/bash
# hooks/danger-system-paths.sh
# Trigger: PreToolUse | Matcher: Write|Edit|Bash
# Blocks or gates operations targeting system paths

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

is_system_path() {
    echo "$1" | grep -qiE '^/(etc|usr|bin|sbin|boot|sys|proc)/' && return 0
    echo "$1" | grep -qiE '^C:\\Windows|^C:\\Program Files' && return 0
    return 1
}

if [[ "$TOOL_NAME" == "Bash" ]]; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
    if is_system_path "$COMMAND"; then
        cat <<'ENDJSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "System path operation requires confirmation"
  }
}
ENDJSON
        exit 0
    fi
else
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
    if [[ -n "$FILE_PATH" ]] && is_system_path "$FILE_PATH"; then
        echo "BLOCKED: Cannot modify system file: $FILE_PATH" >&2
        exit 2
    fi
fi

exit 0
```

### 7. Permission Change Confirmation

Prompts before chmod, chown, chgrp, and ACL commands that alter file permissions.

**Matcher:** `Bash`
**Decision:** Soft gate (ask)

```bash
#!/bin/bash
# hooks/danger-permission-change.sh
# Trigger: PreToolUse | Matcher: Bash
# Prompts confirmation for permission-changing commands

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
    exit 0
fi

if echo "$COMMAND" | grep -qiE '^(chmod|chown|chgrp|setfacl|icacls|takeown|cacls)'; then
    cat <<ENDJSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Permission change requires confirmation: $COMMAND"
  }
}
ENDJSON
    exit 0
fi

exit 0
```

## Input Validation Patterns

### Path Traversal Prevention

Always validate file paths before using them in hook logic:

```bash
validate_path() {
    local path="$1"

    # Reject empty paths
    [[ -z "$path" ]] && return 1

    # Reject path traversal
    echo "$path" | grep -q '\.\.' && return 1

    # Reject null bytes
    echo "$path" | grep -qP '\x00' && return 1

    # Reject shell metacharacters (command injection prevention)
    echo "$path" | grep -qE '[;&|`$(){}[\]<>!\\]' && return 1

    return 0
}
```

### Command Injection Prevention

Never pass tool_input values into shell commands without sanitization:

```bash
# BAD — command injection via tool_input
eval "$COMMAND"
bash -c "$COMMAND"

# GOOD — pattern match only, never execute
echo "$COMMAND" | grep -qiE 'rm\s+-rf'
```

## Settings Configuration

### Minimal Security Setup

Deploy the two highest-value guards (sensitive files + destructive git):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "command": ".claude/hooks/block-sensitive-files.sh"
      },
      {
        "matcher": "Bash",
        "command": ".claude/hooks/danger-git-destructive.sh"
      }
    ]
  }
}
```

### Full Security Suite

Deploy all 7 protection hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "command": ".claude/hooks/block-sensitive-files.sh"
      },
      {
        "matcher": "Write|Edit",
        "command": ".claude/hooks/danger-file-protection.sh"
      },
      {
        "matcher": "Write|Edit|Bash",
        "command": ".claude/hooks/danger-system-paths.sh"
      },
      {
        "matcher": "Bash",
        "command": ".claude/hooks/danger-bash-confirm.sh"
      },
      {
        "matcher": "Bash",
        "command": ".claude/hooks/danger-git-destructive.sh"
      },
      {
        "matcher": "Bash",
        "command": ".claude/hooks/danger-network-confirm.sh"
      },
      {
        "matcher": "Bash",
        "command": ".claude/hooks/danger-permission-change.sh"
      }
    ]
  }
}
```

### Global vs Project Scope

```bash
# Global hooks (all projects) — place in:
~/.claude/settings.json

# Project hooks (this repo only) — place in:
.claude/settings.json

# Recommendation: deploy block-sensitive-files and danger-git-destructive
# globally. Add project-specific hooks as needed.
```

## Deployment Checklist

When setting up security hooks for a project:

1. Create the hooks directory: `mkdir -p .claude/hooks`
2. Copy desired hook scripts into `.claude/hooks/`
3. Make them executable: `chmod +x .claude/hooks/*.sh`
4. Verify `jq` is installed (required for stdin JSON parsing)
5. Add hook entries to `.claude/settings.json`
6. Test each hook with sample input:
   ```bash
   echo '{"tool_name":"Write","tool_input":{"file_path":".env.local"}}' | bash .claude/hooks/block-sensitive-files.sh
   echo "Exit code: $?"
   ```
7. Commit the hooks directory and settings to version control

## Constraints

- Hooks are system-level — Claude cannot disable or bypass them
- PreToolUse hooks must be fast (under 5 seconds) — they block tool execution
- Exit code 1 means hook crashed — tool proceeds (fail-open by design)
- Multiple hooks on the same matcher run in order — first block wins
- Hook stderr is shown to Claude as the block reason
- The `jq` command is required for all hook scripts — verify it is installed
- JSON decision output goes to stdout; human-readable block messages go to stderr
