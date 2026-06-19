# Registry Contract v2

## Decision

The registry is a **generated artifact**. It is not manually edited.

## Inputs

- validated `manifest.yaml` files;
- computed file digests;
- evaluation results;
- adapter compatibility results;
- deprecation records.

## Output Shape

```yaml
schema_version: "2.0"
generated_at: "2026-06-18T00:00:00Z"
repository_version: "2.0.0"
source_digest: "sha256:..."

skills:
  persona/engineering/code-reviewer:
    path: personas/engineering/code-reviewer
    name: code-reviewer
    version: 2.1.0
    kind: persona
    category: engineering
    lifecycle: stable
    description: ...
    risk_severity: low
    approval: none
    parallel_safe: true
    has_interface_schema: false
    has_output_schema: true
    eval:
      score: 0.92
      cases: 8
      passed: 8
    compatibility:
      claude-code: compatible
      openclaw: compatible
    digest: sha256:...

stats:
  total: 103
  by_kind:
    persona: 70
    agent: 20
    workflow: 13
  by_lifecycle:
    experimental: 12
    candidate: 9
    stable: 79
    deprecated: 3
```

Numbers above are illustrative; generation determines actual values.

## Build Rules

- fail on duplicate IDs;
- fail on duplicate active install names unless namespaced target paths are used;
- fail on missing files;
- derive all `has_*` fields;
- compute all statistics;
- exclude archived skills from active stats;
- include deprecated skills with status;
- sort deterministically;
- output reproducibly;
- include content digests;
- refuse to overwrite a modified generated file unless `--force` is explicitly used.

## Drift Gate

CI runs:

```text
ai-skills registry build --check
```

The command regenerates in memory and fails if the committed registry differs.

## Documentation Generation

The README badge, architecture counts, catalog tables, bundle references, and docs site reference pages consume this registry.

## Migration from Current Registry

1. Parse existing entries.
2. Scan every `SKILL.md`.
3. classify unregistered directories;
4. create manifests;
5. derive schema presence;
6. compare descriptions and paths;
7. generate v2 registry;
8. remove manually stored stats;
9. lock manual edits through a generated-file header and CI.
