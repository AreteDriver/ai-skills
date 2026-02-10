#!/bin/bash
# Hook: Tool Usage Logger
# Event: PostToolUse
# Matcher: *
# Purpose: Logs all tool invocations for audit and analysis
#
# Install in .claude/settings.json:
# {
#   "hooks": {
#     "PostToolUse": [
#       { "matcher": "*", "command": "./hooks/tool-logger.sh" }
#     ]
#   }
# }

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
