# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-14

### Added
- **Installer** (`tools/install.sh`) — CLI installer with `--persona`, `--agent`,
  `--bundle`, `--all`, `--list`, `--uninstall`, and `--symlink` support
- **Bundle presets** (`bundles.yaml`) — 5 curated skill collections:
  webapp-security, release-engineering, data-pipeline, full-stack-dev, claude-code-dev
- **Format checker** (`tools/format-check.sh`) — validates YAML syntax, markdown
  quality, shell syntax, CRLF line endings, and frontmatter consistency
- **Output schemas** for top 5 personas — `review_report.schema.yaml` (code-reviewer),
  `output.schema.yaml` (senior-software-engineer, software-architect,
  security-auditor, testing-specialist)
- **Golden examples** — 7 before/after review examples demonstrating correct
  severity calibration across code review, debugging, architecture, security
  audit, and test suite generation
- **Release engineering workflow** (`workflows/release-engineering/`) — 6-phase
  end-to-end release pipeline with WHY/WHAT/HOW framework
- **Pre-commit hook** (`hooks/pre-commit-format.sh`) — runs format and skill
  validation before commits
- **Expanded validator** — 3 new checks: agent registry metadata validation,
  schema.yaml structure verification, bundle reference resolution
- **CI improvements** — format checker added to GitHub Actions workflow with
  Python YAML support

### Changed
- Updated README with installer quickstart, bundle presets table, validation
  documentation, and release-engineering workflow
- Updated CLAUDE.md with new tooling conventions
- Registry updated to 55 skills (36 personas + 16 agents + 3 workflows)

## [0.1.0] - 2025-05-01

Initial release with 54 skills across personas, agents, and workflows.

### Added
- 36 persona skills across 6 categories (engineering, data, devops, claude-code,
  security, domain)
- 16 agent skills with typed schema.yaml interfaces
- 2 workflows (context-mapping, feature-implementation)
- Skill validator (`tools/validate-skills.sh`)
- Registry (`registry.yaml`) with central skill catalog
- 4 hook scripts (tdd-guard, no-force-push, protected-paths, tool-logger)
- Example quality-gate plugin
- GitHub Actions CI for skill validation
- Quickstart guide with before/after demos
