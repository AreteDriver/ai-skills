<!-- AUTO-GENERATED from registry.yaml — do not edit manually -->
<!-- Run: python3 scripts/generate-docs.py -->

# Workflow Catalog

| Name | Description | Phase | Schema |
|------|-------------|-------|--------|
| [agent-pipeline](../../workflows/agent-pipeline/SKILL.md) | Automated Issue-to-PR-to-Merge pipeline using GitHub Actions and AI agents with review loops | full-lifecycle | ✓ |
| [conductor](../../workflows/conductor/SKILL.md) | Context-driven development workflow — interactive setup, spec generation, TDD implementation with checkpoints and revert | full-lifecycle |  |
| [context-mapping](../../workflows/context-mapping/SKILL.md) | Pre-execution context mapping phase inspired by Blitzy — maps codebase structure, identifies dependencies, and builds execution context before any agent writes code. Use before complex multi-file changes, large refactors, or unfamiliar codebases. | full-lifecycle | ✓ |
| [evaluation](../../workflows/evaluation/SKILL.md) | Evaluation-mode prompt scaffold. Use when you have candidates (options, outputs, PRs, copy variants, vendors) and need a scored comparison with a verdict — not opinions. Always produces a decision plus evidence. "It depends" is not an acceptable output. Invoke with /evaluation. | full-lifecycle |  |
| [exploration](../../workflows/exploration/SKILL.md) | Exploration-mode prompt scaffold. Use when the option space isn't mapped yet — generate distinct alternatives, surface unknowns, challenge assumptions. The output is a list of options with evidence, not a recommendation. Invoke with /exploration. | full-lifecycle |  |
| [feature-implementation](../../workflows/feature-implementation/SKILL.md) | End-to-end feature implementation workflow using WHY/WHAT/HOW framework — from requirements through context mapping, implementation, testing, and PR creation. Use when implementing a complete feature across multiple files. | full-lifecycle | ✓ |
| [feature-pipeline](../../workflows/feature-pipeline/SKILL.md) | Multi-phase feature development with checkpoint gates, parallel agent streams, and phased artifact output | full-lifecycle |  |
| [goal](../../workflows/goal/SKILL.md) | Manage the build-mode goal-loop — set, inspect, pause, resume, extend, or clear a durable build objective with a budget ceiling. Drives the goal-loop + goal-gate hooks via a repo-root .goal-active sentinel. Invoke with /goal. | full-lifecycle |  |
| [production](../../workflows/production/SKILL.md) | Production-mode prompt scaffold. Use when the decision is made and spec is clear — produce the final deliverable with no exploratory sprawl, no meta-commentary, no preamble. Output is the artifact itself, nothing else. Invoke with /production. | full-lifecycle |  |
| [release-engineering](../../workflows/release-engineering/SKILL.md) | End-to-end release workflow — preflight checks, code review, changelog generation, version bump, tagging, and publishing. Coordinates release-engineer agent, code-reviewer persona, and github-operations agent through the WHY/WHAT/HOW framework. | full-lifecycle | ✓ |
| [session-end](../../workflows/session-end/SKILL.md) | Session wrap-up workflow — captures decisions, syncs memory, reports costs, updates tasks, and commits cleanly. Run before ending any session with meaningful work. | full-lifecycle | ✓ |
| [session-start](../../workflows/session-start/SKILL.md) | Session bootstrap workflow — audits project context, suggests session template, checks service health, and pulls pending tasks. Run at the start of any non-trivial engineering session. | full-lifecycle | ✓ |
| [specification](../../workflows/specification/SKILL.md) | Specification-mode prompt scaffold. Use when the decision is made and you need a buildable, testable, reviewable spec. Output is fixed-structure with measurable acceptance criteria. Never re-argues the premise. Invoke with /specification. | full-lifecycle |  |
