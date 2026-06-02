#!/usr/bin/env bash
# Acceptance tests for goal-loop.sh + goal-gate.sh (spec §5).
# Runs each hook against a throwaway git repo with synthetic sentinels + stdin.
set -uo pipefail

HOOK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOOP="$HOOK_DIR/goal-loop.sh"
GATE="$HOOK_DIR/goal-gate.sh"
PASS=0; FAIL=0

work=$(mktemp -d)
cd "$work" || exit 1
git init -q
SENT="$work/.goal-active"

pass() { PASS=$((PASS+1)); echo "PASS: $1"; }
fail() { FAIL=$((FAIL+1)); echo "FAIL: $1 :: got [$2]"; }
has()  { printf '%s' "$2" | grep -q "$3" && pass "$1" || fail "$1" "$2"; }
empty(){ [ -z "$2" ] && pass "$1" || fail "$1" "$2"; }

engaged_sentinel() {
cat > "$SENT" <<EOF
objective: ship the thing
stop_condition: all tests green
budget_ceiling_usd: 10
turn_ceiling: ${1:-25}
turns: ${2:-0}
spent_usd: ${3:-0}
mode: engaged
started_at: 2026-06-02T00:00:00Z
EOF
}

# 1. no sentinel -> no injection
rm -f "$SENT"
out=$(echo '{"prompt":"hi"}' | bash "$LOOP")
empty "test_no_sentinel_no_injection" "$out"

# 2. engaged -> injection names objective + engaged
engaged_sentinel 25 0 0
out=$(echo '{"prompt":"hi"}' | bash "$LOOP")
has "test_engaged_injects_objective" "$out" "ship the thing"
has "test_engaged_mode_marked" "$out" "engaged"

# 3. armed -> advisory, no autonomous-continue
rm -f "$SENT"
{ echo "objective: design it"; echo "stop_condition: TBD"; echo "mode: armed"; } > "$SENT"
out=$(echo '{"prompt":"hi"}' | bash "$LOOP")
has "test_armed_is_advisory" "$out" "armed"

# 4. ceiling -> checkpoint (turn_ceiling 1, fresh -> increments to 1 >= 1)
engaged_sentinel 1 0 0
out=$(echo '{"prompt":"hi"}' | bash "$LOOP")
has "test_turn_ceiling_pauses" "$out" "CHECKPOINT REACHED"

# 4b. usd ceiling -> checkpoint
engaged_sentinel 25 0 10
out=$(echo '{"prompt":"hi"}' | bash "$LOOP")
has "test_usd_ceiling_pauses" "$out" "CHECKPOINT REACHED"

# 5. malformed -> fail-open (no mode/objective)
rm -f "$SENT"; printf 'garbage!!!\n::::\n' > "$SENT"
out=$(echo '{"prompt":"hi"}' | bash "$LOOP")
empty "test_malformed_fails_open" "$out"

# 6. gate: engaged + destructive -> ask
engaged_sentinel 25 0 0
out=$(printf '{"tool_input":{"command":"git push origin main"}}' | bash "$GATE")
has "test_destructive_requires_approval" "$out" "ask"

# 7. gate: no sentinel + destructive -> no interference
rm -f "$SENT"
out=$(printf '{"tool_input":{"command":"git push origin main"}}' | bash "$GATE")
empty "test_no_sentinel_no_gate" "$out"

# 8. gate: engaged + benign -> no interference
engaged_sentinel 25 0 0
out=$(printf '{"tool_input":{"command":"ls -la"}}' | bash "$GATE")
empty "test_benign_passes_gate" "$out"

echo "-----"
echo "PASS=$PASS FAIL=$FAIL"
rm -rf "$work"
[ "$FAIL" -eq 0 ]
