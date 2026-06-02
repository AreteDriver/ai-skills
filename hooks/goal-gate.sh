#!/usr/bin/env bash
# goal-gate.sh — PreToolUse(Bash): when a build-mode goal is ENGAGED, require
# explicit approval for destructive commands the autonomous loop might run.
# Inert unless `.goal-active` is engaged at the target repo root.
#
# Complements (does not replace) no-force-push / destructive-disk-guard /
# gh-merge-guard — this is the autonomous-loop escalation: while a goal drives
# unattended turns, ANY destructive op surfaces for confirmation.
#
# Hard override anywhere: export GOAL_LOOP_OFF=1
set -uo pipefail

[ "${GOAL_LOOP_OFF:-}" = "1" ] && exit 0

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)
[ -z "$COMMAND" ] && exit 0

# Resolve target repo (honor explicit `git -C <dir>`, else PWD).
target_dir=$(printf '%s' "$COMMAND" | sed -nE 's/.*git[[:space:]]+-C[[:space:]]+([^[:space:]]+).*/\1/p')
target_dir="${target_dir:-$PWD}"
repo_root=$(git -C "$target_dir" rev-parse --show-toplevel 2>/dev/null || true)
[ -z "$repo_root" ] && exit 0

SENTINEL="$repo_root/.goal-active"
[ ! -f "$SENTINEL" ] && exit 0
mode=$(sed -nE 's/^mode:[[:space:]]*(.*)$/\1/p' "$SENTINEL" 2>/dev/null | head -1)
[ "$mode" != "engaged" ] && exit 0

# Destructive patterns the autonomous loop must not run unattended.
case "$COMMAND" in
    *"git push"*|*"git reset --hard"*|*"git clean "*|*"--force"*|*"--force-with-lease"*|\
    *"rm -rf"*|*"rm -r "*|"rm "*|*" rm "*|*"wipefs"*|*"mkfs"*|*"dd of="*|\
    *"drop table"*|*"DROP TABLE"*|*"truncate "*|*"TRUNCATE "*)
        jq -nc '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:"Build-mode goal-loop is ENGAGED: this is a destructive action. Confirm explicitly before the autonomous loop proceeds."}}'
        exit 0
        ;;
esac
exit 0
