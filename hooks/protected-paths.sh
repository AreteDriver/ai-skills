#!/bin/bash
# Hook: Protected Paths
# Event: PreToolUse
# Matcher: Write,Edit
# Purpose: Blocks modifications to sensitive directories and files
#
# Install in .claude/settings.json:
# {
#   "hooks": {
#     "PreToolUse": [
#       { "matcher": "Write,Edit", "command": "./hooks/protected-paths.sh" }
#     ]
#   }
# }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=""

if [[ "$TOOL" == "Write" ]]; then
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
elif [[ "$TOOL" == "Edit" ]]; then
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
fi

# Exit early if no file path
if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

PROTECTED_PATTERNS=(
    "*/.git/*"
    "*/node_modules/*"
    "*/.env"
    "*/.env.*"
    "*/.ssh/*"
    "*/credentials*"
    "*/.gnupg/*"
    "*/.password-store/*"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == $pattern ]]; then
        echo "BLOCKED: Cannot modify protected path: $FILE_PATH" >&2
        echo "This file is in a protected directory. Remove it from the protected list if this is intentional." >&2
        exit 2
    fi
done

exit 0
