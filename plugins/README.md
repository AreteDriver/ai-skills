# Claude Code Plugins

Example plugin configurations for bundling skills, hooks, and MCP servers into distributable packages.

## What Are Plugins?

Plugins are the distribution format for Claude Code extensions. A plugin bundles related skills, hooks, agent definitions, and MCP server configurations into a single shareable package with a `plugin.json` manifest.

## Example Plugins

### quality-gate

A plugin that enforces code quality standards:
- **Skills:** code-reviewer, security-auditor
- **Hooks:** TDD guard, force-push protection, protected paths, tool logger
- **Purpose:** Ensures code quality gates are enforced automatically

## Plugin Structure

```
my-plugin/
├── plugin.json              # Manifest (required)
├── README.md                # Documentation
├── LICENSE                  # License
├── skills/                  # Skill definitions
│   └── my-skill/
│       └── SKILL.md
├── hooks/                   # Hook scripts
│   └── my-hook.sh
├── agents/                  # Agent definitions
│   └── agent.json
└── mcp/                     # MCP server configs
    └── server.json
```

## Installation

```bash
# Clone and symlink
git clone https://github.com/user/my-plugin.git
ln -s $(pwd)/my-plugin ~/.claude/plugins/my-plugin

# Or copy to project
cp -r my-plugin .claude/plugins/

# Or via CLI (if registry supports it)
npx claude-plugins install my-plugin
```

## Creating Plugins

See the `plugin-builder` skill for comprehensive guidance on creating, testing, and publishing plugins.
