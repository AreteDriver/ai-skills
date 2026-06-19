# AI-Skills Project Charter

**Version**: 1.0  
**Date**: 2026-06-18  
**Classification**: Active  
**Owner**: AreteDriver  

---

## Purpose

Curate a **reusable AI skill library** — a catalog of prompts, personas, agents, and workflows for use across AI-assisted development and content creation projects. Skills must be installable, versioned, and documented.

## Scope

### In Scope
- Markdown-based skill definitions
- YAML registries and bundles
- Bash installer (`tools/install.sh`)
- Personas, agents, workflows, and rules
- Versioned releases with changelogs

### Out of Scope
- Runtime execution environment (handled by Animus/Claude Code)
- General-purpose package manager (not npm/pip competitor)
- GUI or web interface for skill browsing

## Success Criteria

1. README skill count matches filesystem reality
2. Installer parses `bundles.yaml` dynamically
3. All agents with `schema.yaml` files report `has_schema: true`
4. Missing templates created (`agent-template.md`, `workflow-template.md`)
5. Truth baseline passes all checks

## Constraints

- Flat directory structure (no deep nesting)
- YAML + Markdown + Bash only
- Semantic versioning
- Backward-compatible bundle definitions

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Catalog overstated | Medium | Auto-generated stats, truth baseline |
| Installer out of sync | Medium | Parse bundles.yaml dynamically |
| Scope creep to package manager | Low | Charter boundary, flat structure |

## Authority

- **Decision maker**: AreteDriver
- **Skill additions**: Personal need-driven
- **Breaking changes**: Major version bump, changelog entry

## Definition of Done

- Skill file created with frontmatter
- Registry entry accurate
- Installer handles new skill type correctly
- Truth baseline passes
- Version bumped if bundle structure changes
