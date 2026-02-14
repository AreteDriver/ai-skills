# AI Skills

[![Validate Skills](https://github.com/AreteDriver/ai-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/AreteDriver/ai-skills/actions/workflows/validate-skills.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/Skills-55-blue)]()

**Production-ready skills for Claude Code personas, Gorgon agent capabilities, and orchestrated workflows.**

---

## The Problem

Claude is powerful but generic. For specialized work you end up re-explaining context, missing domain best practices, and getting responses that don't match your workflow.

**Skills fix this.** Each skill transforms Claude into a specialized persona with defined behaviors, constraints, and output formats. Agent skills give Gorgon agents typed interfaces with risk levels and consensus requirements. Workflows coordinate them with the WHY/WHAT/HOW framework.

## Quickstart

```bash
git clone https://github.com/AreteDriver/ai-skills.git
cd ai-skills

# Install a single skill
./tools/install.sh --persona code-reviewer

# Install a curated bundle
./tools/install.sh --bundle webapp-security

# Install everything
./tools/install.sh --all

# See what's available
./tools/install.sh --list
```

**See it in action:** Ask Claude to review a function with SQL injection — with the skill loaded, you get severity-ranked findings with line references and concrete fixes instead of vague suggestions.

See the full [Quickstart Guide](examples/quickstart/README.md) with before/after comparisons for code review, architecture advice, and feature implementation workflows.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   ai-skills                      │
├─────────────────┬───────────────┬───────────────┤
│    Personas     │    Agents     │   Workflows   │
│  (how Claude    │ (what Gorgon  │ (multi-step   │
│   behaves)      │  agents do)   │  execution)   │
├─────────────────┼───────────────┼───────────────┤
│ 36 skills       │ 16 skills     │ 3 workflows   │
│ SKILL.md only   │ SKILL.md +    │ SKILL.md +    │
│                 │ schema.yaml   │ schema.yaml   │
└─────────────────┴───────────────┴───────────────┘
```

## Personas — User Behavior Skills

### Engineering (7)

| Skill | Purpose | Path |
|-------|---------|------|
| [senior-software-engineer](personas/engineering/senior-software-engineer/SKILL.md) | Code review, architecture, mentoring | `personas/engineering/` |
| [senior-software-analyst](personas/engineering/senior-software-analyst/SKILL.md) | Codebase auditing, system mapping | `personas/engineering/` |
| [software-architect](personas/engineering/software-architect/SKILL.md) | System design, technical decisions | `personas/engineering/` |
| [code-reviewer](personas/engineering/code-reviewer/SKILL.md) | Quality, security, best practices | `personas/engineering/` |
| [code-builder](personas/engineering/code-builder/SKILL.md) | Production-ready implementation | `personas/engineering/` |
| [testing-specialist](personas/engineering/testing-specialist/SKILL.md) | Test suite creation, TDD | `personas/engineering/` |
| [documentation-writer](personas/engineering/documentation-writer/SKILL.md) | API docs, guides, READMEs | `personas/engineering/` |

### Data (4)

| Skill | Purpose | Path |
|-------|---------|------|
| [data-engineer](personas/data/data-engineer/SKILL.md) | Pipelines, schemas, ETL | `personas/data/` |
| [data-analyst](personas/data/data-analyst/SKILL.md) | Statistical analysis, insights | `personas/data/` |
| [data-visualizer](personas/data/data-visualizer/SKILL.md) | Charts, dashboards | `personas/data/` |
| [report-generator](personas/data/report-generator/SKILL.md) | Executive summaries | `personas/data/` |

### DevOps (6)

| Skill | Purpose | Path |
|-------|---------|------|
| [backup](personas/devops/backup/SKILL.md) | Backup strategy, disaster recovery | `personas/devops/` |
| [monitor](personas/devops/monitor/SKILL.md) | Observability, alerting | `personas/devops/` |
| [networking](personas/devops/networking/SKILL.md) | Network config, troubleshooting | `personas/devops/` |
| [systemd](personas/devops/systemd/SKILL.md) | Service management, unit files | `personas/devops/` |
| [perf](personas/devops/perf/SKILL.md) | Performance profiling | `personas/devops/` |
| [process-management](personas/devops/process-management/SKILL.md) | Process lifecycle | `personas/devops/` |

### Claude Code Ecosystem (5)

| Skill | Purpose | Path |
|-------|---------|------|
| [hooks-designer](personas/claude-code/hooks-designer/SKILL.md) | Hook design, lifecycle events | `personas/claude-code/` |
| [plugin-builder](personas/claude-code/plugin-builder/SKILL.md) | Plugin packaging | `personas/claude-code/` |
| [mcp-server-builder](personas/claude-code/mcp-server-builder/SKILL.md) | MCP server implementation | `personas/claude-code/` |
| [session-memory-manager](personas/claude-code/session-memory-manager/SKILL.md) | Cross-session context | `personas/claude-code/` |
| [cicd-pipeline](personas/claude-code/cicd-pipeline/SKILL.md) | CI/CD for Claude Code | `personas/claude-code/` |

### Security (2)

| Skill | Purpose | Path |
|-------|---------|------|
| [security-auditor](personas/security/security-auditor/SKILL.md) | OWASP audit, vulnerability assessment | `personas/security/` |
| [accessibility-checker](personas/security/accessibility-checker/SKILL.md) | WCAG 2.2 compliance | `personas/security/` |

### Domain-Specific (12)

| Skill | Purpose | Path |
|-------|---------|------|
| [mentor-linux](personas/domain/mentor-linux/SKILL.md) | Linux cert prep (RHCSA, Linux+) | `personas/domain/` |
| [eve-esi](personas/domain/eve-esi/SKILL.md) | EVE Online ESI API | `personas/domain/` |
| [gamedev](personas/domain/gamedev/SKILL.md) | Game dev (Bevy/Rust ECS) | `personas/domain/` |
| [streamlit](personas/domain/streamlit/SKILL.md) | Streamlit apps | `personas/domain/` |
| [strategic-planner](personas/domain/strategic-planner/SKILL.md) | Business strategy | `personas/domain/` |
| [hauling-business-advisor](personas/domain/hauling-business-advisor/SKILL.md) | Junk hauling ops | `personas/domain/` |
| [hauling-image-estimator](personas/domain/hauling-image-estimator/SKILL.md) | Visual load estimation | `personas/domain/` |
| [hauling-job-scheduler](personas/domain/hauling-job-scheduler/SKILL.md) | Job scheduling | `personas/domain/` |
| [hauling-lead-qualifier](personas/domain/hauling-lead-qualifier/SKILL.md) | Lead qualification | `personas/domain/` |
| [hauling-quote-generator](personas/domain/hauling-quote-generator/SKILL.md) | Quote generation | `personas/domain/` |
| [tie-dye-business-coach](personas/domain/tie-dye-business-coach/SKILL.md) | Tie-dye business coaching | `personas/domain/` |
| [apple-dev-best-practices](personas/domain/apple-dev-best-practices/SKILL.md) | Apple platform dev (Swift, SwiftUI) | `personas/domain/` |

## Agents — Gorgon Capabilities

Agent skills define typed interfaces with inputs, outputs, risk levels, and Triumvirate consensus requirements.

| Agent | Category | Risk | Consensus | Description |
|-------|----------|------|-----------|-------------|
| [file-operations](agents/system/file-operations/SKILL.md) | system | medium | destructive ops | Safe filesystem operations |
| [process-runner](agents/system/process-runner/SKILL.md) | system | medium | none | Subprocess execution with safety controls |
| [web-search](agents/browser/web-search/SKILL.md) | browser | low | none | Rate-limited web search |
| [web-scrape](agents/browser/web-scrape/SKILL.md) | browser | low | none | Ethical web scraping |
| [email-compose](agents/email/email-compose/SKILL.md) | email | high | send ops | Draft-review-send email workflow |
| [github-operations](agents/integrations/github-operations/SKILL.md) | integrations | medium | push ops | Git CLI and GitHub API |
| [api-client](agents/integrations/api-client/SKILL.md) | integrations | low | none | Authenticated HTTP API client |
| [multi-agent-supervisor](agents/orchestration/multi-agent-supervisor/SKILL.md) | orchestration | medium | adaptive | Gorgon supervisor with Triumvirate |
| [agent-teams-orchestrator](agents/orchestration/agent-teams-orchestrator/SKILL.md) | orchestration | medium | none | Claude Code Agent Teams |
| [technical-debt-auditor](agents/analysis/technical-debt-auditor/SKILL.md) | analysis | low | none | Repo health scoring (5 sub-agents) |
| [release-engineer](agents/analysis/release-engineer/SKILL.md) | analysis | medium | publish | Last-mile shipping automation |
| [entity-resolver](agents/analysis/entity-resolver/SKILL.md) | analysis | low | none | Fuzzy entity matching + dedup |
| [context-mapper](agents/analysis/context-mapper/SKILL.md) | analysis | low | none | Pre-execution project mapping |
| [workflow-debugger](agents/analysis/workflow-debugger/SKILL.md) | analysis | low | none | Gorgon failure diagnosis |
| [document-forensics](agents/analysis/document-forensics/SKILL.md) | analysis | low | none | Investigative document analysis |
| [intent-author](agents/analysis/intent-author/SKILL.md) | analysis | low | none | Convergent intent authoring |

## Workflows — Multi-Step Execution

Workflows use the **WHY/WHAT/HOW** framework to ensure clear intent, scope, and execution strategy.

| Workflow | Phase | Description |
|----------|-------|-------------|
| [context-mapper](workflows/context-mapping/SKILL.md) | pre-execution | Codebase reconnaissance before agents write code |
| [feature-implementation](workflows/feature-implementation/SKILL.md) | full-lifecycle | Requirements → context → design → implement → test → PR |
| [release-engineering](workflows/release-engineering/SKILL.md) | full-lifecycle | Preflight → review → changelog → version → tag → publish |

### WHY/WHAT/HOW Framework

Every workflow captures three dimensions:

- **WHY** — Intent: goal, motivation, success criteria, anti-goals
- **WHAT** — Scope: files in/out of scope, dependencies, data flows
- **HOW** — Plan: strategy, step sequence, patterns, risks, quality gates

See `workflow-schema.yaml` for the full schema definition.

## Installation

### Installer (recommended)

```bash
git clone https://github.com/AreteDriver/ai-skills.git
cd ai-skills

# Install a single persona
./tools/install.sh --persona code-reviewer

# Install a curated bundle (see below)
./tools/install.sh --bundle full-stack-dev

# Install everything
./tools/install.sh --all

# Symlink for development (edit in repo, changes appear in Claude Code)
./tools/install.sh --persona code-reviewer --symlink

# List all available skills and bundles
./tools/install.sh --list

# Remove installed skills
./tools/install.sh --uninstall
```

### Manual Installation

```bash
# Copy persona skills
cp -r personas/engineering/code-reviewer ~/.claude/skills/

# Or symlink for development
ln -s $(pwd)/personas/engineering/code-reviewer ~/.claude/skills/code-reviewer
```

### Project-Level Reference

```markdown
# CLAUDE.md
See skills from: https://github.com/AreteDriver/ai-skills

Active skills:
- senior-software-engineer (always on for code tasks)
- mentor-linux (when studying)
```

## Bundle Presets

Curated skill collections for common use cases. Install with `./tools/install.sh --bundle <name>`.

| Bundle | Skills | Use Case |
|--------|--------|----------|
| `webapp-security` | code-reviewer, security-auditor, testing-specialist, accessibility-checker | Secure web app development |
| `release-engineering` | code-reviewer, cicd-pipeline | Shipping releases with confidence |
| `data-pipeline` | data-engineer, data-analyst, data-visualizer, report-generator | End-to-end data engineering |
| `full-stack-dev` | senior-software-engineer, code-reviewer, testing-specialist, software-architect, documentation-writer | Full engineering stack |
| `claude-code-dev` | hooks-designer, plugin-builder, mcp-server-builder, cicd-pipeline, session-memory-manager | Building Claude Code extensions |

Bundle definitions live in `bundles.yaml`. Add your own by following the same format.

## Validation

```bash
# Validate all skills (structure, frontmatter, registry consistency)
./tools/validate-skills.sh

# Check formatting (YAML syntax, markdown quality, shell syntax, line endings)
./tools/format-check.sh

# Verbose output
./tools/validate-skills.sh --verbose
./tools/format-check.sh --verbose

# Auto-fix issues (hook permissions, trailing whitespace, CRLF)
./tools/validate-skills.sh --fix
./tools/format-check.sh --fix
```

Both validators run in CI on every push and PR. See `.github/workflows/validate-skills.yml`.

## Registry

`registry.yaml` is the central catalog of all skills. Gorgon's `SkillLibrary` loader uses it to discover, validate, and load skills at runtime.

```yaml
# Query the registry
personas.engineering        # 7 skills
agents.system               # 2 skills (file-operations, process-runner)
workflows                   # 3 workflows (context-mapper, feature-implementation, release-engineering)
```

## Skill Development

### Creating a Persona
```bash
mkdir -p personas/<category>/<skill-name>
cp templates/skill-template.md personas/<category>/<skill-name>/SKILL.md
# Edit SKILL.md, add to registry.yaml
./tools/validate-skills.sh
```

### Creating an Agent
```bash
mkdir -p agents/<category>/<skill-name>
# Create SKILL.md (behavior) + schema.yaml (typed interface)
# Add to registry.yaml
./tools/validate-skills.sh
```

### Key Elements of a Skill

1. **Frontmatter** — `name` and `description` for tooling
2. **Role definition** — who the skill acts as
3. **Core behaviors** — what it always/never does
4. **Trigger contexts** — when to activate different modes
5. **Output formats** — how responses are structured
6. **Constraints** — hard limits on behavior

Agent skills additionally require:
7. **schema.yaml** — typed inputs, outputs, capabilities, risk levels, consensus requirements

## Supporting Infrastructure

| Directory | Purpose |
|-----------|---------|
| `bundles.yaml` | Curated skill bundles for common use cases |
| `examples/` | Quickstart guide with before/after demos |
| `hooks/` | 4 executable hook scripts (tdd-guard, no-force-push, protected-paths, tool-logger) |
| `plugins/` | Example quality-gate plugin bundling skills + hooks |
| `playbooks/` | Multi-step workflow guides (full-feature, debug-and-fix) |
| `prompts/` | 7 legacy prompt templates |
| `templates/` | Skill and prompt templates |
| `decisions/` | ADR template |
| `tools/` | `validate-skills.sh`, `format-check.sh`, `install.sh` |

## Credits

Skills adapted from [Gorgon](https://github.com/AreteDriver/Gorgon) multi-agent orchestration system and the original ClaudeSkills repository.

## Author

**ARETE** — AI Enablement & Workflow Analyst

## License

MIT
