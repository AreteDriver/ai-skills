---
title: AI Skills Logical Directory Tree
source_id: SRC-AIS-REPO-002
status: under-review
authority: high
owner: Engineering
date_created: 2026-06-18
date_collected: 2026-06-18
current: true
sensitive: false
related_documents:
  - sources/repository/repository-inventory.md
---

# Logical Directory Tree

```text
ai-skills/
├── .github/
│   └── workflows/
│       └── validate-skills.yml
├── agents/
│   ├── analysis/
│   ├── browser/
│   ├── email/
│   ├── integrations/
│   ├── orchestration/
│   └── system/
├── decisions/
├── docs/
│   ├── arete/
│   ├── assets/
│   └── legacy/
├── examples/
├── hooks/
├── intel/
├── personas/
│   ├── api/
│   ├── claude-code/
│   ├── data/
│   ├── devops/
│   ├── domain/
│   ├── engineering/
│   ├── security/
│   └── web/
├── playbooks/
├── plugins/
├── prompts/
├── templates/
├── tools/
├── workflows/
├── bundles.yaml
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE
├── README.md
├── registry.yaml
└── workflow-schema.yaml
```

## Proposed Canonical Structure

```text
ai-skills/
├── skills/
│   ├── personas/<category>/<name>/
│   ├── agents/<category>/<name>/
│   └── workflows/<name>/
├── bundles/
│   └── *.yaml
├── schemas/
│   ├── skill-manifest.schema.json
│   ├── agent-interface.schema.json
│   ├── workflow.schema.json
│   ├── bundle.schema.json
│   └── registry.schema.json
├── evals/
│   ├── cases/
│   ├── rubrics/
│   ├── fixtures/
│   └── baselines/
├── adapters/
│   ├── claude-code/
│   ├── openclaw/
│   ├── codex/
│   └── generic/
├── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── security/
├── docs/
│   ├── architecture/
│   ├── guides/
│   ├── reference/
│   └── generated/
├── governance/
│   ├── adr/
│   ├── compatibility/
│   └── deprecations/
├── registry.generated.yaml
└── pyproject.toml
```

## Migration Note

A physical restructure is optional. The essential change is logical: per-skill manifests become canonical, while the registry, bundle index, README tables, counts, and docs are generated.
