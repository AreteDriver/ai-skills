# AI Skills Repository

This is a collection of Claude Code skills, prompts, hooks, plugins, and reference materials for extending Claude's capabilities.

## Project Structure

- `skills/` — SKILL.md definitions organized by domain
- `prompts/` — Standalone prompt templates (legacy format, prefer skills/)
- `hooks/` — Reusable hook scripts for Claude Code lifecycle events
- `plugins/` — Example plugin configurations bundling skills + hooks
- `playbooks/` — Step-by-step workflow guides
- `templates/` — Templates for creating new skills and prompts
- `decisions/` — Architecture Decision Records

## Conventions

- All skills use YAML frontmatter with `name` and `description` fields
- Skill descriptions should be under 300 characters for reliable auto-loading
- Reference materials go in `skills/<name>/references/` subdirectories
- Hook scripts must be executable (`chmod +x`) and handle stdin JSON
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`

## When Adding New Skills

1. Create `skills/<skill-name>/SKILL.md` following the template in `templates/skill-template.md`
2. Include YAML frontmatter with `name` and `description`
3. Add reference materials in `skills/<skill-name>/references/` if needed
4. Test the skill by installing it locally: `ln -s $(pwd)/skills/<name> ~/.claude/skills/<name>`

## Skill Categories

- **Engineering:** code-reviewer, senior-software-engineer, software-architect, senior-software-analyst, testing-specialist
- **Claude Code Ecosystem:** agent-teams-orchestrator, plugin-builder, hooks-designer, mcp-server-builder, session-memory-manager, cicd-pipeline
- **DevOps:** backup, monitor, networking, systemd, perf, process-management
- **Data:** data-analyst, data-engineer, data-visualizer
- **Security:** security-auditor
- **Accessibility:** accessibility-checker
- **Domain-Specific:** hauling-*, tie-dye-business-coach, eve-esi, gamedev, streamlit
- **Orchestration:** multi-agent-supervisor
