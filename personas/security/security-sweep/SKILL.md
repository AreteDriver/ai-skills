---
name: security-sweep
version: "1.0.0"
description: Fleet-wide security audit — runs /security-auditor across multiple repos, aggregates findings to FLEET-SECURITY.md, surfaces NEW findings since last sweep. Use for periodic fleet hardening, post-Dependabot-sweep verification, or before security-sensitive releases.
metadata: {"openclaw": {"emoji": "🛡️", "os": ["darwin", "linux", "win32"]}}
user-invocable: true
type: persona
category: security
risk_level: low
---

# Security Sweep

Fleet-level companion to `/security-auditor`. Where `/security-auditor` audits one repo, `/security-sweep` audits many and produces an aggregate `FLEET-SECURITY.md` index showing the security posture across the portfolio.

## When to Use

Use this skill when:
- Auditing the entire Arete fleet for periodic hardening (monthly/quarterly cadence)
- Verifying no security regressions after a fleet-wide Dependabot sweep
- Preparing the portfolio for an external audit (TIAID assessment, job application security review, pen-test prep)
- Investigating whether a CVE disclosed in a shared dependency affects multiple repos

## When NOT to Use

Do NOT use this skill when:
- Auditing a single repo — use `/security-auditor` directly. This skill adds overhead (project iteration, aggregation) that's wasted on a single target.
- Doing an ad-hoc spot check — single-repo audit is faster.
- The fleet hasn't been sept in <7 days — running too often creates noise; new findings from rapid iteration aren't actionable.

## Core Behaviors

**Always:**
- Run `/security-auditor` per repo with `--diff` and `--patches` flags pre-set
- Use `--ollama` flag when available (Animus HybridBackend) to keep token cost at $0
- Aggregate by **severity-first, repo-second** in the fleet report — a CRITICAL finding in any repo outweighs a LOW in the "important" repo
- Cross-reference findings — if the same CVE or pattern hits multiple repos, surface the cluster
- Persist `FLEET-SECURITY.md` to `~/projects/notes/` so it's version-controlled alongside other portfolio docs
- Emit per-repo `SECURITY_FINDINGS.md` files (the auditor does this; sweep is the aggregator above them)

**Never:**
- Auto-apply patches across the fleet — even more dangerous than single-repo auto-apply because blast radius is multiplied
- Skip a repo because "it's probably fine" — that bypass is how silent vulns accumulate
- Inflate severity to make the sweep look more productive — the auditor's calibrated rubric is authoritative
- Persist findings to public repos (the notes repo is private; per-repo SECURITY_FINDINGS.md goes in the audited repo, which may or may not be public — flag if a repo is public and has CRITICAL findings)

## Default Target Set

When invoked without an explicit repo list, sweep this set (top 8 active per `~/.claude/projects/-home-arete-projects/memory/MEMORY.md`):

1. `~/projects/animus` (monorepo — 4 packages)
2. `~/projects/BenchGoblins`
3. `~/projects/EVE_Gatekeeper` (HIGH PRIORITY — Stripe billing live, real attack surface)
4. `~/projects/anchormd` (HIGH PRIORITY — License server on Fly.io, paid tier)
5. `~/projects/memboot` (validation target, mostly hardened)
6. `~/projects/Argus_Overview`
7. `~/projects/Dossier`
8. `~/projects/tiaid`

Override with explicit list: `/security-sweep ~/projects/foo ~/projects/bar`.

## Workflow

### Phase 1: Tool inventory (once)
Confirm `semgrep`, `bandit`, `gitleaks`, `pip-audit` are installed. Surface install hints if missing. The sweep can run with partial tooling but flag which checks were skipped.

```bash
for t in semgrep bandit gitleaks pip-audit; do
  command -v $t > /dev/null && echo "✓ $t" || echo "✗ $t MISSING"
done
```

### Phase 2: Per-repo audit (iterate)
For each target repo, invoke `/security-auditor --diff --patches` (add `--ollama` when integrated with Animus forge). Capture:
- Repo name + path
- Overall risk rating (Critical | High | Medium | Low)
- Finding counts by severity (after triage — false-positives excluded)
- Path to per-repo `SECURITY_FINDINGS.md`
- New findings since last sweep (from `--diff` output)
- Resolved findings since last sweep
- Regressions (severity increased)

### Phase 3: Cross-repo correlation
After all per-repo audits complete, scan for patterns that span multiple repos:
- **Shared dependency CVEs**: same package + version + CVE appearing in N repos
- **Shared SAST patterns**: same semgrep/bandit rule firing across N repos (e.g., partial-path subprocess, dynamic urllib)
- **Public repos with HIGH/CRITICAL findings**: flag for accelerated remediation (visible to attackers)

### Phase 4: Aggregate report
Write `FLEET-SECURITY.md` to `~/projects/notes/` with the schema below.

## Output Format: `~/projects/notes/FLEET-SECURITY.md`

```markdown
# Fleet Security Report

**Date:** YYYY-MM-DD
**Sweep ID:** UUID or timestamp
**Repos audited:** N
**Tools used:** semgrep + bandit + gitleaks + pip-audit [+ trivy where applicable]
**Triage model:** claude-opus-4-7 | qwen2.5:14b (Ollama)

## Executive Summary

[3-5 sentences: fleet posture, biggest risks, recommended priorities. Quote the worst single finding by name. State the fleet-wide trend vs. last sweep — improving / stable / regressing.]

## Fleet Posture by Severity

| Repo | Risk | Critical | High | Medium | Low | Info | Public? |
|---|---|---|---|---|---|---|---|
| EVE_Gatekeeper | Medium | 0 | 1 | 3 | 7 | 12 | Yes |
| anchormd | Low | 0 | 0 | 2 | 5 | 8 | No |
| memboot | Low | 0 | 0 | 0 | 2 | 0 | Yes |
| ... | ... | ... | ... | ... | ... | ... | ... |

(Sort by Critical desc, then High desc. "Public?" flags public repos for accelerated remediation.)

## Cross-Repo Patterns

### Shared CVEs
| CVE | Package | Fix Version | Affected Repos |
|---|---|---|---|
| CVE-XXXX-YYYY | foo | 1.2.3 | repo-a, repo-c, repo-f |

### Shared SAST Patterns
| Rule | Pattern | Affected Repos | Severity |
|---|---|---|---|
| B607 | partial-path subprocess | repo-a, repo-c | LOW |

## Delta Since Last Sweep

- **NEW (HIGH/CRITICAL):** [list with repo + fingerprint + brief description]
- **NEW (other):** [count by severity, link to per-repo reports]
- **RESOLVED:** [list — confirms fixes landed]
- **REGRESSED:** [list — severity increased, investigate why]

## Per-Repo Reports

- [`EVE_Gatekeeper/SECURITY_FINDINGS.md`](../EVE_Gatekeeper/SECURITY_FINDINGS.md)
- [`anchormd/SECURITY_FINDINGS.md`](../anchormd/SECURITY_FINDINGS.md)
- [...]

## Recommendations (Priority Order)

1. **Immediate** (this week): [CRITICAL findings — every one. Quote fingerprint + repo.]
2. **This Sprint** (this month): [HIGH findings, especially in public repos.]
3. **This Quarter**: [Cross-repo dependency upgrades, shared pattern hardening.]
4. **Ongoing**: [Tooling gaps — missing SAST tools, missing CI integration, etc.]

## Methodology Notes

[Any tool-inventory issues, repos skipped and why, model used for triage, runtime in seconds.]
```

## Severity-First Aggregation Rules

When ranking the fleet:
1. **Any CRITICAL in any repo** → fleet posture = Critical, regardless of other repos
2. **No CRITICAL but ≥1 HIGH in a public repo** → fleet posture = High
3. **No CRITICAL/HIGH in public repos, ≥1 HIGH in private repo** → fleet posture = Medium
4. **No HIGH+, only MEDIUM/LOW** → fleet posture = Low
5. **Zero findings after triage** → fleet posture = Clean

A single finding can dominate the report. That's intentional — alert fatigue from "the rest of the fleet is fine" is exactly how the one CRITICAL gets missed.

## Operating Modes (flags pass through to `/security-auditor`)

| Flag | Behavior |
|---|---|
| (default) | Full sweep across the 8-repo default set, --diff + --patches per repo |
| `<paths...>` | Override target set with explicit repo paths |
| `--ollama` | Route triage through Animus HybridBackend (planned — see Phase 4 of consolidation roadmap) |
| `--quick` | Skip per-repo OWASP grep phase, SAST-only per repo (faster, less coverage) |
| `--public-only` | Audit only repos that have a GitHub public counterpart (focuses attack-surface attention) |

## Constraints

- **No state in the audited repos** beyond `SECURITY_FINDINGS.md` (the per-repo file). All cross-repo state lives in `~/projects/notes/FLEET-SECURITY.md`.
- **Read-only on the audited repos** — never modify code, never auto-stage patches.
- **Don't run while CI is failing on `main`** — if a repo's main branch has red CI, audit it but flag the CI status in the report (audit may be operating on inconsistent state).
- **Respect `.gitignore`** — don't scan files the project itself excludes.

## Companion skills

- **`/security-auditor`**: per-repo audit. This skill calls it. Update both together when changing severity rubric or output schema.
- **`/fleet-status`**: portfolio-wide git/test/CI status (no security focus). Run this BEFORE `/security-sweep` if you want a holistic fleet snapshot.

## Animus-forge integration (planned)

When invoked via `animus-forge` workflow, the sweep runs nightly with `--ollama` pre-set, persists findings to ChromaDB for cross-session memory, and emits Discord notifications via the existing `fleet-monitor` bot when new HIGH/CRITICAL findings appear. See `~/projects/animus/packages/forge/workflows/security-sweep.yaml` (planned — Phase 4 of consolidation roadmap).
