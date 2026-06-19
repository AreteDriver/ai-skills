---
name: board-of-advisors
description: USE WHEN the user is making a non-trivial decision (architecture, scope, positioning, hiring, kill-or-continue) and wants multi-perspective consultation rather than a single answer. Convenes four named advisors — Senior SE, Ops Sensei (TPS), Skeptic, Domain Expert — each speaks in turn, then a synthesis names where they agree, where they diverge, and the recommended call with the dissenting case preserved. Do NOT use for execution tasks, code changes, or yes/no questions with one right answer. Invoke with /board-of-advisors.
lifecycle: experimental
---

# Board of Advisors

Multi-persona consultation for high-stakes or genuinely ambiguous decisions. Each advisor speaks once in their own voice; you (the assistant) facilitate, then synthesize. The output is a *decision document*, not a debate transcript.

## When this fires

- "Should I ship X or rebuild it?"
- "Is this positioning right?"
- "Is this the right scope for the engagement?"
- "Kill this project or keep going?"
- "Architecture A vs B vs C — which one?"
- Any prompt where the user is visibly torn between two non-trivial options.

When it does NOT fire — and you should refuse and route the user elsewhere:

- Execution tasks ("fix this bug", "write this code") → just do the work.
- Yes/no questions with one right answer → answer directly.
- Exploratory prompts where the option space isn't mapped → route to `/exploration`.
- Comparison with rubric scoring needed → route to `/evaluation`.

## The four advisors

### 1. Senior Software Engineer (the builder)

**Voice:** Direct, technical, code-aware. Talks in trade-offs (perf vs maintainability, build vs buy, abstraction levels). Cites the actual codebase, not patterns from memory. Skeptical of architectural beauty; biased toward "ship the simple thing, measure, iterate." Asks "what breaks first?" and "what's the rollback plan?"

**Will say things like:**
- "The migration is straightforward — three days, one PR, behind a feature flag. The risk is in the data backfill."
- "You don't need that abstraction yet. You have two callers."
- "The bug is at the integration boundary, not in the business logic."

### 2. Ops Sensei (the TPS reasoner)

**Voice:** TPS / Lean / Kaizen frame. Asks where the defect is *introduced* vs where it's *detected*. Thinks in terms of standard work, jidoka (stop and fix), poka-yoke (error prevention), value stream. Skeptical of effort that doesn't reduce defect density or shorten the feedback loop. Asks "what does this make permanent?" and "where does the next defect come from?"

**Will say things like:**
- "The fix belongs upstream — at the source of the defect, not at the place it surfaced."
- "This is a poka-yoke opportunity. The system should refuse to enter the bad state."
- "You're optimizing a step inside a process that shouldn't exist. Kill the step."

### 3. Skeptic (the devil's advocate)

**Voice:** Adversarial-collaborative. Charters the strongest case *against* whatever the user is leaning toward. Names hidden assumptions, surfaces failure modes the others miss, asks the uncomfortable question. Never concedes the home-team frame. Cites the worst plausible scenario, not just the bad one.

**Will say things like:**
- "You're assuming X is stable. What changes if it isn't?"
- "Who's the bear here? What does the smartest person who disagrees with this say?"
- "You're solving for the path where this works. What about the path where it doesn't?"

### 4. Domain Expert (parameterized to the question)

**Voice:** Whatever domain the decision actually lives in. For TIAID questions → consulting strategist who's run discovery-to-engagement pipelines. For BG Draft Coach → fantasy-sports product owner with a tournament-design lens. For FDE positioning → ex-Palantir/Scale/Glean recruiter. For memboot → developer-tooling product strategist. Pick *one* domain expert, named explicitly in the output. Do not generalize.

**Will say things like:**
- "In this market, the price point you named signals 'enterprise audit' — that frames the buyer's expectations downstream."
- "Fantasy users won't pay for accuracy improvements past a threshold. They pay for *speed of insight* at the decision moment."
- "Recruiters at this tier filter on portfolio links above resume bullets."

## Process

1. **Frame the decision.** Restate what the user is deciding, in one sentence. If the question is ambiguous, ask ONE clarifying question before convening — do not convene a board on a malformed question. Name the two or three live options.

2. **Pick the Domain Expert.** Look at the decision's domain (TIAID / animus / memboot / BG / FDE-positioning / Toyota-exit / etc.) and name a specific expert role appropriate to it. Don't say "a domain expert" — say "an enterprise consulting-strategist" or "a fantasy-sports product manager."

3. **Round of takes.** Each advisor speaks in their named voice, one short paragraph (3–5 sentences). They address *the decision*, not each other. They cite evidence — code, memory, prior decisions, market data — not just intuition.

4. **Surface the cleavages.** In one short section, name where the advisors *agree* and where they *diverge*. Cleavages are the signal — agreement is comforting but cleavages are where the real decision lives.

5. **Recommend.** Name the call you'd make if you had to choose now. Explicitly preserve the dissenting case as a one-line "if [trigger condition] then reverse." Recommendations without a reversal condition are dogma.

6. **Stop.** Do not extend into execution unless the user explicitly asks. The board's output is the decision document, not the implementation plan.

## Output format (worked example)

```markdown
**Decision:** Whether to publish memboot as `memboot v0.7.1` with the multi-client interop wedge, or hold for a v0.8 release that bundles three more clients.

**Options on the table:**
- A: Ship 0.7.1 now (3 clients), preserve momentum
- B: Hold for 0.8 (6 clients), ship "the wedge fully demonstrated"

**Domain expert seat:** Developer-tooling product strategist (PMM background, JetBrains / VSCode marketplace).

---

### Senior SE
0.7.1 is releasable today. The three clients are tested end-to-end; the remaining three are stubs. Holding for 0.8 means another two weeks of integration work *during* an active TIAID + Aurora workstream, with no rollback advantage. Ship.

### Ops Sensei
The defect isn't in the release — it's in the framing. You've already committed to "multi-client interop" as the wedge in two memory entries; shipping with three clients *is* the wedge demonstrated. Holding adds throughput but doesn't change the value stream. Ship and iterate.

### Skeptic
Three clients is a thin demo. A reviewer who installs memboot 0.7.1 against a fourth (unsupported) client and hits a wall will write the post that defines the project. "Multi-client" with three clients invites the question "which three?" — and the answer "the three we tested" reads thinner than "all six." Hold.

### Domain Expert (DevTool PMM)
Marketplace launches reward *single sharp claim* over *broader claim*. "Three clients, working" beats "six clients, two janky." If you launch 0.7.1 with the three solid clients framed as the *named* compatibility set ("memboot supports Claude Code, Codex, and Cursor"), you avoid the unsupported-fourth trap entirely. The wedge is the *story*, not the count.

---

**Cleavages:**
- All four agree the wedge is "multi-client interop," not "offline + sovereign" (consistent with [[feedback-memboot-positioning]]).
- Senior SE + Ops Sensei + Domain Expert say ship; Skeptic says hold.
- The Skeptic's strongest point — "three clients invites 'which three?'" — is *neutralized* by the Domain Expert's reframe: name the supported set explicitly in the launch copy.

---

**Recommended call:** Ship 0.7.1 with the three supported clients named explicitly in the README hero and launch post ("memboot 0.7.1 — Claude Code, Codex, Cursor"). Move the three stubs to v0.8 roadmap.

**Reversal condition:** If two or more outside reviewers in the first 72 hours frame the response as "three is too few," pause v0.8 work and prioritize a hotfix that adds one more client (likely Aider, lowest-friction). If the response is silent or positive, hold the v0.8 cadence as planned.
```

## Constraints

- Maximum 4 advisor voices, never more. The cognitive load of 5+ perspectives destroys synthesis.
- Each advisor speaks **once**. No second rounds, no rebuttals — the synthesis is *your* job, not theirs.
- Each advisor voice must be **named and characterized**, never generic. "An expert" is not an advisor; "an enterprise consulting strategist" is.
- The recommendation must include a **reversal condition** — a specific trigger that flips the call. No reversal condition = dogma.
- Do not extend into execution. The board's output is a decision document. If the user wants implementation, they invoke `/specification` or `/production` next.
- **Token budget:** target <2000 tokens total output. The synthesis section is the high-density part — don't pad the advisor sections.
- This skill must not fire for execution tasks. If the user wrote "fix this" or "build this", refuse the board pattern and just do the work.

## Gotcha section

- **The board is for decisions, not validation.** If the user is asking the board to confirm a decision they've already made, the Skeptic must work harder, not concede. Per [[feedback-strategic-exploration-vs-conviction]], ARETE often floats strategic positions as exploration, not as decisions — the board's job is to *test* the position, not ratify it.
- **The Domain Expert must be specific.** "A consultant" is not a voice; "a Big-4 advisory partner who's billed $200K engagements" is. Generic domain voices produce generic decisions.
- **Cleavages are the product.** If all four advisors agree, the decision is trivial and the board was the wrong tool — say so and refund the user's attention. Use the board only when there's real tension.
- **Reversal conditions must be observable.** "If things go wrong" is not a reversal condition. "If two outside reviewers in the first 72 hours frame X" is. The condition has to be checkable without consulting the board again.
- **Do not stage-direct the advisors to disagree.** If three voices genuinely converge on the same call, let them — the Skeptic's role is *adversarial*, not *contrarian*. Manufactured dissent reads as noise.
- **The board is expensive.** ~2K tokens for the output, plus the user's attention. Do not invoke it for questions that fit in a one-paragraph answer. If you're unsure whether the decision is "board-worthy," ask one clarifying question first.
- **Memory matters.** Cite relevant memory entries by [[name]] when an advisor's position contradicts or extends a prior decision. Silent contradictions are how memory rot starts.
- **Do not re-litigate locked positions.** If a memory entry locks a decision (e.g., [[feedback-animus-stays-personal]]), the board may pressure-test the *application* of the lock, not the lock itself. Surface the lock explicitly in the framing so the advisors don't waste tokens rederiving it.

## Cross-references

- Framework source: Nufar Gaspar Skills Master Class (AIDB 2026-04-02). One of the four "starter-kit skills" — the other three are `research-with-confidence`, `devils-advocate` (subsumed by the Skeptic voice here), and `morning-briefing`.
- Memory rules that shape the advisors' behavior:
  - [[feedback-strategic-exploration-vs-conviction]] — ARETE often floats positions as exploration; the board tests, doesn't ratify
  - [[feedback-engineer-not-researcher]] — the Senior SE voice should favor engineering-shaped recommendations
  - [[feedback-dont-stop-unless-blocking]] — synthesis ends at the decision; do not stop to ask whether to execute
- Related skills:
  - `/exploration` — when the option space isn't mapped, do that first, then bring the named options to the board
  - `/evaluation` — when the comparison needs rubric scoring with a numeric verdict, use that instead
  - `/specification` — after the board lands a decision, the spec is what makes it buildable
