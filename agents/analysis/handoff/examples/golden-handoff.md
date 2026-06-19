# Golden Example: AI Agent Handoff

Demonstrates a complete, actionable handoff document with exact next step,
uncommitted changes, and git context.

## Input Context

- Branch: `feat/eval-runner-live-mode`
- Uncommitted: `scripts/run-evals.py`, `evals/reports/quality-card-golden.md`
- Last commit: `051b7cd feat(eval): add golden-mode scoring`
- Active plan: `.claude/plans/phase-3-eval-runner.md`
- Next: extend eval cases to agents/workflows

## Expected Handoff Output

```markdown
# Handoff: ai-skills — 2026-06-19T12:00:00Z

## Current State
Completed Phase 0–3 remediation. Eval runner now scores golden examples
against content, structure, reasoning, and safety criteria. 5 personas
have eval cases; next extension is agents and workflows.

## Active Context
- Eval runner uses per-criterion weighted scoring (correctness, structure, reasoning, safety)
- Safety check refined to avoid false positives on security audit content
- Reports generated to `evals/reports/quality-card-{mode}.md`

## Branch & Changes
- Branch: `feat/eval-runner-live-mode`
- Uncommitted: yes
  - `scripts/run-evals.py` — eval runner with scoring logic
  - `evals/reports/quality-card-golden.md` — generated report
- Last commit: `051b7cd feat(eval): add golden-mode scoring`

## Blocked / Waiting
- None

## Immediate Next Action
Add eval cases for `agents/analysis/handoff` and `workflows/session-start`.
Create golden examples in `examples/` and case YAMLs in `evals/`.

## Files Modified This Session
| File | What Changed |
|------|-------------|
| `scripts/run-evals.py` | Added content/structure/reasoning/safety scoring |
| `evals/reports/quality-card-golden.md` | Generated golden-mode report |

## Open Questions
- Should live-mode API execution be implemented next?
- How many additional skills should get eval cases before 7.5→8.0 push?

## Relevant Context
- Safety checker uses substring matching; may need regex for more precision
- Thresholds are per-case: 0.85–1.0 depending on skill criticality
```

## Why This Handoff Is Good

1. **Next action is exact** — specifies which skills and which directories
2. **Git state is precise** — branch name, uncommitted files, last commit hash
3. **No file contents** — only paths and summaries, keeping it lightweight
4. **Blocked section exists even when empty** — consistent format
5. **Timestamped** — ISO8601 for machine parsing
6. **Audience-aware** — structured for an AI agent to resume immediately
