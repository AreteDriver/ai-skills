---
name: technical-debt-auditor
description: Systematic technical debt assessment for any repository. Scans for security issues, correctness gaps, infrastructure debt, maintainability problems, documentation quality, and dependency freshness. Produces scored DEBT.md reports. Supports sandboxed execution via Docker, single-repo and cross-repo portfolio analysis, and Gorgon workflow integration. Use when auditing repos, preparing projects for public release, portfolio polish, or tracking debt over time.
---

# Technical Debt Auditor

Systematic, repeatable technical debt assessment that produces consistent scoring across projects and over time. Designed to run standalone via Claude Code or as a Gorgon orchestrated workflow.

## When to Activate

- "Audit this repo for tech debt"
- "What's the health of this project?"
- "Prioritize what to fix before making this public"
- "Compare debt across my repos"
- Pre-job-application portfolio polish
- Any request to assess code quality, project health, or release readiness

## Operating Modes

| Mode | Trigger | Output |
|------|---------|--------|
| **Single Repo** | `audit <path>` | `DEBT.md` in repo root |
| **Portfolio** | `audit --portfolio <path-to-repos>` | `DEBT.md` per repo + `PORTFOLIO-HEALTH.md` summary |
| **Diff** | `audit --diff <path>` | Compare against previous `DEBT.md`, show improvement/regression |
| **Career** | `audit --mode portfolio` | Applies career-weight modifier (2x Documentation + Infrastructure for pinned/resume repos) |

## Architecture: 5-Agent Gorgon Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATOR (this skill)                   │
│  Dispatches repos, manages checkpoints, aggregates results   │
├──────────┬──────────┬───────────┬───────────┬───────────────┤
│ SCANNER  │ EXECUTOR │ ANALYZER  │ REPORTER  │  AGGREGATOR   │
│ Agent    │ Agent    │ Agent     │ Agent     │  Agent        │
│          │          │           │           │               │
│ Read-only│ Sandboxed│ Scores &  │ Writes    │ Cross-repo    │
│ file     │ Docker   │ categorize│ DEBT.md   │ matrix &      │
│ analysis │ run/test │ findings  │ per repo  │ PORTFOLIO-    │
│          │          │           │           │ HEALTH.md     │
└──────────┴──────────┴───────────┴───────────┴───────────────┘
```

### Agent Responsibilities

**Scanner Agent** — Read-only static analysis
- File tree discovery, language/framework detection
- `grep` for secrets, TODOs/FIXMEs, dead code indicators
- Dependency manifest parsing (requirements.txt, package.json, Cargo.toml)
- Dependency vulnerability scan (`pip-audit`, `npm audit`, `cargo audit`)
- License detection
- README presence and completeness check
- CI/CD configuration detection (.github/workflows, Makefile, Dockerfile)
- Git history analysis (last commit, contributor count, commit frequency)
- Output: `scan-results.json`

**Executor Agent** — Sandboxed runtime verification
- Builds Docker container from repo (auto-detects Dockerfile, or generates minimal one)
- Attempts: `pip install`, `npm install`, `cargo build`
- Runs entry point: `python -m <pkg> --help`, `npm start`, `cargo run`
- Runs test suite: `pytest`, `npm test`, `cargo test`
- Captures: exit codes, stderr, test results, install duration
- Output: `execution-results.json`
- Budget: max 5 min per repo, 500MB container limit
- **Checkpoint**: If execution fails, report failure and continue — never blocks pipeline

**Analyzer Agent** — Scoring and categorization
- Consumes `scan-results.json` + `execution-results.json`
- Scores each of 6 categories (0-10) per rubric in `references/scoring-rubric.md`
- Categorizes findings by severity: Critical / High / Medium / Low
- Applies career-weight modifier if `--mode portfolio`
- Detects patterns: "this repo has 0 tests but 200 TODOs" → structural neglect
- Output: `analysis.json`

**Reporter Agent** — Human-readable output
- Consumes `analysis.json`
- Generates `DEBT.md` from template
- Orders fix recommendations by ROI (impact / effort)
- Includes estimated fix times
- If previous `DEBT.md` exists, generates diff section showing improvement/regression
- Output: `DEBT.md` in repo root

**Aggregator Agent** — Portfolio-wide synthesis (portfolio mode only)
- Consumes all per-repo `analysis.json` files
- Builds comparison matrix
- Ranks repos by health score
- Identifies cross-repo patterns ("3 of your 5 Python repos have no CI")
- Highlights career-critical repos that need immediate attention
- Output: `PORTFOLIO-HEALTH.md`

## Scan Categories & Weights

| # | Category | What It Checks | Weight | Career Modifier |
|---|----------|---------------|--------|-----------------|
| 1 | **Security** | Hardcoded secrets, vulnerable deps, .env in git, exposed API keys | Critical (blocker — score capped at 3 if any critical finding) | 1x |
| 2 | **Correctness** | Tests exist? Pass? Coverage? Entry point runs? | High (2x) | 1x |
| 3 | **Infrastructure** | CI/CD, Dockerfile, install steps work, reproducible build | High (2x) | **2x career** |
| 4 | **Maintainability** | TODO/FIXME count, dead code, module structure, naming | Medium (1x) | 1x |
| 5 | **Documentation** | README quality, docstrings, API docs, CHANGELOG, LICENSE | Medium (1x) | **2x career** |
| 6 | **Freshness** | Last commit age, dep staleness, Python/Node version | Low (0.5x) | 0.5x |

### Score Calculation

```
raw_score = weighted_average(category_scores, weights)

# Security blocker: if any CRITICAL security finding exists
if security_has_critical:
    raw_score = min(raw_score, 3.0)

# Career mode: apply career modifiers to pinned/resume repos
if career_mode and repo.is_career_relevant:
    apply career_weights instead of default weights

final_score = round(raw_score, 1)
grade = map_to_grade(final_score)  # A/B/C/D/F
```

### Grade Scale

| Score | Grade | Meaning |
|-------|-------|---------|
| 9-10 | A | Production-ready, portfolio showcase |
| 7-8.9 | B | Solid, minor polish needed |
| 5-6.9 | C | Functional but significant gaps |
| 3-4.9 | D | Major issues, not demo-ready |
| 0-2.9 | F | Broken or dangerous |

## Gorgon Workflow Integration

The audit runs as a Gorgon pipeline defined in `workflow.yaml`:

```yaml
workflow:
  name: technical_debt_audit
  version: "1.0"
  description: "Systematic technical debt assessment"

  config:
    checkpoint_enabled: true
    max_budget_per_repo: 2000  # tokens
    docker_timeout: 300        # seconds
    docker_memory_limit: "512m"

  agents:
    - role: scanner
      task: "Static analysis of repository"
      budget: { max_tokens: 1000 }
      timeout: 60
      output: scan-results.json

    - role: executor
      task: "Sandboxed runtime verification"
      depends_on: [scanner]
      budget: { max_tokens: 500 }
      timeout: 300
      output: execution-results.json
      on_failure: continue  # Don't block pipeline if repo won't build

    - role: analyzer
      task: "Score and categorize findings"
      depends_on: [scanner, executor]
      budget: { max_tokens: 1000 }
      output: analysis.json

    - role: reporter
      task: "Generate DEBT.md report"
      depends_on: [analyzer]
      budget: { max_tokens: 500 }
      output: DEBT.md

    - role: aggregator
      task: "Cross-repo portfolio synthesis"
      depends_on: [reporter]  # Waits for ALL repos to complete
      budget: { max_tokens: 1000 }
      output: PORTFOLIO-HEALTH.md
      condition: "portfolio_mode == true"
```

### Checkpoint/Resume

Gorgon's checkpoint system means:
- Auditing 20 repos and Docker fails on repo #13 → resume from #13
- Scanner completes but executor hits timeout → analyzer still gets scanner data
- Network drops during `pip-audit` → re-run only the executor for that repo

### Budget Controls

- Scanner: lightweight, mostly grep/file analysis — low token budget
- Executor: Docker operations, no LLM tokens needed (shell commands only)
- Analyzer: needs reasoning about findings — moderate budget
- Reporter: template-driven output — low budget
- Aggregator: cross-repo pattern detection — moderate budget

## Execution: Standalone (No Gorgon)

For quick single-repo audits without Gorgon:

```bash
# From Claude Code
cd /path/to/repo
# Run scanner
./scripts/scan.sh > scan-results.json
# Run executor (Docker)
./scripts/execute.sh > execution-results.json
# Claude analyzes and generates DEBT.md
```

Or paste this into Claude Code:

```
Read the technical-debt-auditor SKILL.md and audit this repository.
Use the scoring rubric in references/scoring-rubric.md.
Generate DEBT.md in the repo root.
```

## File Structure

```
technical-debt-auditor/
├── SKILL.md                          # This file (coordinator)
├── workflow.yaml                     # Gorgon pipeline definition
├── agents/
│   ├── scanner.md                    # Scanner agent instructions
│   ├── executor.md                   # Executor agent instructions
│   ├── analyzer.md                   # Analyzer agent instructions
│   ├── reporter.md                   # Reporter agent instructions
│   └── aggregator.md                # Aggregator agent instructions
├── references/
│   ├── scoring-rubric.md            # Detailed 0-10 criteria per category
│   ├── scan-commands.md             # Language-specific scan commands
│   ├── readme-rubric.md             # README quality checklist
│   └── docker-templates.md          # Auto-generated Dockerfiles per language
├── templates/
│   ├── DEBT.md                      # Per-repo output template
│   ├── PORTFOLIO-HEALTH.md          # Cross-repo summary template
│   └── Dockerfile.audit             # Sandboxed execution container
└── scripts/
    ├── scan.sh                      # Standalone scanner (no Gorgon)
    └── execute.sh                   # Standalone executor (no Gorgon)
```

## Coordinator Responsibilities

1. **Detect mode** from arguments or conversation context
2. **Enumerate repos** (single path or directory of repos for portfolio mode)
3. **Dispatch agents** in pipeline order per repo
4. **Handle failures gracefully** — executor failure doesn't block analysis
5. **Checkpoint after each agent** — resume from last successful step
6. **Apply career-weight** if portfolio/career mode
7. **Aggregate** if portfolio mode — wait for all repos, then run aggregator
8. **Diff** if previous DEBT.md exists — show what improved/regressed
9. **Present results** — summary in conversation + files written to repo

## Important Constraints

- **Never auto-fix** — audit and document only. Fixing is a separate decision.
- **Never commit to git** — DEBT.md is written locally. User decides whether to commit.
- **Secrets found = immediate flag** — don't just score low, explicitly warn the user.
- **Docker sandbox is mandatory for execution** — never run untrusted code on host.
- **Reproducible** — same repo scanned twice should produce same scores (within tolerance of dep vulnerability databases updating).
