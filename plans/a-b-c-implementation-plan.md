# Option A → B → C Implementation Plan

## Objective
Move `ai-skills` from ~8.2/10 to **9.5+/10** maturity by systematically expanding eval coverage, building discovery/distribution tooling, and automating skill lifecycle governance.

---

## Phase A — Eval Coverage Expansion (Target: 50+ skills with evals)

**Premise:** We have 7 eval cases covering 7 skills. We need broad structural coverage (all 144) and deep behavioral coverage (stable/high-use skills).

### A1. Fix CI Artifact Path Mismatch (15 min)
- **File:** `.github/workflows/validate-skills.yml`
- **Change:** Upload `evals/reports/quality-card-golden.md` instead of stale `quality-card.md`
- **Commit:** `ci: fix eval report artifact path`

### A2. Build Eval Scaffolding Tool (2–3 hrs)
- **New file:** `scripts/scaffold-eval.py`
- **Behavior:**
  - Accepts `--skill <path>` or `--all`
  - Reads SKILL.md frontmatter + body
  - Generates `evals/<type>/<category>/<name>/case-001.yaml` from a template
  - Derives `must_contain` from the skill's "Core Behaviors" section headings
  - Derives `must_not_contain` from the skill's "When NOT to Use" alternatives
  - Derives `required_headers` from the skill's markdown structure
  - Generates a synthetic golden example by extracting the first code block / example paragraph from SKILL.md
- **Commit:** `feat: add eval case scaffolding from SKILL.md`

### A3. Batch-Create Smoke Eval Cases (1–2 hrs)
- Run `scripts/scaffold-eval.py --all`
- Review a sample of 10 for sanity, then commit the bulk
- Every skill gets at least a **structural smoke eval** (validates SKILL.md structure, frontmatter, and basic content expectations)
- High-priority skills (all agents + all workflows + top 20 personas by bundle usage) get a **critical behavioral eval** with richer `expected` criteria
- **Commit:** `test: add smoke eval cases for all 144 skills`

### A4. Improve Scoring Robustness (1–2 hrs)
- **File:** `scripts/run-evals.py`
- **Changes:**
  - Add `regex_contains` alongside `must_contain` for pattern matching
  - Add `check_format()` that validates JSON/YAML output with actual parsers
  - Add `--judge-model` flag that optionally uses an LLM-as-judge for `reasoning_quality` when API key is present
  - Add per-skill-type default weights (agents prioritize safety, personas prioritize structure, workflows prioritize reasoning)
- **Commit:** `feat: improve eval scoring with format validation and optional LLM judge`

### A5. Add Incremental Eval Mode (30 min)
- **File:** `scripts/run-evals.py`
- **Changes:**
  - Add `--changed` flag: uses `git diff --name-only origin/main` to find modified skills, only runs their evals
  - Add `--since <commit>` flag for custom baselines
- **Commit:** `feat: add incremental eval mode for PR efficiency`

### A6. Add Eval Coverage Gate to CI (30 min)
- **File:** `.github/workflows/validate-skills.yml`
- **Changes:**
  - Add a step after `evals` job that computes coverage % (eval_cases / total_skills)
  - Fail if coverage < 90% (eventually; start with 50% as we ramp)
  - Store coverage badge artifact
- **Commit:** `ci: add eval coverage percentage gate`

**Phase A Exit Criteria:**
- ≥50 skills have at least one eval case
- All 144 skills have at least a structural smoke eval
- CI artifact path is correct
- `--changed` mode works for PRs
- Coverage gate passes at ≥50%

---

## Phase B — Distribution & Discovery (Target: searchable CLI + enriched registry)

**Premise:** Users find skills by browsing README or running `--list`. We need keyword search, faceted filtering, and a skill info command.

### B1. Enrich Manifest Schema with Tags (1–2 hrs)
- **New file:** `scripts/extract-tags.py`
- **Behavior:**
  - Scans each SKILL.md for technology mentions (heuristic: code blocks with language hints, capitalized tech names, explicit "Languages:" or "Technologies:" lines)
  - Derives a `tags` array per skill: e.g., `python`, `rust`, `security`, `testing`, `frontend`, `backend`, `api`, `devops`
  - Also extracts `triggers` ("Triggers on:", "Use when:", "Activate on:") as a second tag list
  - Stores results in `manifests/<id>.json` as `"tags"` and `"triggers"`
- **File:** `scripts/generate-manifests.py`
- **Change:** Call `extract-tags.py` during manifest generation
- **Commit:** `feat: auto-extract tags and triggers from SKILL.md into manifests`

### B2. Add Tags to Registry and Index (30 min)
- **File:** `scripts/generate-registry.py`
- **Change:** Include `tags` and `triggers` arrays in registry.yaml entries
- **File:** `scripts/generate-docs.py`
- **Change:** Add a tag-cloud / faceted index to generated docs
- **Commit:** `feat: expose tags and triggers in registry and docs`

### B3. Build `scripts/skill-search.py` CLI (2–3 hrs)
- **New file:** `scripts/skill-search.py`
- **Interface:**
  - `skill-search.py "security"` — full-text search across names, descriptions, tags, triggers
  - `skill-search.py --tag python` — filter by tag
  - `skill-search.py --type agent --risk high` — faceted filter
  - `skill-search.py --fuzzy "reviwer"` — typo-tolerant fuzzy match (simple Levenshtein on names)
  - Output: ranked table with name, type, category, description, match score, tags
- **Behavior:** Reads `manifests/_index.json` — no external dependencies beyond Python stdlib
- **Commit:** `feat: add skill-search CLI with faceted filtering`

### B4. Wire Search into Installer (30 min)
- **File:** `tools/install.sh`
- **Changes:**
  - Add `--search <query>` subcommand: delegates to `scripts/skill-search.py`, prints results, optionally prompts to install
  - Add `--info <skill>` subcommand: reads manifest JSON and prints rich metadata (description, tags, version, schema status, lifecycle, eval status)
- **Commit:** `feat: add --search and --info to installer`

### B5. Generate Searchable Index Page (30 min)
- **File:** `scripts/generate-docs.py`
- **Change:** Generate `docs/generated/search-index.md` — an alphabetically sorted, tagged, cross-referenced index of all skills with jump links
- **Commit:** `docs: add generated search index`

**Phase B Exit Criteria:**
- `./tools/install.sh --search "python testing"` returns relevant skills
- `./tools/install.sh --info code-reviewer` prints rich metadata
- `registry.yaml` includes tags for all skills
- Generated docs include a faceted search index

---

## Phase C — Skill Lifecycle Automation (Target: eval-gated promotion)

**Premise:** No skill has a `lifecycle` field. We need experimental → stable → deprecated states with automated gates.

### C1. Add Lifecycle Field to Templates and Validator (1 hr)
- **Files:** `templates/skill-template-v2.md`, `templates/agent-template.md`, `templates/workflow-template.md`
- **Change:** Add `lifecycle: experimental` to frontmatter (default for new skills)
- **File:** `scripts/validate-skill-contract.py`
- **Change:** Add `lifecycle` enum validation (`experimental`, `beta`, `stable`, `deprecated`)
- **Commit:** `feat: add lifecycle field to templates and contract validator`

### C2. Bulk-Classify Existing Skills (1–2 hrs)
- **Script:** `scripts/classify-lifecycle.py` (one-shot, not retained)
- **Logic:**
  - `stable`: Has v2 frontmatter + has_schema where applicable + has `examples/` + eval case passes + no validation errors
  - `experimental`: Everything else (v1 frontmatter, missing examples, no evals, or validation warnings)
  - `deprecated`: Already noted in prose (e.g., `/security-audit` replaced by `security-auditor`) — manual review required
- Apply classification to all 144 SKILL.md files via `scripts/classify-lifecycle.py`
- **Commit:** `feat: classify all 144 skills with initial lifecycle state`

### C3. Add Promotion/Demotion Pipeline (2–3 hrs)
- **New file:** `scripts/lifecycle-manager.py`
- **Interface:**
  - `lifecycle-manager.py promote <skill>` — checks gates, upgrades lifecycle if passes
  - `lifecycle-manager.py demote <skill> --reason "..."` — downgrades lifecycle
  - `lifecycle-manager.py audit` — scans all skills, reports which are eligible for promotion/demotion
- **Promotion Gates (to stable):**
  1. v2 frontmatter complete
  2. Has `examples/` directory with ≥1 example
  3. Has ≥1 eval case that passes
  4. No validation errors (warnings OK)
  5. No deprecated dependencies
- **Demotion Triggers (to experimental):**
  1. Eval case fails
  2. Validation errors introduced
  3. Missing examples (if previously had them)
- **Commit:** `feat: add lifecycle promotion/demotion pipeline`

### C4. Add Deprecation Metadata to Registry (1 hr)
- **File:** `scripts/generate-registry.py`
- **Change:** If a skill's `lifecycle` is `deprecated`, include `replaces`, `deprecated_by`, `sunset_date` fields sourced from frontmatter
- **File:** `scripts/generate-manifests.py`
- **Change:** Extract deprecation metadata if present in frontmatter
- **Commit:** `feat: add deprecation metadata to registry`

### C5. Add Lifecycle Gate to CI (30 min)
- **File:** `.github/workflows/validate-skills.yml`
- **Changes:**
  - Add `lifecycle` job that runs `scripts/lifecycle-manager.py audit`
  - Fail if any `stable` skill violates promotion gates
  - Report promotion candidates (informational, not blocking)
- **Commit:** `ci: add lifecycle audit gate`

### C6. Add Lifecycle Dashboard to Docs (30 min)
- **File:** `scripts/generate-docs.py`
- **Change:** Generate `docs/generated/lifecycle-dashboard.md` — table of all skills with lifecycle badge, eval status, examples count, and promotion eligibility
- **Commit:** `docs: add generated lifecycle dashboard`

**Phase C Exit Criteria:**
- Every skill has a `lifecycle` value
- `stable` skills are gated (examples + evals + clean validation)
- `lifecycle-manager.py audit` runs in CI
- Promotion/demotion is scriptable
- Generated docs include a lifecycle dashboard

---

## Commit Order & Dependencies

```
# Phase A
A1  ci: fix eval report artifact path
A2  feat: add eval case scaffolding from SKILL.md
A3  test: add smoke eval cases for all 144 skills
A4  feat: improve eval scoring with format validation and optional LLM judge
A5  feat: add incremental eval mode for PR efficiency
A6  ci: add eval coverage percentage gate

# Phase B (depends on A3 for eval-enriched manifests)
B1  feat: auto-extract tags and triggers from SKILL.md into manifests
B2  feat: expose tags and triggers in registry and docs
B3  feat: add skill-search CLI with faceted filtering
B4  feat: add --search and --info to installer
B5  docs: add generated search index

# Phase C (depends on A6 for eval gates, B2 for tag-enriched manifests)
C1  feat: add lifecycle field to templates and contract validator
C2  feat: classify all 144 skills with initial lifecycle state
C3  feat: add lifecycle promotion/demotion pipeline
C4  feat: add deprecation metadata to registry
C5  ci: add lifecycle audit gate
C6  docs: add generated lifecycle dashboard
```

---

## Estimates

| Phase | Estimated Time | Commits |
|-------|---------------|---------|
| A | 6–8 hrs | 6 |
| B | 5–7 hrs | 5 |
| C | 5–7 hrs | 6 |
| **Total** | **16–22 hrs** | **17** |

---

## Risk Mitigation

- **Scoring robustness (A4):** LLM-as-judge is optional; golden mode remains default. No API key dependency for CI.
- **Bulk classification (C2):** One-shot script; human reviews a sample of 10 before applying to all 144.
- **Tag extraction (B1):** Heuristic-based; false positives are harmless (extra tags just improve recall).
- **Eval coverage at scale:** Smoke evals are cheap (no API calls, structural only). Critical evals remain focused on high-value skills.

---

## Definition of Done (Overall)

- `./tools/install.sh --search "<query>"` works and returns ranked results
- `./tools/install.sh --info <skill>` prints lifecycle, eval status, tags, and examples count
- ≥90% of skills have at least one eval case (all 144 have smoke evals)
- CI gates on eval coverage % and stable-skill lifecycle requirements
- `registry.yaml` includes tags, triggers, and lifecycle for every skill
- Generated docs include a faceted search index and a lifecycle dashboard
- Project maturity score: **9.5/10**
