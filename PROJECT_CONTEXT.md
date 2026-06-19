# AI-Skills — Project Context

**Classification**: Active  
**Version**: 1.0.0 (needs update)  
**Owner**: AreteDriver  
**Repository**: https://github.com/AreteDriver/ai-skills  
**Branch**: main  
**Last updated**: 2026-06-18  
**Next review**: 2026-07-18  

---

## Technology Stack

- **Formats**: YAML, Markdown, Bash
- **Structure**: Flat (no deep nesting)
- **Registry**: `registry.yaml` (hand-maintained, needs auto-generation)
- **Bundles**: `bundles.yaml` (14 bundles)
- **Installer**: `tools/install.sh` (hard-codes 10 bundles, needs dynamic parse)

## Key Directories

| Path | Purpose |
|------|---------|
| `personas/` | 114 persona definitions |
| `agents/` | 17 agent definitions |
| `workflows/` | 13 workflow definitions |
| `rules/` | Reusable rules |
| `tools/` | Installer scripts |
| `registry.yaml` | Skill registry (out of sync with filesystem) |
| `bundles.yaml` | Bundle definitions |

## Current Milestone

Fix catalog truth: README claims fewer skills than exist; installer out of sync with bundles.

## Quick Links

- [ROADMAP.md](ROADMAP.md)
- [PROJECT_CHARTER.md](PROJECT_CHARTER.md)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
