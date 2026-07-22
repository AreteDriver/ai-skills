#!/bin/bash
#
# Security Hook: Log session start/end events.
# Provides audit trail for all Claude Code sessions.
#
# This hook runs on SessionStart and SessionEnd events.
#

set -euo pipefail

AUDIT_LOG="$HOME/.claude/audit-log.txt"

# Read JSON input from stdin
input=$(cat)

# Extract hook event name
hook_event=$(echo "$input" | jq -r '.hook_event_name // empty')

timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
session_id=$(echo "$input" | jq -r '.session_id // "unknown"')
working_dir=$(echo "$input" | jq -r '.working_directory // "unknown"')

case "$hook_event" in
    "SessionStart")
        echo "[$timestamp] [INFO] SESSION_START: Session $session_id started in $working_dir" >> "$AUDIT_LOG"
        echo "" # No output needed
        ;;
    "SessionEnd")
        echo "[$timestamp] [INFO] SESSION_END: Session $session_id ended" >> "$AUDIT_LOG"
        echo "" # No output needed
        ;;
    *)
        # Unknown event, just exit
        ;;
esac

exit 0
