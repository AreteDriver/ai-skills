# Security and Trust Model

## Security Position

Skill content can change model behavior. Agent schemas can authorize tools. Hooks execute code. Bundles compose all three. The repository is therefore a software supply chain.

## Asset Classes

| Class | Example | Default Trust |
|---|---|---|
| Passive guidance | Persona Markdown | Low execution risk |
| Typed capability | Agent schema | Medium; may authorize tools |
| Workflow | Multi-step orchestration | Medium; compounds permissions |
| Reference content | Domain notes | Untrusted data unless reviewed |
| Hook | Shell script | Executable; high trust requirement |
| Adapter | Runtime transformer | Executable build logic |
| Installer | CLI | Privileged local file operation |

## Canonical Risk Model

Use two independent dimensions.

### Impact Severity

- `low` — read-only or advisory
- `medium` — modifies local project content
- `high` — external side effect, credentialed access, or broad local changes
- `critical` — destructive, irreversible, privileged, or high-consequence operation

### Approval Class

- `none` — no approval beyond invocation
- `preview` — show plan/diff before execution
- `user` — explicit user approval
- `quorum` — multiple-agent or policy approval
- `user_and_quorum` — both required

Do not overload one enum to represent both risk and consensus.

## Threat Model

### Prompt Injection

Untrusted repository content, web pages, issues, and documents may instruct the agent to ignore the skill contract.

Controls:

- distinguish instructions from data;
- isolate untrusted content;
- prohibit policy changes from retrieved text;
- include injection eval cases;
- require user approval for privilege escalation.

### Tool Overreach

A skill may request tools unrelated to its job.

Controls:

- deny-by-default allowlists;
- per-operation permissions;
- runtime adapter enforcement;
- audit log of tool calls;
- release gate for wildcard permissions.

### Data Exfiltration

A skill may transmit source, secrets, or personal information.

Controls:

- outbound-domain allowlist;
- secret scanner;
- data classification;
- explicit external-send approval;
- redaction and minimization.

### Unsafe Hooks

Hooks execute automatically in sensitive lifecycle events.

Controls:

- never auto-install by default;
- preview exact hook files and events;
- checksum and signature verification;
- static shell analysis;
- sandbox tests;
- least-privilege filesystem scope.

### Path Traversal and Overwrite

Installer paths may escape the target or overwrite unrelated assets.

Controls:

- normalized path validation;
- no `..` segments;
- staged install;
- ownership manifest;
- collision detection;
- backup and rollback.

### Supply-Chain Tampering

Repository or release artifacts may be modified.

Controls:

- signed tags or attestations;
- release checksums;
- pinned action dependencies;
- SBOM for executable tooling;
- reproducible registry digest.

## Trust Modes

| Mode | Allowed Content |
|---|---|
| `inspect-only` | Load metadata and docs only |
| `advisory` | Persona guidance; no write tools |
| `supervised` | Write tools with preview |
| `autonomous-local` | Bounded local changes with verification |
| `external-side-effect` | Explicit approval for every external action |
| `destructive` | User plus policy approval; rollback where possible |

## Security Release Gates

- no critical unresolved findings;
- no wildcard tools in stable skills without waiver;
- all hooks pass shellcheck and adversarial input tests;
- all installer writes are covered by integration tests;
- bundle permission union is displayed and approved;
- dependency audit passes;
- provenance files generated;
- injection eval suite passes.
