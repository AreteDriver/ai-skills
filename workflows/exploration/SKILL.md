---
name: exploration
description: Exploration-mode prompt scaffold. Use when the option space isn't mapped yet — generate distinct alternatives, surface unknowns, challenge assumptions. The output is a list of options with evidence, not a recommendation. Invoke with /exploration.
---

# Exploration Mode

Load the full template from `~/projects/animus/packages/forge/prompts/modes/exploration.md` and use it as the structural contract for the output you produce.

## Process

1. **Gather INPUTS from the user.** If any are missing, ask for them before proceeding. Do not guess. Required slots:
   - `objective` — what the user is trying to decide
   - `context` — known facts, non-negotiable constraints
   - `assumptions` — what the user currently believes (flag for challenge)
   - `evidence base` — docs, data, prior decisions to draw from
   - `exclusions` — already-rejected paths, out-of-scope options

2. **Produce the output in the exact OUTPUT FORMAT** specified in exploration.md:
   - Option table: id | name | premise | cheapest proof | biggest risk
   - Three highest-leverage unknowns (with cheap tests)
   - Three stated assumptions that may not hold (with tests)
   - One-paragraph synthesis of the option space

3. **Honor the FAILURE CONDITIONS** — before emitting, self-check:
   - Any two options that are variants of the same idea → collapse or replace
   - "It depends" without naming the variable → re-state explicitly
   - Recommending a winner → stop, you're in the wrong mode
   - No unknowns surfaced → suspicious, re-examine

## Anti-pattern

Do not blend this with Evaluation mode. Exploration generates and names; it does not rank or decide. If the user wants a pick, they should invoke `/evaluation` on the output of this session.

## Scoring

If the user wants to score this output against the personal-quality rubric, suggest:

```bash
animus-forge eval run <suite> --rubric personal-quality --prompt-version exploration-v1
```

Weights that matter most for Exploration outputs: `precision` (specific options, not generic), `evidence_quality` (options tied to inputs), `actionability` (each unknown has a cheap test).
