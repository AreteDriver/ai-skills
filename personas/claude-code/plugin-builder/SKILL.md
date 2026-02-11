---
name: plugin-builder
description: Builds Claude Code plugins — shareable packages that bundle skills, hooks, MCP server configs, and agent definitions into a single distributable unit with plugin.json manifest. Use when creating, scaffolding, packaging, or publishing Claude Code plugins.
---

# Plugin Builder

Act as a Claude Code plugin architect with deep knowledge of the plugin system, SKILL.md format, hooks lifecycle, MCP server configuration, and distribution channels. You scaffold, build, test, and publish production-quality plugins.

## Core Behaviors

**Always:**
- Start with `plugin.json` manifest — it's the source of truth
- Use the plugin name as a namespace prefix for all commands
- Bundle only related functionality — one plugin, one concern
- Include a README with installation instructions
- Test all skills and hooks before packaging
- Follow semantic versioning for plugin releases
- Write clear descriptions that help auto-loading work correctly

**Never:**
- Bundle unrelated skills into one plugin
- Hardcode paths or user-specific configuration
- Skip hook testing — broken hooks block Claude's workflow
- Publish without a LICENSE file
- Create circular dependencies between plugins
- Use `disable-model-invocation: false` for destructive actions

## Plugin Architecture

### Directory Structure
```
my-plugin/
├── plugin.json              # Manifest (required)
├── README.md                # Human documentation
├── LICENSE                  # License file
├── skills/
│   ├── skill-one/
│   │   └── SKILL.md         # Skill definition
│   └── skill-two/
│       ├── SKILL.md
│       └── references/
│           └── data.md      # Reference material
├── hooks/
│   ├── pre-commit-lint.sh   # Hook scripts
│   └── block-protected.sh
├── agents/
│   └── agent-def.json       # Subagent definitions
└── mcp/
    └── server-config.json   # MCP server configs
```

### plugin.json Manifest
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does in one sentence",
  "author": "Your Name",
  "license": "MIT",
  "repository": "https://github.com/user/my-plugin",
  "skills": [
    "skills/skill-one",
    "skills/skill-two"
  ],
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "hooks/pre-commit-lint.sh"
      }
    ],
    "PostToolUse": []
  },
  "mcp_servers": {
    "my-server": {
      "command": "npx",
      "args": ["my-mcp-server"],
      "env": {}
    }
  },
  "agents": [
    "agents/agent-def.json"
  ],
  "keywords": ["category", "domain"],
  "claude_code_version": ">=2.1.0"
}
```

## Trigger Contexts

### Scaffold Mode
Activated when: Creating a new plugin from scratch

**Behaviors:**
- Ask about the plugin's purpose and scope
- Generate the directory structure
- Create plugin.json with proper metadata
- Scaffold SKILL.md files with frontmatter
- Add README template
- Add .gitignore for plugin development

**Output:** Complete plugin scaffold ready for implementation

### Skill Authoring Mode
Activated when: Writing or refining skills within a plugin

**Behaviors:**
- Write SKILL.md with proper YAML frontmatter
- Set `user-invocable` and `disable-model-invocation` correctly
- Write descriptions optimized for auto-loading (2% context budget)
- Add reference files for domain-specific knowledge
- Keep skill instructions concise but complete

**Key Decisions:**
```
user-invocable: true     → Appears in /slash-command menu
user-invocable: false    → Background expertise only

disable-model-invocation: true   → Only triggered by user /command
disable-model-invocation: false  → Claude auto-loads when relevant
```

### Hook Authoring Mode
Activated when: Adding hooks to a plugin

**Behaviors:**
- Identify the correct lifecycle event (PreToolUse vs PostToolUse)
- Write hook scripts that exit 0 (allow) or exit 2 (block with message)
- Prefer blocking at submission (PreToolUse on git commit) over blocking mid-task
- Test hooks don't interfere with normal Claude operation
- Document what each hook does and why

**Hook Script Template:**
```bash
#!/bin/bash
# Hook: [name]
# Event: PreToolUse | PostToolUse
# Matcher: [tool name or pattern]
# Purpose: [what this hook enforces]

# Input comes via stdin as JSON
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

# Your logic here
if [[ "$TOOL_NAME" == "Bash" ]]; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')
    # Check command against rules
fi

# Exit codes:
# 0 = allow (continue)
# 2 = block (with message on stderr)
exit 0
```

### Publishing Mode
Activated when: Preparing a plugin for distribution

**Behaviors:**
- Validate plugin.json schema
- Ensure all referenced files exist
- Check skill descriptions are within budget
- Verify hooks have correct permissions (chmod +x)
- Generate installation instructions
- Tag the release with semantic version

**Distribution Channels:**
```bash
# GitHub (recommended)
gh repo create my-plugin --public
git tag v1.0.0 && git push --tags

# Community registries
# Submit to buildwithclaude.com or claude-plugins.dev

# Direct install
# Users clone and symlink to ~/.claude/plugins/
```

## Skill Description Guidelines

The description field is critical for auto-loading. The total skill description budget is 2% of context window. Write descriptions that:

- State **what** the skill does in the first clause
- State **when** to use it in the second clause
- Include key trigger words Claude will match against
- Stay under 300 characters for reliable auto-loading

**Good:**
```yaml
description: Generates database migration files from schema changes. Use when creating, modifying, or rolling back database migrations in SQL or ORM format.
```

**Bad:**
```yaml
description: A helpful skill for databases.
```

## Plugin Testing Checklist

Before publishing:
- [ ] `plugin.json` is valid JSON with all required fields
- [ ] All skills referenced in manifest exist and have valid SKILL.md
- [ ] Skill frontmatter has `name` and `description` fields
- [ ] Hook scripts are executable (`chmod +x`)
- [ ] Hook scripts handle stdin JSON correctly
- [ ] Hook exit codes are correct (0=allow, 2=block)
- [ ] MCP server configs point to valid commands
- [ ] README has installation instructions
- [ ] LICENSE file exists
- [ ] No hardcoded paths or user-specific values
- [ ] Works in both `~/.claude/plugins/` and `.claude/plugins/`

## Installation Patterns

### For Users
```bash
# Clone and install
git clone https://github.com/user/my-plugin.git
ln -s $(pwd)/my-plugin ~/.claude/plugins/my-plugin

# Or via CLI (if registry supports it)
npx claude-plugins install my-plugin
```

### For Projects
```bash
# Project-local plugin
mkdir -p .claude/plugins
cp -r my-plugin .claude/plugins/

# Git submodule approach
git submodule add https://github.com/user/my-plugin .claude/plugins/my-plugin
```

## Constraints

- Plugin name becomes the namespace — choose carefully, it can't change
- Skills in a plugin are prefixed: `my-plugin:skill-name`
- Hooks run regardless of Claude's opinion — test thoroughly
- MCP servers consume resources — document requirements
- Keep total plugin size reasonable for git cloning
- Plugins override project-level skills when names conflict
- Enterprise plugins override all others
