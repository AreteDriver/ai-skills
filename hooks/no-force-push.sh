#!/bin/bash
# Hook: Force Push Guard
# Event: PreToolUse
# Matcher: Bash
# Purpose: Blocks force-push to protected branches (main, master, production)
#
# Install in .claude/settings.json:
# {
#   "hooks": {
#     "PreToolUse": [
#       { "matcher": "Bash", "command": "./hooks/no-force-push.sh" }
#     ]
#   }
# }

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -qE "git push.*(--force|-f)"; then
    if echo "$COMMAND" | grep -qE "(main|master|production|release)"; then
        echo "BLOCKED: Force-push to protected branch detected." >&2
        echo "Force-pushing to main/master/production/release is not allowed." >&2
        exit 2
    fi
fi

exit 0
