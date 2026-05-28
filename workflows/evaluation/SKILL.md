---
name: evaluation
description: Evaluation-mode prompt scaffold. Use when you have candidates (options, outputs, PRs, copy variants, vendors) and need a scored comparison with a verdict — not opinions. Always produces a decision plus evidence. "It depends" is not an acceptable output. Invoke with /evaluation.
---

# Evaluation Mode

Load the full template from `~/projects/animus/packages/forge/prompts/modes/evaluation.md` and use it as the structural contract.

## Process

1. **Gather INPUTS from the user.** Ask for anything missing before scoring — fabricating inputs is the top failure mode for this mode. Required slots:
   - `candidates` — the N things being compared
   - `rubric` — weighted criteria (name, weight, what high/low means). If the user doesn't have one, suggest a rubric from `~/projects/animus/packages/forge/rubrics/` (e.g. `personal-quality`) or help them author one.
   - `acceptance` — what a passing composite looks like (floor score, per-dim minimums)
   - `evidence base` — inputs the evaluation must cite
   - `exclusions` — criteria NOT to score (keeps scope tight)

2. **Produce OUTPUT FORMAT in order** from evaluation.md:
   1. Scored table (candidate × dim → composite)
   2. Evidence per score (one-line citation per cell)
   3. Top 3 weaknesses per candidate (specific, tied to dim scores)
   4. Top 3 strengths per candidate
   5. Decision: [pursue: X] | [pursue selectively: X with conditions] | [pass: none qualify]
   6. Conditions (if "pursue selectively")
   7. "What would change the decision": the single piece of new evidence that would flip the verdict

3. **Honor FAILURE CONDITIONS** — self-check before emitting:
   - Any score without cited evidence → add it or drop the score
   - "It depends" without naming the deciding variable → name it
   - Weaknesses stated as categories ("scalability issues") → rewrite as specifics ("no caching at L3")
   - Scope-creep dims not in the input rubric → drop them
   - Verdict that restates the question → wrong mode, go to Exploration
   - Winner's weaknesses omitted → add them

## Adversarial extension (optional)

After the first pass, the user may request an adversarial re-score:

> "Attack the previous evaluation. Assume a hostile reviewer. List the 5 weakest scores and the 3 most questionable evidence citations. Revise only those."

Apply this when stakes justify it (hiring, architecture calls, vendor contracts). Skip on low-stakes scoring — judge-disagreement noise dominates at small sample sizes.

## Scoring

Evaluation outputs themselves get scored against personal-quality:

```bash
animus-forge eval run <suite> --rubric personal-quality --prompt-version evaluation-v1
```

Weights that matter: `actionability` (must produce a decision), `evidence_quality` (every score cited), `precision` (specific weaknesses, not categories), `format_compliance` (scored table structure).
