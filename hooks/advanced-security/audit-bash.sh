#!/bin/bash
#
# Security Hook: Audit and log bash commands executed by Claude.
# Blocks dangerous commands that could harm the system.
#

AUDIT_LOG="$HOME/.claude/audit-log.txt"

# Function to log events
log_audit() {
    local severity="$1"
    local event_type="$2"
    local message="$3"
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] [$severity] $event_type: $message" >> "$AUDIT_LOG" 2>/dev/null || true
}

# Read JSON input from stdin
input=$(cat)

# Extract fields using jq (with error handling)
hook_event=$(echo "$input" | jq -r '.hook_event_name // empty' 2>/dev/null) || hook_event=""
tool_name=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null) || tool_name=""
command=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || command=""

# Only process PreToolUse events for Bash tool
if [ "$hook_event" != "PreToolUse" ] || [ "$tool_name" != "Bash" ] || [ -z "$command" ]; then
    exit 0
fi

# Log the command
log_audit "INFO" "BASH_COMMAND" "$command"

# Function to check exact string match (case insensitive)
contains_exact() {
    echo "$1" | grep -qiF "$2" 2>/dev/null
}

# Function to check regex match
contains_regex() {
    echo "$1" | grep -qiE "$2" 2>/dev/null
}

# Block helper function
block_command() {
    local pattern="$1"
    log_audit "CRITICAL" "BLOCKED_COMMAND" "Blocked dangerous command matching: $pattern"
    cat << EOF
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Security policy violation: This command matches a dangerous pattern and has been blocked."
    }
}
EOF
    exit 0
}

# ============================================
# DANGEROUS COMMAND CHECKS
# ============================================

# Destructive filesystem operations
contains_exact "$command" "rm -rf /" && block_command "rm -rf /"
contains_exact "$command" "rm -rf /*" && block_command "rm -rf /*"
contains_exact "$command" "rm -rf ~" && block_command "rm -rf ~"
contains_exact "$command" 'rm -rf $HOME' && block_command 'rm -rf $HOME'
contains_exact "$command" "rm -rf /home" && block_command "rm -rf /home"
contains_exact "$command" "rm -fr /" && block_command "rm -fr /"

# Fork bombs
contains_exact "$command" ":(){ :|:& };:" && block_command "fork bomb"

# Dangerous permission changes
contains_exact "$command" "chmod -R 777 /" && block_command "chmod -R 777 /"
contains_exact "$command" "chmod 777 /" && block_command "chmod 777 /"

# Network attacks
contains_exact "$command" "nc -e" && block_command "netcat exec"
contains_exact "$command" "/dev/tcp/" && block_command "/dev/tcp"

# Credential theft
contains_exact "$command" "cat /etc/shadow" && block_command "cat /etc/shadow"

# History manipulation
contains_exact "$command" "history -c" && block_command "history clear"
contains_exact "$command" "export HISTFILE=/dev/null" && block_command "disable history"
contains_exact "$command" "unset HISTFILE" && block_command "unset history"

# dd to disk devices
contains_regex "$command" "dd if=/dev/(zero|random|urandom) of=/dev/sd" && block_command "dd to disk"

# mkfs on devices
contains_regex "$command" "mkfs\.[a-z]+ /dev/sd" && block_command "mkfs on disk"

# Reverse shells
contains_regex "$command" "bash -i.*>&.*/dev/tcp" && block_command "reverse shell"

# Dangerous curl/wget piped to shell.
# Match the pipe + shell-command pattern tightly: `| sh`, `| bash`, `|bash -c ...`
# etc. — sh/bash must appear as a command token directly after the pipe, not as a
# substring of a later word (e.g. avoids false-positives on `curl ... | grep dashboard`).
contains_regex "$command" "curl([[:space:]]|$).*\|[[:space:]]*(sh|bash)([[:space:]]|;|&|\||$)" && block_command "curl pipe to shell"
contains_regex "$command" "wget([[:space:]]|$).*\|[[:space:]]*(sh|bash)([[:space:]]|;|&|\||$)" && block_command "wget pipe to shell"

# ============================================
# LLM CLIENT CONFIG PROTECTION (added 2026-04-20)
# ============================================
# Block rm of critical Claude Code / Cursor / Windsurf config files.
# Prevents accidental wipes by agents — on 2026-04-18 an agent ran
# `rm ~/.claude/mcp.json ~/.cursor/mcp.json ~/.codeium/.../mcp_config.json`
# across three clients, including deleting memboot's auto-backup, losing
# 5 MCP server definitions silently. Recovery required manually reconstructing
# the file from prior session transcripts.

for _cfg_pat in \
    '/\.claude/mcp\.json' \
    '/\.claude/\.mcp\.json' \
    '/\.claude/settings\.json' \
    '/\.claude/settings\.local\.json' \
    '/\.claude/keybindings\.json' \
    '/\.claude/CLAUDE\.md' \
    '/\.cursor/mcp\.json' \
    '/\.codeium/[^[:space:]]+/mcp_config\.json'
do
    if echo "$command" | grep -qiE "(^|[[:space:]]|/)rm[[:space:]]+.*${_cfg_pat}([[:space:]]|$|;|&|\|)" 2>/dev/null; then
        block_command "rm of protected LLM client config (${_cfg_pat})"
    fi
done

# Block rm of .env / .env.<name> files
if echo "$command" | grep -qiE "(^|[[:space:]]|/)rm[[:space:]]+.*/\.env(\.[a-z_]+)?([[:space:]]|$|;|&|\|)" 2>/dev/null; then
    block_command "rm of .env file"
fi

# ============================================
# PARANOID EXTENSIONS (added 2026-04-20)
# ============================================
# Catches agent workarounds that bypass plain rm:
#   - find ... -delete on protected trees
#   - mv <protected> ... (equivalent blast radius to rm)
#   - output redirection (> or >>) clobbering protected config files

# find -delete rooted at a whole protected dir (blocks wipes of the tree).
# Subdir targets like find ~/.claude/logs -delete are allowed — legit cleanup.
# Path may be absolute (/home/user/.claude) or tilde-relative (~/.claude).
if echo "$command" | grep -qiE "find[[:space:]]+[^[:space:]]*\.(claude|cursor|codeium|config)[[:space:]]+.*-delete" 2>/dev/null; then
    block_command "find -delete on whole LLM client config tree"
fi
# find -delete with -name matching critical config filenames (any path).
if echo "$command" | grep -qiE "find[[:space:]].*-name[[:space:]]+["']?(mcp|settings|keybindings|\.mcp|mcp_config|CLAUDE)[^[:space:]]*\.(json|md)["']?.*-delete" 2>/dev/null; then
    block_command "find -delete targeting critical config filename"
fi

# mv of protected config files (same filenames as rm protection)
for _cfg_pat in \
    '/\.claude/mcp\.json' \
    '/\.claude/\.mcp\.json' \
    '/\.claude/settings\.json' \
    '/\.claude/settings\.local\.json' \
    '/\.claude/keybindings\.json' \
    '/\.claude/CLAUDE\.md' \
    '/\.cursor/mcp\.json' \
    '/\.codeium/[^[:space:]]+/mcp_config\.json'
do
    if echo "$command" | grep -qiE "(^|[[:space:]]|/)mv[[:space:]]+.*${_cfg_pat}([[:space:]]|$|;|&|\|)" 2>/dev/null; then
        block_command "mv of protected LLM client config (${_cfg_pat})"
    fi
done
if echo "$command" | grep -qiE "(^|[[:space:]]|/)mv[[:space:]]+.*/\.env(\.[a-z_]+)?([[:space:]]|$|;|&|\|)" 2>/dev/null; then
    block_command "mv of .env file"
fi

# Output redirection clobbering critical config files.
# Any > or >> targeting these paths is almost certainly an agent
# trying to reset state via shell rather than Edit tool. Block.
for _cfg_pat in \
    '/\.claude/mcp\.json' \
    '/\.claude/\.mcp\.json' \
    '/\.claude/settings\.json' \
    '/\.claude/settings\.local\.json' \
    '/\.claude/keybindings\.json' \
    '/\.claude/CLAUDE\.md' \
    '/\.cursor/mcp\.json' \
    '/\.codeium/[^[:space:]]+/mcp_config\.json'
do
    if echo "$command" | grep -qiE ">[[:space:]]*[^[:space:]]*${_cfg_pat}([[:space:]]|$|;|&|\|)" 2>/dev/null; then
        block_command "shell-redirect clobber of protected config (${_cfg_pat})"
    fi
done
if echo "$command" | grep -qiE ">[[:space:]]*[^[:space:]]*/\.env(\.[a-z_]+)?([[:space:]]|$|;|&|\|)" 2>/dev/null; then
    block_command "shell-redirect clobber of .env file"
fi

# Allow the command
exit 0
