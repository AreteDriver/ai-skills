---
name: specification
description: Specification-mode prompt scaffold. Use when the decision is made and you need a buildable, testable, reviewable spec. Output is fixed-structure with measurable acceptance criteria. Never re-argues the premise. Invoke with /specification.
lifecycle: experimental
---

# Specification Mode

Load the full template from `~/projects/animus/packages/forge/prompts/modes/specification.md` and use it as the structural contract.

## Process

1. **Gather INPUTS from the user.** If any are missing, ask before producing the spec. Do not fill gaps with assumptions — that's a rubric-grade failure mode. Required slots:
   - `artifact` — the thing being specified (API, module, workflow, deliverable)
   - `objective` — what it must do, one sentence
   - `constraints` — explicit + measurable (e.g. "p95 latency < 200ms", not "fast")
   - `interfaces` — inputs consumed, outputs emitted (types, schemas)
   - `acceptance` — how we know it's done (test names, observable behaviors)
   - `evidence base` — prior art, reference implementations
   - `exclusions` — explicitly out of scope

2. **Produce the spec in OUTPUT FORMAT order** from specification.md:
   1. Summary (2-3 sentences)
   2. Requirements (MUST / MAY / MUST NOT)
   3. Constraints (each with a measurement method)
   4. Interfaces (typed schemas, error cases)
   5. Acceptance criteria (falsifiable)
   6. Out of scope (explicit)
   7. Open questions (labeled, decisions NOT injected)

3. **Honor FAILURE CONDITIONS** — self-check before emitting:
   - Any untestable requirement ("should be fast") → rewrite with a threshold
   - Any interface without error-case behavior → add it
   - Any exploratory language ("we could", "maybe") → you're in the wrong mode
   - Any implementation-detail leak in acceptance → replace with observable behavior

## Anti-pattern

Do not re-litigate the decision. If the user prompts with "but what if we did X instead?", stop and tell them to run `/evaluation` to re-open the decision. Specs get weaker every time they defend their own premise.

## Build-mode goal-loop (code/build artifacts ONLY)

If the `artifact` being specified is code/build (not a spec for non-code work), ARM the goal-loop by writing a `.goal-active` sentinel at the repo root with `mode: armed` — advisory only: it surfaces the objective each turn but does **not** start autonomous looping. Full engagement happens at `/production`.

```
objective: <objective, one line>
stop_condition: <acceptance summary, or "TBD at production">
budget_ceiling_usd: 10
turn_ceiling: 25
turns: 0
spent_usd: 0
mode: armed
started_at: <ISO8601>
```

Ensure `.goal-active` is git-ignored. Clear it via `/exploration`, `/evaluation`, or `/goal clear`.

## Scoring

```bash
animus-forge eval run <suite> --rubric code-edit --prompt-version specification-v1
```

For non-code specs, author a custom rubric in `~/projects/animus/packages/forge/rubrics/`. Weights that matter: `format_compliance` (output structure), `precision` (measurable constraints), `actionability` (an engineer can implement from this alone).
