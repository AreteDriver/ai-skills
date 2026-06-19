# Executive Assessment

## Bottom Line

The project has crossed the line from a prompt collection into a software distribution system, but its engineering controls have not fully caught up.

The content itself is often strong. The repository contains typed agent schemas, orchestration workflows, hooks, bundles, installers, validation, and CI. That is real product architecture.

The weakness is not ambition. It is **truth management**.

A user cannot currently trust that:

- the documented inventory is accurate;
- a named bundle can be installed;
- the installed bundle matches its definition;
- an agent's registry metadata reflects its files;
- a passing CI run means the repository is contract-consistent;
- uninstall will remove only assets owned by this project;
- a skill has been behaviorally tested.

That prevents a 10/10 rating.

## Scorecard

| Dimension | Score | Assessment |
|---|---:|---|
| Product thesis | 9.0 | Clear and valuable |
| Breadth of content | 8.5 | Strong portfolio across engineering, web, data, operations, and workflows |
| Skill depth | 8.0 | Several sophisticated skills and schemas |
| Information architecture | 7.5 | Good conceptual separation, but registry drift |
| Documentation completeness | 7.0 | Many useful docs; no canonical spine |
| Documentation accuracy | 4.5 | Counts, tables, and commands are stale |
| Installer reliability | 4.0 | Catalog duplication breaks documented bundles |
| Contract consistency | 4.5 | Risk vocabulary and schema flags conflict |
| CI and structural validation | 6.0 | Useful baseline; too permissive |
| Behavioral evaluation | 3.0 | No governing executable eval system |
| Security and trust | 5.5 | Risk concepts exist; executable distribution boundary is immature |
| Release governance | 5.0 | Changelog and semantic claims are not synchronized |
| **Weighted maturity** | **6.7** | Strong foundation, unreliable control plane |

## What Is Already Excellent

1. **The three-part model is correct.** Personas, capabilities, and workflows are meaningfully different artifacts.
2. **Typed agent schemas are the right direction.** The technical-debt auditor schema demonstrates mature routing, inputs, outputs, verification, and safety metadata.
3. **Bundles turn the library into products.** They map skills to user jobs.
4. **The v2 template contains strong ideas.** Negative routing, bounded retries, checkpoints, trust, and parallel safety are material improvements.
5. **The repository is public and portable.** Markdown/YAML makes inspection and contribution accessible.
6. **Validation already exists.** The project does not need to start from zero; it needs stricter enforcement and consolidation.

## What Must Change

### 1. End Manual Duplication

Counts, paths, bundle contents, schema flags, and reference tables must be generated. A production catalog cannot be maintained in five places.

### 2. Make Installation a Transaction

Installation must resolve dependencies, preview permissions, stage changes, verify contents, write an ownership manifest, and roll back on failure.

### 3. Test Behavior

A syntactically valid skill can still be vague, contradictory, unsafe, over-broad, or ineffective. Every stable skill needs executable cases.

### 4. Separate Core Contract from Runtime Adapters

Claude Code, OpenClaw, Codex, and other runtimes should consume a neutral skill contract through adapters. Runtime-specific metadata should not pollute the core schema.

### 5. Treat Hooks as Executable Supply Chain

Hooks are code, not documentation. Their installation requires explicit consent, review, checksums, permissions, and security tests.

## 10/10 Definition

A 10/10 release is one where a new user can:

1. run `ai-skills doctor`;
2. search the catalog;
3. inspect a skill's purpose, risk, permissions, compatibility, version, and eval score;
4. preview a bundle installation;
5. install atomically;
6. verify the installed state;
7. update or roll back;
8. remove only project-owned files;
9. reproduce the same result from a signed release;
10. trust that documentation was generated from validated source data.
