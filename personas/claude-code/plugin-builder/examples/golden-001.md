# Plugin Builder Response
## Example Output
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
