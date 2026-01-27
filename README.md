# ClaudeSkills

Custom Claude skills and prompt engineering resources for AI-assisted development workflows.

## What This Is

A collection of Claude Code skills that transform Claude from a general assistant into specialized personas for specific tasks. Each skill is a `.md` file that defines behaviors, constraints, and response formats.

## Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [senior-software-engineer](skills/senior-software-engineer/SKILL.md) | Code review, architecture, mentoring | Any coding task, PR reviews, debugging |
| [senior-software-analyst](skills/senior-software-analyst/SKILL.md) | Codebase auditing, system mapping | Unfamiliar codebases, documentation, tech debt |
| [mentor-linux](skills/mentor-linux/SKILL.md) | Linux certification prep | RHCSA, Linux+, LPIC-1 study |
| [eve-esi](skills/eve-esi/SKILL.md) | EVE Online ESI API integration | ESI endpoints, SSO auth, rate limiting |
| [gamedev](skills/gamedev/SKILL.md) | Game dev patterns (Bevy/Rust ECS) | Building games, ECS architecture, game loops |
| [streamlit](skills/streamlit/SKILL.md) | Streamlit app patterns | Dashboards, state management, deployment |
| [perf](skills/perf/SKILL.md) | Performance profiling & optimization | Bottleneck hunting, benchmarking |
| [backup](skills/backup/SKILL.md) | Backup strategy & data integrity | Backup design, disaster recovery |
| [monitor](skills/monitor/SKILL.md) | Observability & monitoring | Logging, metrics, alerting, health checks |
| [systemd](skills/systemd/SKILL.md) | Systemd service management | Unit files, timers, journalctl |
| [networking](skills/networking/SKILL.md) | Linux networking & troubleshooting | DNS, firewalls, ports, connectivity |

## Usage

### In Claude Code

Drop the skill folder into your project or reference it in your `CLAUDE.md`:

```markdown
# CLAUDE.md

See skills from: https://github.com/AreteDriver/ClaudeSkills

Active skills:
- senior-software-engineer (always on for code tasks)
- mentor-linux (when studying)
```

### Direct Activation

Reference the skill behavior directly:

```
"Act as senior-software-engineer: review this PR"
"Mentor-linux failure mode: break my networking"
```

## Structure

```
ClaudeSkills/
├── skills/                              # Persona-based skill definitions
│   ├── senior-software-engineer/
│   │   ├── SKILL.md                     # Code review, architecture, mentoring
│   │   └── references/
│   │       └── coding-standards.md      # Coding standards reference
│   ├── senior-software-analyst/
│   │   └── SKILL.md                     # Codebase auditing, system mapping
│   └── mentor-linux/
│       └── SKILL.md                     # Linux certification prep
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

## Author

**ARETE** - AI Enablement & Workflow Analyst

## License

MIT
