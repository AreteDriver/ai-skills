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
├── skills/
│   ├── senior-software-engineer/
│   │   ├── SKILL.md           # Core skill definition
│   │   └── references/
│   │       └── coding-standards.md
│   ├── senior-software-analyst/
│   │   └── SKILL.md
│   └── mentor-linux/
│       └── SKILL.md
├── prompts/
│   └── development-collection.md
└── templates/
    └── skill-template.md
```

## Prompts

The `prompts/` directory contains battle-tested prompt patterns for common workflows:

- GitHub profile optimization
- CI/CD diagnostics
- Project scaffolding
- Universal prompt template

## Creating New Skills

Use `templates/skill-template.md` as a starting point. Key elements:

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
