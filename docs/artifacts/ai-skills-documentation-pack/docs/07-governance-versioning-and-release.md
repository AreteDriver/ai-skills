# Governance, Versioning, and Release

## Governance Model

### Maintainers

Own schemas, release gates, security policy, and breaking-change decisions.

### Category Owners

Review domain correctness and approve stable status for skills in a category.

### Contributors

Submit skills, evals, examples, and documentation under the contract.

### Security Reviewers

Approve hooks, high/critical-risk agents, installer changes, and external-side-effect capabilities.

## Lifecycle States

- `experimental` — incomplete contract or limited evidence
- `candidate` — contract-complete, under evaluation
- `stable` — all gates pass
- `deprecated` — supported temporarily, replacement identified
- `archived` — excluded from active registry and bundles

## Versioning

### Repository Version

Semantic version of the toolchain, schemas, and distribution format.

### Skill Version

Each skill has its own semantic version.

Breaking examples:

- changed output structure;
- broader or narrower permissions;
- renamed operations;
- changed required inputs;
- materially changed routing;
- removed behavior relied upon by workflows.

### Schema Version

Independent version for interchange contracts.

## Release Artifacts

A release should contain:

- source archive;
- generated registry;
- bundle catalog;
- runtime adapter outputs;
- checksums;
- provenance/attestation;
- SBOM for executable tooling;
- changelog;
- migration guide;
- quality report;
- compatibility matrix.

## Pull Request Requirements

Every skill PR includes:

- problem and user job;
- manifest;
- SKILL changes;
- examples;
- eval cases;
- security implications;
- compatibility implications;
- version bump;
- changelog fragment.

## Required Repository Governance Files

Add:

- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `SUPPORT.md`
- `GOVERNANCE.md`
- `CODEOWNERS`
- issue templates for bug, setup blocker, skill proposal, use case, and security report
- pull request template
- Dependabot or Renovate configuration
- release workflow

## Changelog Policy

Use fragments merged with each change. Generate release notes. Do not rely on maintainers remembering months of additions.

## Decision Records

Use ADRs for:

- canonical metadata source;
- risk model;
- installer rewrite;
- adapter architecture;
- lifecycle policy;
- evaluation backend;
- release signing.
