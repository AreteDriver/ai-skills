# AI_Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/Skills-27-blue)]()

**Production-ready Claude Code skills for software engineering, data analysis, DevOps, and domain-specific workflows.**

---

## The Problem

Claude is powerful but generic. For specialized work you end up re-explaining context, missing domain best practices, and getting responses that don't match your workflow.

**Skills fix this.** Each skill transforms Claude into a specialized persona with defined behaviors, constraints, and output formats. Load once, use everywhere.

## Skills

### Development Workflow Agents

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [senior-software-engineer](skills/senior-software-engineer/SKILL.md) | Code review, architecture, mentoring | Any coding task, PR reviews, debugging |
| [senior-software-analyst](skills/senior-software-analyst/SKILL.md) | Codebase auditing, system mapping | Unfamiliar codebases, documentation, tech debt |
| [strategic-planner](skills/strategic-planner/SKILL.md) | Feature decomposition, implementation planning | Breaking down features into actionable steps |
| [code-builder](skills/code-builder/SKILL.md) | Production-ready code implementation | Writing new features based on plans |
| [testing-specialist](skills/testing-specialist/SKILL.md) | Comprehensive test suite creation | Unit tests, integration tests, edge cases |
| [code-reviewer](skills/code-reviewer/SKILL.md) | Quality, security, and best practices review | PR reviews, security audits, code quality |
| [software-architect](skills/software-architect/SKILL.md) | System design and technical decisions | Architecture, component design, tech selection |
| [documentation-writer](skills/documentation-writer/SKILL.md) | API docs, guides, and READMEs | Documentation, developer guides, API reference |

### Data & Analytics Agents

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [data-engineer](skills/data-engineer/SKILL.md) | Data pipelines, schemas, ETL | Data ingestion, transformation, validation |
| [data-analyst](skills/data-analyst/SKILL.md) | Statistical analysis, pattern finding | EDA, hypothesis testing, insights |
| [data-visualizer](skills/data-visualizer/SKILL.md) | Charts, dashboards, visual design | Creating visualizations, dashboard layouts |
| [report-generator](skills/report-generator/SKILL.md) | Executive summaries, analytical reports | Stakeholder reports, findings documentation |

### Operational Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [file-operations](skills/file-operations/SKILL.md) | Safe filesystem operations | File CRUD with backups and validation |
| [web-search](skills/web-search/SKILL.md) | Web search with rate limiting | Gathering current information |
| [web-scrape](skills/web-scrape/SKILL.md) | Ethical web scraping | Content extraction, table parsing |
| [github-operations](skills/github-operations/SKILL.md) | Git CLI and GitHub API operations | Repos, branches, PRs, issues |
| [email-compose](skills/email-compose/SKILL.md) | Email drafting with approval workflow | Composing and sending emails safely |
| [process-management](skills/process-management/SKILL.md) | System process control | Process monitoring, service management |

### Domain-Specific Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [mentor-linux](skills/mentor-linux/SKILL.md) | Linux certification prep | RHCSA, Linux+, LPIC-1 study |
| [eve-esi](skills/eve-esi/SKILL.md) | EVE Online ESI API integration | ESI endpoints, SSO auth, rate limiting |
| [gamedev](skills/gamedev/SKILL.md) | Game dev patterns (Bevy/Rust ECS) | Building games, ECS architecture, game loops |
| [streamlit](skills/streamlit/SKILL.md) | Streamlit app patterns | Dashboards, state management, deployment |

### Infrastructure Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [perf](skills/perf/SKILL.md) | Performance profiling & optimization | Bottleneck hunting, benchmarking |
| [backup](skills/backup/SKILL.md) | Backup strategy & data integrity | Backup design, disaster recovery |
| [monitor](skills/monitor/SKILL.md) | Observability & monitoring | Logging, metrics, alerting, health checks |
| [systemd](skills/systemd/SKILL.md) | Systemd service management | Unit files, timers, journalctl |
| [networking](skills/networking/SKILL.md) | Linux networking & troubleshooting | DNS, firewalls, ports, connectivity |

## Installation

### Claude Code Native Skills (Recommended)

Copy skills directly to your Claude Code skills directory for `/skill-name` invocation:

```bash
# Clone the repo
git clone https://github.com/AreteDriver/ai_skills.git

# Copy individual skills to Claude Code
cp -r ai_skills/skills/eve-esi ~/.claude/skills/
cp -r ai_skills/skills/gamedev ~/.claude/skills/
cp -r ai_skills/skills/perf ~/.claude/skills/

# Or copy all skills at once
cp -r ai_skills/skills/* ~/.claude/skills/
```

Skills are immediately available as slash commands:
- `/eve-esi` - EVE Online API patterns
- `/gamedev` - Bevy/Rust ECS development
- `/perf` - Performance profiling
- `/backup` - Backup strategies
- `/monitor` - Observability patterns
- etc.

### Project-Level Reference

Reference skills in your project's `CLAUDE.md`:

```markdown
# CLAUDE.md

See skills from: https://github.com/AreteDriver/ai_skills

Active skills:
- senior-software-engineer (always on for code tasks)
- mentor-linux (when studying)
```

### Direct Activation

Reference the skill behavior directly in prompts:

```
"Act as senior-software-engineer: review this PR"
"Mentor-linux failure mode: break my networking"
```

## Structure

```
ai_skills/
├── skills/                              # Skill definitions (27 total)
│   ├── senior-software-engineer/        # Code review, architecture
│   ├── senior-software-analyst/         # Codebase auditing
│   ├── strategic-planner/               # Feature planning
│   ├── code-builder/                    # Code implementation
│   ├── testing-specialist/              # Test suite creation
│   ├── code-reviewer/                   # Code review
│   ├── software-architect/              # System design
│   ├── documentation-writer/            # Documentation
│   ├── data-engineer/                   # Data pipelines
│   ├── data-analyst/                    # Statistical analysis
│   ├── data-visualizer/                 # Visualizations
│   ├── report-generator/                # Reports
│   ├── file-operations/                 # Filesystem ops
│   ├── web-search/                      # Web search
│   ├── web-scrape/                      # Web scraping
│   ├── github-operations/               # GitHub/Git ops
│   ├── email-compose/                   # Email drafting
│   ├── process-management/              # Process control
│   ├── mentor-linux/                    # Linux cert prep
│   ├── eve-esi/                         # EVE Online API
│   ├── gamedev/                         # Game development
│   ├── streamlit/                       # Streamlit apps
│   ├── perf/                            # Performance
│   ├── backup/                          # Backup strategy
│   ├── monitor/                         # Observability
│   ├── systemd/                         # Systemd services
│   └── networking/                      # Linux networking
├── prompts/
│   └── development-collection.md        # Battle-tested prompt patterns
├── templates/
│   └── skill-template.md               # Template for creating new skills
├── playbooks/                           # Multi-step workflows
│   ├── full-feature.md                  # Requirements to merge workflow
│   └── debug-and-fix.md                # Bug report to verified fix workflow
├── decisions/
│   └── templates/
│       └── adr-template.md             # Architecture Decision Record template
├── SKILL_DEVELOPER_PROMPT.md            # Guide for building Claude skills
├── SKILL_TECH_SPEC.md                   # Technical spec for skill filesystem access
├── LINUX_SKILL_DEVELOPER_PROMPT_FINAL.md # Linux-specific skill dev request
├── eve-esi-skill.skill                  # EVE Online ESI API skill package
└── local-dev.skill                      # Local dev automation skill package
```

## Prompts

The `prompts/` directory contains battle-tested prompt patterns for common workflows:

- GitHub profile optimization
- CI/CD diagnostics
- Project scaffolding
- Universal prompt template

## Playbooks

The `playbooks/` directory contains multi-step workflows that chain skills together:

- **full-feature** — End-to-end from requirements to merge (design, implement, test, review)
- **debug-and-fix** — Bug report to verified fix (reproduce, diagnose, fix, verify)

## Packaged Skills

`.skill` files are self-contained skill packages with embedded references and scripts:

- **eve-esi-skill.skill** — EVE Online ESI API integration skill
- **local-dev.skill** — Local development automation skill

## Skill Development

Resources for building new skills:

- `templates/skill-template.md` — Starting point for new skills
- `SKILL_DEVELOPER_PROMPT.md` — Comprehensive guide for building Claude skills
- `SKILL_TECH_SPEC.md` — Technical spec for skill filesystem access
- `decisions/templates/adr-template.md` — ADR template for recording design choices

### Key elements of a skill:

1. **Frontmatter** - Name and description for tooling
2. **Role definition** - Who the skill acts as
3. **Core behaviors** - What it always does
4. **Constraints** - What it never does
5. **Trigger contexts** - When to activate different modes
6. **Output formats** - How responses should be structured

---

## Why Skills > System Prompts

| Aspect | System Prompts | Skills |
|--------|---------------|--------|
| **Portability** | Locked in platform | Version-controlled, shareable |
| **Composability** | One blob | Mix and match |
| **Transparency** | Hidden | Readable, auditable |
| **Evolution** | Manual updates | Git history, branches |

---

## Credits

Several skills adapted from [Gorgon](https://github.com/AreteDriver/Gorgon) multi-agent orchestration system:
- Development workflow agents (planner, builder, tester, reviewer, architect, documenter)
- Data pipeline agents (data-engineer, analyst, visualizer, reporter)
- Operational skills (file-operations, web-search, web-scrape, github-operations, email-compose, process-management)

## Author

**ARETE** - AI Enablement & Workflow Analyst

## License

MIT
