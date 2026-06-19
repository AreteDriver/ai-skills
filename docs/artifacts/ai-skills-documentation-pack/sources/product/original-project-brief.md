---
title: AI Skills Project Brief
source_id: SRC-AIS-PROD-001
status: active
authority: canonical
owner: AreteDriver
date_created: 2026-06-18
date_collected: 2026-06-18
current: true
sensitive: false
related_documents:
  - docs/01-product-and-user-model.md
  - plans/10-out-of-10-roadmap.md
---

# AI Skills Project Brief

## Purpose

Create a trustworthy, portable, production-ready library of skills that changes AI behavior, defines typed agent capabilities, and coordinates multi-step work.

## Product Thesis

Generic AI agents become useful when context, operating policy, domain knowledge, tool boundaries, output contracts, and verification behavior are packaged as versioned artifacts.

## Intended Users

- Claude Code power users
- AI-assisted software engineers
- Multi-agent framework builders
- Small technical teams standardizing AI workflows
- Domain operators who need repeatable expert behavior
- Portfolio owners managing consistent AI practices across repositories

## Core Product Objects

1. **Persona** — changes how the model reasons, communicates, and structures work.
2. **Agent capability** — defines typed operations, permissions, risks, inputs, and outputs.
3. **Workflow** — coordinates steps, gates, checkpoints, and handoffs.
4. **Bundle** — curates compatible skills for a concrete job.
5. **Hook** — enforces local lifecycle policy around tool use.
6. **Evaluation suite** — proves a skill behaves as claimed.
7. **Registry** — generated index for discovery and installation.

## Success Criteria

The project reaches 10/10 when:

- every skill is uniquely identified, versioned, validated, and evaluated;
- the filesystem, manifests, registry, bundles, README, and installer cannot drift;
- installation is atomic, reversible, idempotent, and secure;
- risk, permissions, and approval requirements are explicit;
- each stable skill has behavioral evidence, not only valid Markdown;
- releases are reproducible and include provenance;
- users can search, inspect, install, update, verify, and remove skills safely;
- documentation is generated from authoritative contracts;
- deprecated and experimental content is clearly separated from stable content.

## Non-Goals

- Hiding proprietary credentials or company-specific secrets in public skills
- Treating large prompt text as proof of quality
- Auto-installing executable hooks without explicit consent
- Claiming framework portability without compatibility tests
- Preserving every historical skill indefinitely
