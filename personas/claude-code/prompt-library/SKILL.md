---
name: prompt-library
description: Extract effective prompts from the current session and save them to a reusable library. Captures prompts that worked well for future reference. Invoke with /prompt-library or /prompts.
---

# Prompt Library Skill

Extract and save effective prompts from work sessions.

## Process

1. **Scan session** for prompts that:
   - Achieved the desired outcome efficiently
   - Used clever techniques or patterns
   - Could be reused for similar tasks
   - Demonstrated good prompt engineering

2. **Categorize** each prompt:
   - `CODE` - Code generation, refactoring, debugging
   - `REVIEW` - Code review, architecture analysis
   - `DOCS` - Documentation, READMEs, comments
   - `TEST` - Test generation, coverage
   - `DEPLOY` - CI/CD, packaging, deployment
   - `DESIGN` - UI/UX, system design
   - `DATA` - Data processing, analysis
   - `META` - Prompts about prompting

3. **Extract template** - generalize specifics into placeholders

4. **Pre-write format-match check** (mandatory):
   - Run `grep -E '^### P-' ~/projects/DecisionLog/PROMPTS.md | head -3` to confirm the target file already contains `P-YYYYMMDD-###` entries.
   - If the file has zero `P-` entries OR has entries in a different format (e.g., named templates without P-IDs), STOP. The destination has drifted. Surface to user: "PROMPTS.md format doesn't match the skill's catalog shape (P-IDs + Category field). Which file should I write to, or should we re-route the skill?"
   - This catches path-drift before silently writing into the wrong file. Discovered 2026-05-23 — the public-notes `PROMPTS.md` is a *templates* file, NOT a catalog; writing P-ID entries there would corrupt it.

5. **Append to** `~/projects/DecisionLog/PROMPTS.md` (in the private repo `AreteDriver/DecisionLog`). This is the skill's design target: P-IDs + Category field + the same CODE/REVIEW/DOCS/TEST/DEPLOY/DESIGN/DATA/META vocabulary as the Categories table above. A separate file at `~/projects/notes/PROMPTS.md` exists for *named template scaffolds* (Universal, CI/CD Diagnostic, GitHub Profile, etc.) — that one is hand-maintained, not a /prompt-library target.

## Entry Format

```markdown
### P-YYYYMMDD-###: [Short Title]
**Category:** [CODE|REVIEW|DOCS|TEST|DEPLOY|DESIGN|DATA|META]
**Context:** [When to use this]

**Prompt:**
```
[The prompt text with {{placeholders}} for variable parts]
```

**Why it works:**
- [Key technique 1]
- [Key technique 2]

**Example use:**
[Brief example of how it was used]
```

## What to Extract

Good candidates:
- Prompts that got it right first try
- Novel approaches to common problems
- Prompts with good constraint specification
- Multi-step workflows that worked well
- Effective few-shot examples

Skip:
- Simple one-off requests
- Prompts that needed multiple corrections
- Context-heavy prompts that won't generalize

## Prompt Patterns to Look For

1. **Constraint sandwich**: Context → Constraints → Task
2. **Output format spec**: Explicit structure requests
3. **Role assignment**: "Act as X with Y years experience"
4. **Negative examples**: "Do NOT do X"
5. **Step-by-step**: Breaking complex tasks into phases
6. **Few-shot**: Examples before the actual request
