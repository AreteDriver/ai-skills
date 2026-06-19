<!-- AUTO-GENERATED from registry.yaml — do not edit manually -->
<!-- Run: python3 scripts/generate-docs.py -->

# Agent Catalog

| Name | Category | Description | Risk | Consensus | Schema |
|------|----------|-------------|------|-----------|--------|
| [entity-resolver](../../agents/analysis/entity-resolver/SKILL.md) | analysis | Resolves entity ambiguity across document corpora — fuzzy name matching, alias detection, identity consolidation, and confidence-scored entity merging | medium | majority | ✓ |
| [handoff](../../agents/analysis/handoff/SKILL.md) | analysis | Packages project state into structured context documents for agent sessions, human pickup, or Quorum IntentNodes | low | any | ✓ |
| [document-forensics](../../agents/analysis/document-forensics/SKILL.md) | analysis | Investigative methodology for analyzing document collections — provenance analysis, anomaly detection, redaction detection, and cross-document validation | medium | majority | ✓ |
| [release-engineer](../../agents/analysis/release-engineer/SKILL.md) | analysis | Automates the last mile of shipping software — verifies release readiness, generates changelogs, tags versions, and pushes releases | high | majority | ✓ |
| [context-mapper](../../agents/analysis/context-mapper/SKILL.md) | analysis | Pre-execution mapping of codebases, document collections, or problem spaces. Runs BEFORE any Gorgon workflow to give all agents shared situational awareness | low | any | ✓ |
| [technical-debt-auditor](../../agents/analysis/technical-debt-auditor/SKILL.md) | analysis | Systematic technical debt assessment — scans for security issues, correctness gaps, infrastructure debt, maintainability problems, documentation quality, and dependency freshness | low | any | ✓ |
| [workflow-debugger](../../agents/analysis/workflow-debugger/SKILL.md) | analysis | Diagnoses why Gorgon workflows fail — reads checkpoint state, agent logs, budget traces, and output contracts to produce root-cause analysis | low | any | ✓ |
| [intent-author](../../agents/analysis/intent-author/SKILL.md) | analysis | Teaches agents how to publish well-structured intents for Convergent's intent graph — schema, quality criteria, and authoring patterns | low | any | ✓ |
| [web-scrape](../../agents/browser/web-scrape/SKILL.md) | browser | Fetch and parse web content with ethical scraping practices, rate limiting, and structured extraction | low | any | ✓ |
| [web-search](../../agents/browser/web-search/SKILL.md) | browser | Search the web for information with rate limiting, caching, and structured source attribution | low | any | ✓ |
| [email-compose](../../agents/email/email-compose/SKILL.md) | email | Compose and send emails with safety controls, draft-review-approve workflow, and SMTP delivery | high | unanimous+user | ✓ |
| [github-operations](../../agents/integrations/github-operations/SKILL.md) | integrations | Repository management through Git CLI and GitHub API with branch protection, commit conventions, and security controls | medium | majority | ✓ |
| [api-client](../../agents/integrations/api-client/SKILL.md) | integrations | Authenticated HTTP API client with retry logic, rate limiting, response parsing, and structured error handling. Supports OAuth2, API key, and bearer token auth. | low | any | ✓ |
| [multi-agent-supervisor](../../agents/orchestration/multi-agent-supervisor/SKILL.md) | orchestration | Hierarchical multi-agent orchestration supervisor that decomposes tasks, delegates to specialized worker agents, tracks state, and employs triumvirate consensus for high-stakes operations | high | adaptive | ✓ |
| [agent-teams-orchestrator](../../agents/orchestration/agent-teams-orchestrator/SKILL.md) | orchestration | Designs and coordinates Claude Code Agent Teams — multi-agent collaboration where teammate sessions work in parallel with direct communication, task claiming via file locks, and cross-referencing findings | medium | majority | ✓ |
| [process-runner](../../agents/system/process-runner/SKILL.md) | system | Execute and manage subprocesses with timeout, output capture, and safety controls. Blocks dangerous commands, enforces resource limits, and returns structured results with exit codes, stdout, stderr, and timing. | medium | any | ✓ |
| [file-operations](../../agents/system/file-operations/SKILL.md) | system | Safe filesystem operations with path protection, backup enforcement, and audit logging | medium | adaptive | ✓ |
