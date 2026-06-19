# Migration Plan: Current Repository to Contract v2

## Migration Principles

- preserve content before restructuring;
- never infer stable status automatically;
- retain aliases for renamed skills;
- separate correction commits from feature additions;
- keep a reversible migration map;
- do not break existing install paths until adapter compatibility exists.

## Step 1 — Inventory

Generate a machine-readable tree of:

- every `SKILL.md`;
- schemas;
- references;
- examples;
- hooks;
- bundles;
- templates;
- registry entries.

Produce discrepancy reports:

- filesystem-only;
- registry-only;
- name mismatch;
- duplicate slug;
- missing schema;
- stale stats;
- bundle resolution mismatch.

## Step 2 — Classify

For every skill:

- kind;
- category;
- owner;
- lifecycle;
- runtime compatibility;
- duplicate or overlap;
- security level;
- migration priority.

## Step 3 — Establish Canonical IDs

Use:

```text
persona/<category>/<name>
agent/<category>/<name>
workflow/<name>
hook/<name>
```

Maintain aliases for current basename installation.

## Step 4 — Create Manifests

Automate from current frontmatter and registry, then require human review for:

- description;
- routing;
- permissions;
- lifecycle;
- compatibility;
- dependencies;
- conflicts.

## Step 5 — Generate Registry

Build v2 registry and compare against current. Keep current registry as `registry.v1.yaml` during transition.

## Step 6 — Repair Installer

Introduce a new CLI alongside `install.sh`.

- `install.sh` becomes a compatibility wrapper;
- new CLI reads v2 registry and bundles;
- both produce equivalent installs during a transition test;
- deprecate direct Bash implementation after parity.

## Step 7 — Migrate Evals

Convert existing examples into cases. Prioritize:

1. hooks and high-risk agents;
2. installer-facing popular bundles;
3. engineering and security personas;
4. workflows;
5. remaining domain skills.

## Step 8 — Generate Docs

Replace manually maintained tables and counts. Preserve narrative content.

## Step 9 — Release Candidate

Run:

- full contract checks;
- all bundles;
- clean-machine install;
- update from v1;
- rollback;
- uninstall;
- supported adapter tests;
- security suite;
- docs link check.

## Step 10 — Major Release

Publish v2 with:

- migration guide;
- deprecated command map;
- compatibility wrapper;
- signed artifacts;
- quality report.

## Rollback

Retain:

- v1 registry;
- v1 installer tag;
- path alias map;
- migration manifest.

A failed migration must be able to restore the prior installed-state manifest.
