# Session Memory Manager Response
## Example Output
```
~/.claude/
├── CLAUDE.md                          # Global instructions (all projects)
├── projects/
│   └── -home-user-project-name/       # Per-project (path-encoded)
│       ├── CLAUDE.md                  # Project instructions
│       └── memory/                    # Auto-memory directory
│           ├── MEMORY.md             # Main memory (loaded in system prompt)
│           ├── debugging.md          # Topic: debugging patterns
│           ├── architecture.md       # Topic: architecture decisions
│           ├── patterns.md           # Topic: code patterns
│           └── dependencies.md       # Topic: dependency notes
```
