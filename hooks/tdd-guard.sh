#!/bin/bash
# Hook: TDD Guard
# Event: PreToolUse
# Matcher: Bash
# Purpose: Blocks git commit if tests haven't passed in this session
#
# Install in .claude/settings.json:
# {
#   "hooks": {
#     "PreToolUse": [
#       { "matcher": "Bash", "command": "./hooks/tdd-guard.sh" }
#     ]
#   }
# }

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
