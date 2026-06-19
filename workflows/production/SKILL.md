---
name: production
description: Production-mode prompt scaffold. Use when the decision is made and spec is clear — produce the final deliverable with no exploratory sprawl, no meta-commentary, no preamble. Output is the artifact itself, nothing else. Invoke with /production.
lifecycle: experimental
---

# Production Mode

Load the full template from `~/projects/animus/packages/forge/prompts/modes/production.md` and use it as the structural contract.

## Process

1. **Gather INPUTS from the user.** Missing slots are the #1 cause of filler output — ask before producing. Required slots:
   - `deliverable` — one artifact (email, PR description, landing copy, decision memo, code change)
   - `objective` — what the reader does after reading
   - `audience` — who reads it
   - `constraints` — measurable ("350 words", "≤ 3 bullets", "subject < 60 chars")
   - `voice / format` — existing pattern to match ("matches the tone of <reference>")
   - `evidence base` — every claim maps here; responsibilities from a role, bullets from a resume, commits from a PR
   - `exclusions` — must not appear (hedging, filler, generic adjectives)

2. **Produce the deliverable in the exact requested format.** Nothing else.
   - NO preamble ("Here is the email you requested...")
   - NO wrapper ("```" fences around prose that isn't code)
   - NO trailing sign-off unless requested
   - NO meta-commentary about the choices made

3. **Honor FAILURE CONDITIONS** — self-check before emitting:
   - Any exploratory language ("we could consider", "one option") → delete, wrong mode
   - Any meta ("I've structured this as...") → delete
   - Filler phrases ("it's worth noting", "importantly", "in essence") → delete
   - Unsourced quantifiers ("significantly improved X") → replace with a number from evidence OR delete
   - Soft-skill boilerplate ("strong communicator") → delete unless evidenced
   - Format violation (exceeded word count, missing section, wrong structure) → rewrite
   - Hedging the deliverable ("you may want to consider...") when a decision is requested → replace with the decision

## Anti-pattern: "make it better"

If the deliverable scores below band B on the personal-quality rubric, DO NOT respond to "make it better" — too vague, will regress or add filler. Instead:

1. Run the output through `/evaluation` against `personal-quality`
2. Identify the 3 lowest-scoring dims
3. Re-enter `/production` with those named in INPUTS.exclusions (e.g. "exclusions: generic adjectives flagged in prior pass: [list]")

Measured iteration beats "try again" prompts 2-4x in practice.

## Build-mode goal-loop (code/build deliverables ONLY)

If and only if `deliverable` is a code/build artifact (a module, feature, multi-file change, or system — **NOT** prose like an email, cover letter, copy, memo, or docs), ENGAGE the goal-loop by writing a `.goal-active` sentinel at the repo root:

```
objective: <INPUTS.objective, one line>
stop_condition: <falsifiable end state, from acceptance criteria>
budget_ceiling_usd: 10
turn_ceiling: 25
turns: 0
spent_usd: 0
mode: engaged
started_at: <ISO8601>
```

Then ensure `.goal-active` is git-ignored (add to `.gitignore` or `.git/info/exclude`). The `goal-loop` hook injects the objective + budget each turn and forces a checkpoint at the ceiling; `goal-gate` escalates destructive ops for approval. For prose deliverables, do **not** write the sentinel. Manage an active goal with `/goal`.

## Scoring

```bash
animus-forge eval run <suite> --rubric personal-quality --prompt-version production-v1
```

Weights that matter most: `format_compliance` (hit every format constraint), `precision` (no generic boilerplate), `concision` (every sentence earns its keep), `decision-clarity` (reader knows exactly what they're asked to do).
