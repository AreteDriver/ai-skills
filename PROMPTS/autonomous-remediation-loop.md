# Autonomous AI Skills Remediation Loop

**Purpose:** Execute Phase 0–3 of the ai-skills remediation roadmap autonomously, with self-checking gates and checkpoint reporting.

**Trigger:** Paste this entire prompt into `/loop` or run as a Claude Code session directive.

**Context required:**
- Review `AUDIT_REPORT.md` (created 2026-06-19) for current drift findings
- Review `docs/artifacts/ai-skills-documentation-pack/CLAUDE_CODE_EXECUTION_BRIEF.md` for execution rules
- Review `plans/10-out-of-10-roadmap.md` for phase definitions

---

## Global Constraints

1. **Do not add new stable skills.** Only reconcile existing inventory.
2. **Preserve source content.** No rewrites of SKILL.md files unless to fix broken links.
3. **Do not manually patch counts.** Generate counts from source or leave them for auto-generation.
4. **Do not retain hard-coded bundle tables.** Installer must parse `bundles.yaml`.
5. **Do not auto-install hooks.** Hooks remain opt-in.
6. **Do not delete orphan skills without classifying.** Orphans with valid SKILL.md stay; add to registry.
7. **Run gates before reporting completion.** Every phase has exit criteria.
8. **Use small, reviewable commits.** One concern per commit.
9. **Record decisions.** Any architectural choice gets an ADL entry.
10. **Stop on blockers.** If a gate fails twice, stop and report — do not loop infinitely.

---

## Phase 0 — Stop the Drift

**Objective:** One accurate inventory. No documented command is false.

### Step 0.1: Write failing tests
Create `tests/test_catalog_drift.py` that reproduces every finding from `AUDIT_REPORT.md`:

- [ ] `test_all_personas_in_registry()` — every `personas/<cat>/<name>/SKILL.md` has a registry entry
- [ ] `test_all_agents_in_registry()` — every `agents/<cat>/<name>/SKILL.md` has a registry entry
- [ ] `test_all_workflows_in_registry()` — every `workflows/<name>/SKILL.md` has a registry entry
- [ ] `test_schema_flags_match_files()` — `has_schema` iff `schema.yaml` or `schema/` exists
- [ ] `test_all_bundles_installable()` — every bundle in `bundles.yaml` is accepted by `./tools/install.sh --bundle <name>` (dry-run)
- [ ] `test_content_ops_complete()` — `content-ops` resolves all 8 skills from `bundles.yaml`
- [ ] `test_no_missing_skill_md()` — every registry entry points to an existing `SKILL.md`
- [ ] `test_readme_bundle_commands_valid()` — every `./tools/install.sh --bundle <name>` in README matches a bundles.yaml entry

Run the tests. Confirm they fail. Commit: `test: reproduce catalog and installer drift`

### Step 0.2: Reconcile registry.yaml
- Add all 51 orphan personas to correct categories in `registry.yaml`
- Add 6 orphan workflows (`context-mapping`, `evaluation`, `exploration`, `goal`, `production`, `specification`)
- Rename `context-mapper` to `context-mapping` in registry (or verify it's truly orphaned)
- Set `has_schema: true` on 7 agents + 5 personas with actual schema files
- Recompute category totals manually once, then verify with script

Commit: `fix: reconcile registry with filesystem inventory`

### Step 0.3: Repair installer
Replace the hard-coded `BUNDLE_NAMES` and `bundle_skills()` in `tools/install.sh` with a parser that reads `bundles.yaml`.

Requirements:
- Parse `bundles.yaml` to get bundle names and skill lists
- Handle hooks reference (list, do not auto-install)
- Add `--dry-run` flag that prints what would be installed without copying
- Add `--preview` flag that shows bundle contents before install
- All 14 bundles from `bundles.yaml` must work
- `content-ops` must resolve all 8 skills

Test every bundle with `./tools/install.sh --bundle <name> --dry-run`.

Commit: `feat: resolve bundles from bundles.yaml in installer`

### Step 0.4: Correct README and CLAUDE.md
- Update skill counts to match reconciled registry
- Replace manual count tables with a note: "counts auto-generated from registry"
- Fix `arete-studio-ops` reference if still broken after installer fix
- Mark any remaining manual tables with `<!-- auto-generated -->`

Commit: `docs: replace stale catalog data with generated output`

### Step 0.5: Add strict validation to CI
Modify `.github/workflows/validate-skills.yml`:
- Add a `strict` job that runs `tests/test_catalog_drift.py`
- Fail on warnings for stable lane
- Validate exact registry entry equality (no duplicates, no orphans)
- Validate bundle definitions resolve

Commit: `ci: add strict catalog validation gate`

### Phase 0 Exit Gate
Run the full test suite. All Phase 0 tests must pass. Report:
- Persona count: registry vs filesystem
- Agent count: registry vs filesystem
- Workflow count: registry vs filesystem
- Bundle count: `bundles.yaml` vs installer
- Schema flag accuracy: % correct

If any gate fails after 2 attempts, stop and report the specific failure.

---

## Phase 1 — Single Source of Truth

**Objective:** Registry, docs, and bundle resolution are generated from skill sources.

**Precondition:** Phase 0 exit gate passed.

### Step 1.1: Build manifest compiler
Create `scripts/generate-manifests.py` that:
- Walks `personas/`, `agents/`, `workflows/`
- Generates a manifest per skill: `skill-id`, `type`, `category`, `path`, `has_schema`, `has_references`, `version`, `description` (from SKILL.md frontmatter if present)
- Writes manifests to `manifests/` directory
- Validates unique IDs across all types

Commit: `feat: add skill manifest compiler`

### Step 1.2: Build registry generator
Create `scripts/generate-registry.py` that:
- Reads all manifests from `manifests/`
- Generates `registry.yaml` in canonical format
- Preserves any manually added metadata (e.g., `has_references` flags that aren't auto-detectable)
- Adds a header comment: `# AUTO-GENERATED — do not edit manually`

Test: run generator, diff against current registry, verify no semantic drift.

Commit: `feat: generate registry from skill manifests`

### Step 1.3: Generate counts and catalog tables
Create `scripts/generate-docs.py` that:
- Reads registry
- Generates README catalog tables (personas, agents, workflows)
- Generates count summaries
- Outputs to `docs/generated/` (do not overwrite README directly yet)

Commit: `feat: generate catalog tables from registry`

### Step 1.4: Wire generation into CI
Add a CI job that:
- Runs `scripts/generate-registry.py`
- Runs `scripts/generate-docs.py`
- Fails if the generated output differs from committed output (i.e., someone forgot to regenerate)

Commit: `ci: gate on generated output freshness`

### Phase 1 Exit Gate
- Delete `manifests/` and regenerate from scratch — all tests still pass
- Modify one SKILL.md description — CI catches the registry drift
- Report: generation time, manifest count, registry coverage %

---

## Phase 2 — Installer Transactions

**Objective:** Every bundle installs exactly as defined and can be safely reversed.

**Precondition:** Phase 1 exit gate passed.

### Step 2.1: Add install ownership manifest
Modify `tools/install.sh`:
- Write a manifest to `~/.ai-skills/manifests/<bundle>-<timestamp>.json` on install
- Manifest contains: source paths, destination paths, checksums, hook refs
- Uninstall reads manifest and removes only listed files
- Update preserves user modifications (warn, do not overwrite without flag)

Commit: `feat: add transactional install manifest`

### Step 2.2: Add dry-run and rollback
- `--dry-run`: print planned actions, no filesystem changes
- `--rollback`: restore from backup manifest on failure
- `--uninstall <bundle>`: remove only files owned by this bundle

Commit: `feat: add dry-run, rollback, and safe uninstall`

### Step 2.3: Add integration tests
Create `tests/test_installer.py`:
- Install each bundle to a temp dir
- Verify expected files present
- Verify unexpected files absent
- Uninstall and verify cleanup
- Verify rollback works on injected failure

Commit: `test: add installer integration test matrix`

### Phase 2 Exit Gate
- All 14 bundles install and uninstall cleanly in temp environment
- No orphan files left after uninstall
- Rollback restores previous state on failure injection

---

## Phase 3 — Behavioral Quality (Optional if time permits)

**Objective:** Stable skills have evidence of effectiveness and safety.

**Precondition:** Phases 0–2 complete.

### Step 3.1: Define eval case schema
Create `specs/eval-case-v1.yaml`:
- `skill`: path to skill under test
- `input`: prompt or context
- `expected`: output criteria
- `negative`: what the skill must NOT do
- `safety`: any safety-critical checks

Commit: `feat: define eval case schema v1`

### Step 3.2: Migrate golden examples
Find existing "golden examples" or "example outputs" in SKILL.md files. Extract them into eval cases in `evals/`.

Commit: `test: migrate golden examples to executable eval cases`

### Step 3.3: Add eval runner
Create `scripts/run-evals.py` that:
- Loads eval cases
- Runs them against a local Claude Code instance or Ollama
- Scores pass/fail with reasoning
- Generates a quality card per skill

Commit: `feat: add behavioral eval runner`

### Phase 3 Exit Gate
- At least 5 stable skills have eval cases
- Eval runner produces a report with pass rate
- CI runs evals on changed skills in PRs

---

## Reporting Contract

Every 30 minutes or after each phase completion, emit a status block:

```
=== REMEDIATION STATUS ===
Phase: [0–3]
Step: [step name]
Commits: [N] on branch [branch-name]
Tests: [N] passing / [N] total
Blockers: [none | description]
Next: [step name]
Time elapsed: [N] min
==========================
```

If blocked for >10 minutes or a gate fails twice consecutively, escalate:
```
=== BLOCKER ESCALATION ===
Phase: [X]
Gate: [name]
Failure: [description]
Attempts: [N]
Suggested action: [human decision needed | retry with fix]
==========================
```

---

## Invocation

To run autonomously:

```bash
# Start a new Claude Code session with this prompt as the system directive
cd /home/arete/projects/ai-skills
claude "$(cat PROMPTS/autonomous-remediation-loop.md)"
```

Or in an existing session, paste the entire prompt and append:

> **Execute autonomously. Report every 30 minutes. Stop on blockers. Commit after every step.**

---

*Generated 2026-06-19. Target: move ai-skills from 6.7/10 to 7.5+/10.*
