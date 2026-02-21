# AI Skills Repository

Production-ready skills for Claude Code personas, Gorgon agent capabilities, and multi-step workflows.

## Project Structure

```
ai-skills/
├── personas/              # User behavior skills (how Claude acts)
│   ├── engineering/       # SSE, architect, code-reviewer, etc.
│   ├── data/              # data-analyst, data-engineer, etc.
│   ├── devops/            # backup, monitor, networking, etc.
│   ├── claude-code/       # hooks-designer, plugin-builder, etc.
│   ├── security/          # security-auditor, accessibility-checker
│   ├── domain/            # hauling-*, eve-esi, gamedev, apple-dev, etc.
│   └── api/               # api-tester, database-ops, webhook-designer, oauth-integrator
├── agents/                # Gorgon agent capabilities (what agents can do)
│   ├── system/            # file-operations, process-runner
│   ├── browser/           # web-search, web-scrape
│   ├── email/             # email-compose
│   ├── integrations/      # github-operations, api-client
│   ├── orchestration/     # multi-agent-supervisor, agent-teams-orchestrator
│   └── analysis/          # tech-debt-auditor, release-engineer, entity-resolver, etc.
├── workflows/             # Multi-step workflow templates
│   ├── context-mapping/   # Pre-execution codebase reconnaissance
│   ├── feature-implementation/  # End-to-end feature lifecycle
│   └── release-engineering/     # Preflight → review → changelog → tag → publish
├── hooks/                 # Hook scripts for Claude Code lifecycle events
├── plugins/               # Plugin configurations bundling skills + hooks
├── bundles.yaml           # Curated skill bundles for common use cases
├── playbooks/             # Step-by-step workflow guides
├── prompts/               # Standalone prompt templates (legacy)
├── templates/             # Templates for creating new skills/prompts
├── decisions/             # Architecture Decision Records
├── tools/                 # Validation, formatting, and installer scripts
├── registry.yaml          # Central skill catalog (70 skills)
└── workflow-schema.yaml   # WHY/WHAT/HOW workflow schema definition
```

## Key Concepts

- **Personas** change how Claude behaves (expertise, tone, output format)
- **Agents** define what Gorgon agents can do (capabilities, inputs/outputs, risk levels)
- **Workflows** orchestrate multi-agent execution with the WHY/WHAT/HOW framework
- Agent skills have both `SKILL.md` (behavior) and `schema.yaml` (typed interface)
- Top personas include `output.schema.yaml` and `examples/` with golden examples

## Conventions

- All skills use YAML frontmatter with `name` and `description` fields
- Skill descriptions should be under 300 characters for reliable auto-loading
- Reference materials go in `<skill>/references/` subdirectories
- Golden examples go in `<skill>/examples/` subdirectories
- Output schemas go in `<skill>/output.schema.yaml` (or `review_report.schema.yaml` for code-reviewer)
- Agent skills must include `schema.yaml` with typed inputs/outputs
- Hook scripts must be executable (`chmod +x`) and handle stdin JSON
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
- Run both validators before committing:
  - `./tools/validate-skills.sh` — structure, frontmatter, registry
  - `./tools/format-check.sh` — YAML syntax, markdown quality, shell syntax

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `tools/validate-skills.sh` | Validate skill structure, frontmatter, registry, agent metadata, bundle refs | `./tools/validate-skills.sh [--verbose] [--fix]` |
| `tools/format-check.sh` | Check YAML syntax, markdown quality, shell syntax, line endings | `./tools/format-check.sh [--verbose] [--fix]` |
| `tools/install.sh` | Install skills, agents, bundles, and hooks to `~/.claude/` | `./tools/install.sh --list` |

## When Adding New Skills

### Persona Skills
1. Create `personas/<category>/<skill-name>/SKILL.md` following `templates/skill-template.md`
2. Include YAML frontmatter with `name` and `description`
3. Add `output.schema.yaml` defining expected response structure
4. Add golden examples in `examples/` demonstrating correct output
5. Add reference materials in `<skill-name>/references/` if needed
6. Add entry to `registry.yaml` under `personas.<category>`

### Agent Skills
1. Create `agents/<category>/<skill-name>/SKILL.md` for behavior
2. Create `agents/<category>/<skill-name>/schema.yaml` for typed interface
3. Define inputs, outputs, capabilities, risk levels, and consensus requirements
4. Add entry to `registry.yaml` under `agents.<category>`

### Workflow Skills
1. Create `workflows/<workflow-name>/SKILL.md` using WHY/WHAT/HOW framework
2. Create `workflows/<workflow-name>/schema.yaml` for the workflow interface
3. Add entry to `registry.yaml` under `workflows`

### Bundles
1. Add bundle definition to `bundles.yaml` with skills and hooks lists
2. Run `./tools/validate-skills.sh` to verify all references resolve

## Validation

```bash
./tools/validate-skills.sh           # Check all skills
./tools/validate-skills.sh --verbose  # Detailed output
./tools/validate-skills.sh --fix      # Auto-fix simple issues

./tools/format-check.sh              # Check formatting
./tools/format-check.sh --fix        # Auto-fix trailing whitespace, CRLF

# Install pre-commit hook for automatic checking
ln -sf ../../hooks/pre-commit-format.sh .git/hooks/pre-commit
```
