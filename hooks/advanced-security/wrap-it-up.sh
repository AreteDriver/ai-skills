#!/bin/bash
# Hook: Wrap It Up trigger
# Event: UserPromptSubmit
# Purpose: Detects "wrap it up" or "wrap it up for now" in user prompts
#          and injects context telling Claude to invoke /session-end.
#
# Install in ~/.claude/settings.json:
# {
#   "hooks": {
#     "UserPromptSubmit": [
#       { "hooks": [{ "type": "command", "command": "/home/arete/.claude/hooks/wrap-it-up.sh" }] }
#     ]
#   }
# }

input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // empty')

if echo "$prompt" | grep -qiE 'wrap it up'; then
    cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "The user said 'wrap it up' (or 'wrap it up for now'). Invoke the /session-end skill NOW to run the full close-out workflow. Reference: ~/projects/ai-skills/workflows/session-end/SKILL.md. Steps: (1) inventory git changes across touched repos, (2) capture high-leverage decisions via /decision-log, (3) record gotchas/patterns to appropriate topic file or CC auto-memory, (4) sync Animus memory if relevant, (5) update ~/projects/notes/TODO.md, (6) write ~/projects/notes/sessions/YYYY-MM-DD.md (create if missing), (7) suggest a conventional commit message and await user confirmation before committing, (8) do NOT push without explicit approval. Respect any active code freezes."
  }
}
EOF
fi

exit 0
