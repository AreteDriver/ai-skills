# AI Skills Repository

## Project Overview

**Type**: Skill library — Claude Code personas, agent capabilities, workflow templates, hooks, and plugins
**Owner**: AreteDriver
**Repo**: github.com/AreteDriver/ai-skills (public, MIT)
**Purpose**: Production-ready, installable skills that transform Claude Code into specialized personas, define typed agent capabilities for orchestration frameworks, and coordinate multi-step workflows via the WHY/WHAT/HOW framework.

**Scale**: 144 skills across personas / agents / workflows (counts from `registry.yaml`). Installable per-skill, per-bundle, or wholesale into `~/.claude/`.

### Key concepts

- **Personas** change how Claude behaves (expertise, tone, output format)
- **Agents** define what an orchestration framework's agents can do (capabilities, inputs/outputs, risk levels, consensus requirements)
- **Workflows** orchestrate multi-agent execution via the WHY/WHAT/HOW framework
- **Hooks** plug into Claude Code lifecycle events (PreToolUse, PostToolUse, etc.)
- **Plugins** bundle skills + hooks into single distributable units
- **Bundles** are curated skill collections for common use cases (webapp-security, content-pipeline, etc.)

---

## Architecture

```
ai-skills/
├── personas/              # User behavior skills (how Claude acts)
│   ├── engineering/       # senior-software-engineer, software-architect, code-reviewer, ...
│   ├── data/              # data-analyst, data-engineer, data-visualizer, ...
│   ├── devops/            # backup, monitor, networking, systemd, ...
│   ├── claude-code/       # hooks-designer, plugin-builder, mcp-server-builder, ...
│   ├── security/          # security-auditor, accessibility-checker
│   ├── domain/            # hauling-*, eve-esi, gamedev, apple-dev-best-practices, ...
│   └── api/               # api-tester, database-ops, webhook-designer, oauth-integrator
├── agents/                # Agent capabilities for orchestration frameworks
│   ├── system/            # file-operations, process-runner
│   ├── browser/           # web-search, web-scrape
│   ├── email/             # email-compose
│   ├── integrations/      # github-operations, api-client
│   ├── orchestration/     # multi-agent-supervisor, agent-teams-orchestrator
│   └── analysis/          # tech-debt-auditor, release-engineer, entity-resolver, ...
├── workflows/             # Multi-step workflow templates
│   ├── context-mapping/
│   ├── feature-implementation/
│   └── release-engineering/
├── hooks/                 # Hook scripts for Claude Code lifecycle events
├── plugins/               # Plugin configurations bundling skills + hooks
├── bundles.yaml           # Curated skill bundles for common use cases
├── playbooks/             # Step-by-step workflow guides
├── prompts/               # Standalone prompt templates (legacy)
├── templates/             # Templates for creating new skills/prompts
├── decisions/             # Architecture Decision Records
├── tools/                 # Validation, formatting, and installer scripts
├── registry.yaml          # Central skill catalog
└── workflow-schema.yaml   # WHY/WHAT/HOW workflow schema definition
```

Each skill is a directory containing at minimum a `SKILL.md`. Agent skills additionally carry a `schema.yaml` (typed interface). Top personas carry an `output.schema.yaml` and an `examples/` subdirectory with golden examples.

---

## Common Commands

```bash
# Validate skill structure, frontmatter, registry, agent metadata, bundle refs
tools/validate-skills.sh
tools/validate-skills.sh --verbose
tools/validate-skills.sh --fix         # Auto-fix simple issues

# Check YAML syntax, markdown quality, shell syntax, line endings
tools/format-check.sh
tools/format-check.sh --fix            # Auto-fix trailing whitespace, CRLF

# Install (per-skill, per-bundle, or wholesale into ~/.claude/)
tools/install.sh --list
tools/install.sh --persona code-reviewer
tools/install.sh --bundle webapp-security
tools/install.sh --all

# Install pre-commit hook for automatic checking
ln -sf ../../hooks/pre-commit-format.sh .git/hooks/pre-commit
```

### When adding new skills

```bash
# Persona skill
cp templates/skill-template.md personas/<category>/<skill-name>/SKILL.md
# fill frontmatter (name + description), add output.schema.yaml, add examples/

# Agent skill
cp templates/agent-template.md agents/<category>/<skill-name>/SKILL.md
# create schema.yaml with inputs, outputs, capabilities, risk_level, consensus

# Workflow skill
cp templates/workflow-template.md workflows/<workflow-name>/SKILL.md
# create schema.yaml for the workflow interface

# Update registry
$EDITOR registry.yaml      # add entry under personas.<category>, agents.<category>, or workflows

# Validate before commit
tools/validate-skills.sh && ./tools/format-check.sh
```

---

## Coding Standards

### Skill files
- Every skill directory MUST contain a `SKILL.md`
- Every `SKILL.md` MUST have valid YAML frontmatter with `name` and `description`
- `description` MUST be under 300 characters for reliable auto-loading
- Reference materials go in `<skill>/references/` subdirectories
- Golden examples go in `<skill>/examples/` subdirectories
- Output schemas go in `<skill>/output.schema.yaml` (or `review_report.schema.yaml` for code-reviewer)

### Agent skills
- MUST include a `schema.yaml` with typed inputs, outputs, capabilities, `risk_level`, and `consensus` requirements
- `risk_level` is one of: `safe`, `caution`, `destructive`
- `consensus` is one of: `none`, `quorum`, `unanimous`

### Hooks
- Hook scripts MUST be executable (`chmod +x`)
- Hook scripts MUST handle stdin JSON (Claude Code lifecycle event payload)
- Hooks SHOULD return JSON to stdout when they need to communicate back

### Workflows
- Use the WHY/WHAT/HOW framework:
  - **WHY** — the problem being solved
  - **WHAT** — the discrete steps with inputs/outputs
  - **HOW** — implementation guidance per step

### Git
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Run both validators before pushing (CI runs them too — fail fast locally)

---

## Anti-Patterns (Do NOT Do)

- Do NOT write skill descriptions over 300 characters — breaks auto-loading
- Do NOT ship a skill without YAML frontmatter — validator rejects it
- Do NOT ship a persona skill without an `output.schema.yaml` and at least one golden example — auto-loaded skills without examples produce inconsistent outputs
- Do NOT ship an agent skill without `schema.yaml` — orchestration frameworks can't type-check the call
- Do NOT hardcode absolute paths in skills — use relative paths or `~/.claude/` references
- Do NOT commit hook scripts that aren't executable — they will silently fail in production
- Do NOT skip the validators before pushing — CI failures on the validate-skills workflow waste a round trip
- Do NOT use non-conventional commit prefixes — registry tooling parses commit messages
- Do NOT duplicate a skill across categories — pick one canonical location and reference from `bundles.yaml`
- Do NOT modify `registry.yaml` by hand without re-running `tools/validate-skills.sh` — registry drift is the #1 cause of broken installs

---

## Dependencies

### Runtime (for `tools/` scripts)
- **bash** (>=4) — all tools are POSIX-compatible shell
- **yamllint** — used by `format-check.sh` for YAML validation
- **markdownlint-cli** (optional) — markdown quality checks in `format-check.sh`
- **python3** (>=3.8) — `add-openclaw-metadata.py` and YAML parsing helpers

### CI
- **GitHub Actions** — runs `validate-skills.yml` workflow on push/PR
- Validation job mirrors the local `tools/validate-skills.sh` invocation

### Install target
- **Claude Code** — skills install to `~/.claude/skills/`, hooks to `~/.claude/hooks/`, plugins to `~/.claude/plugins/`

---

## Domain Context

### Why this repo exists

Claude Code (and any LLM agent framework) is powerful but generic out of the box. For specialized work you end up re-explaining context, missing domain best practices, and getting responses that don't match your operational workflow.

Skills fix this by treating context as a versioned, installable artifact. Each skill is a self-contained transformation: load it, get specialized behavior; uninstall it, return to default. Agent skills extend the same idea to typed capabilities consumed by orchestration frameworks — the skill is the contract, the framework is the runtime.

### How this fits the broader portfolio

This repo is the upstream source for the daily Claude Code workflow across all of AreteDriver's projects. Skills like `/decision-log`, `/handoff`, `/content-scrubber`, `/security-auditor`, and `/composite-scorer` are loaded into every session via `~/.claude/`. Workflows like `release-engineering` and `feature-implementation` coordinate multi-step builds across the project portfolio (animus, memboot, anchormd, BenchGoblins, etc.).

### Public by design

The repo is MIT-licensed and public so other Claude Code users can install bundles directly. The skill format is portable — agent-skill `schema.yaml` files map cleanly onto any agent framework that accepts typed capability declarations, not just the specific one this repo originated against.

### Out of scope

- Skills for specific company workflows or proprietary systems
- Skills that hardcode personal credentials or environment-specific paths
- Skills that depend on private repos or unpublished packages

---

## Git Conventions

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`
- Branch: `main`
- Run `tools/validate-skills.sh` AND `tools/format-check.sh` before pushing
- CI runs the same two checks plus the bundle-reference resolver
