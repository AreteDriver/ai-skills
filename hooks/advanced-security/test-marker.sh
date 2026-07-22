#!/usr/bin/env bash
# test-marker.sh — PostToolUse(Bash): maintain the TDD marker from test runs.
#
# Sets /tmp/.claude-tests-passed when a recognized test command appears to pass,
# and removes it when one appears to fail. Paired with tdd-guard.sh (PreToolUse),
# this enforces "tests must pass before commit" without manual marker juggling.
#
# Detection is heuristic (fail signals checked first, conservatively). Only acts
# on recognized test runners; everything else is a no-op.

set -uo pipefail

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)
RESPONSE=$(printf '%s' "$INPUT" | jq -r '(.tool_response // .tool_result // "") | tostring' 2>/dev/null || true)
MARKER="/tmp/.claude-tests-passed"

# Only react to recognized test commands.
case "$COMMAND" in
    *pytest*|*"npm test"*|*"npm run test"*|*"pnpm test"*|*"yarn test"*|*"cargo test"*|*"go test"*|*jest*|*vitest*|*"make test"*) ;;
    *) exit 0 ;;
esac

# Fail signals win (clear the marker — require a fresh pass before committing).
if printf '%s' "$RESPONSE" | grep -qiE 'failed|error|assertionerror|panic|[1-9][0-9]* failing|exit code [1-9]'; then
    rm -f "$MARKER"
elif printf '%s' "$RESPONSE" | grep -qiE '[0-9]+ passed|all tests passed|tests? passed|test suites?:[^x]*passed|\bPASS\b'; then
    touch "$MARKER"
fi

exit 0
