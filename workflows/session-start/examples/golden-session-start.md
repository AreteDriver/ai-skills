# Golden Example: Session Start Report

Demonstrates a concise, actionable orientation summary with project health,
pending work, and template recommendation.

## Input Context

- Project: ai-skills
- Branch: main
- Uncommitted: 2 files
- Last commit: 051b7cd — feat(eval): add golden-mode scoring
- CLAUDE.md: present, score 85/100
- Pending: 0 open issues, 0 open PRs
- User objective: "Continue extending eval coverage"

## Expected Session Start Output

```markdown
## Session Start: ai-skills

**Project:** ai-skills (AI skill catalog and installer)
**Branch:** main (0 ahead, 0 behind)
**Health:** OK — no failing CI, clean working tree (2 uncommitted files)
**Context:** CLAUDE.md 85/100
**Pending:** 0 issues, 0 PRs, 0 failing runs
**Suggested Template:** MASTER_SESSION_TEMPLATE
**Next Action:** Run `python3 scripts/run-evals.py --all --mode golden` to verify current eval suite

### Uncommitted Changes
- `scripts/run-evals.py` — eval runner scoring improvements
- `evals/reports/quality-card-golden.md` — updated report

### Recent History
- `051b7cd` feat(eval): add golden-mode scoring with content, structure, reasoning, safety
- `7fbc296` ci: add behavioral evals and installer tests to CI
- `be840fd` feat: add behavioral eval runner

### Open Questions
- Extend eval cases to agents/workflows next?
- Implement live-mode API execution after golden coverage is solid?
```

## Why This Session Start Is Good

1. **Under 20 lines** — concise summary at the top
2. **Actionable next action** — exact command to run
3. **Honest health status** — flags uncommitted files without alarm
4. **Template recommendation** — MASTER_SESSION_TEMPLATE fits exploratory work
5. **Recent history included** — gives continuity without dumping full log
6. **No implementation** — strictly orientation, no file modifications suggested
