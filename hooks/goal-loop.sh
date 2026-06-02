#!/usr/bin/env bash
# goal-loop.sh — UserPromptSubmit: inject build-mode goal discipline when a
# `.goal-active` sentinel is present at the repo root. Silent/inert otherwise.
#
# Engagement is opt-in via:
#   - /production  (code/build deliverables only) -> mode: engaged
#   - /specification (code/build deliverables only) -> mode: armed (advisory)
#   - /goal "<objective>"                            -> mode: engaged
# Cleared by /exploration and /evaluation (sentinel removed).
#
# Spend signal: ai-spend has no in-session USD, so the automatic backstop is a
# turn counter (turn_ceiling). Real USD can be logged with `/goal spend <usd>`
# and is honored against budget_ceiling_usd. Either ceiling triggers the
# checkpoint.
#
# Hard override anywhere: export GOAL_LOOP_OFF=1
set -uo pipefail

[ "${GOAL_LOOP_OFF:-}" = "1" ] && exit 0

# Drain stdin (event payload) even if unused, so the writer never blocks.
cat >/dev/null 2>&1 || true

repo_root=$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)
[ -z "$repo_root" ] && exit 0
SENTINEL="$repo_root/.goal-active"
[ ! -f "$SENTINEL" ] && exit 0

# Flat key:value parse; fail-open on anything malformed.
val() { sed -nE "s/^$1:[[:space:]]*(.*)$/\1/p" "$SENTINEL" 2>/dev/null | head -1; }

mode=$(val mode)
objective=$(val objective)
stop_condition=$(val stop_condition)
budget=$(val budget_ceiling_usd)
turn_ceiling=$(val turn_ceiling)
turns=$(val turns)
spent=$(val spent_usd)

# Fail-open: missing core fields -> behave as if no sentinel.
[ -z "$mode" ] && exit 0
[ -z "$objective" ] && exit 0

emit() { jq -nc --arg ctx "$1" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$ctx}}'; }

if [ "$mode" = "armed" ]; then
    emit "BUILD-MODE (armed — specification). Objective: ${objective}. Stop condition: ${stop_condition:-<undefined>}. ADVISORY ONLY: keep the spec tight against this objective; do NOT begin autonomous build looping yet. The goal-loop fully engages at /production."
    exit 0
fi

if [ "$mode" = "engaged" ]; then
    turns=${turns:-0}; turn_ceiling=${turn_ceiling:-25}; spent=${spent:-0}; budget=${budget:-10}

    # Increment turn counter (atomic-ish via temp; fail-open).
    new_turns=$((turns + 1))
    tmp=$(mktemp 2>/dev/null) && {
        sed -E "s/^turns:.*/turns: ${new_turns}/" "$SENTINEL" > "$tmp" 2>/dev/null && mv "$tmp" "$SENTINEL" 2>/dev/null || rm -f "$tmp" 2>/dev/null
    }
    turns=$new_turns

    over_turns=0; over_usd=0
    [ "$turns" -ge "$turn_ceiling" ] 2>/dev/null && over_turns=1
    awk "BEGIN{exit !(($spent)+0 >= ($budget)+0)}" 2>/dev/null && over_usd=1

    if [ "$over_turns" = "1" ] || [ "$over_usd" = "1" ]; then
        emit "GOAL CHECKPOINT REACHED (turns ${turns}/${turn_ceiling}, logged \$${spent}/\$${budget}). PAUSE autonomous progress now. Report against the objective: (1) what is done, (2) what remains vs the stop condition '${stop_condition:-<undefined>}', (3) ROI so far, (4) recommend continue / pivot / kill. Do NOT continue building without explicit operator confirmation. Extend with: /goal extend."
    else
        emit "BUILD-MODE GOAL (engaged). Objective: ${objective}. Stop condition: ${stop_condition:-<undefined>}. Budget: turn ${turns}/${turn_ceiling}, logged \$${spent}/\$${budget}. Drive toward the stop condition; halt and ask only when you reach it or are genuinely blocked. Destructive ops require approval (goal-gate)."
    fi
    exit 0
fi

exit 0
