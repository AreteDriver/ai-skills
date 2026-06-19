# Prioritized Backlog

## P0 — Release Blocking

| ID | Work Item | Acceptance |
|---|---|---|
| AIS-P0-001 | Full skill inventory and orphan reconciliation | Every `SKILL.md` is registered, experimental, deprecated, or archived |
| AIS-P0-002 | Correct registry stats | Generated counts match entries |
| AIS-P0-003 | Installer consumes `bundles.yaml` | No bundle names or contents hard-coded |
| AIS-P0-004 | Fix advertised bundles | Every README example succeeds in integration tests |
| AIS-P0-005 | Normalize risk and approval model | One schema and migration map |
| AIS-P0-006 | Add missing agent/workflow templates | Contributor commands reference existing files |
| AIS-P0-007 | Strict CI | Stable lane fails on orphan, missing schema, drift, or warning |
| AIS-P0-008 | Generate README inventory | Badge and tables derive from registry |
| AIS-P0-009 | Fix schema flags | `has_schema` and related metadata derived |
| AIS-P0-010 | Add safe uninstall ownership | Unknown files can never be deleted |

## P1 — Reliability and Safety

| ID | Work Item | Acceptance |
|---|---|---|
| AIS-P1-001 | Python CLI | Feature parity plus dry-run, doctor, verify |
| AIS-P1-002 | Atomic install and rollback | Failure leaves prior installation valid |
| AIS-P1-003 | Hook consent and review | Hooks absent without explicit approval |
| AIS-P1-004 | Installer integration tests | All bundles tested in temp HOME |
| AIS-P1-005 | Skill Contract v2 | All candidate/stable skills migrated |
| AIS-P1-006 | Eval runner | Executable deterministic and model-graded cases |
| AIS-P1-007 | Stable skill eval minimum | Required suites enforced |
| AIS-P1-008 | Prompt-injection suite | Untrusted-content cases pass |
| AIS-P1-009 | Changelog automation | Every release includes all merged fragments |
| AIS-P1-010 | Governance files | Contribution and security process documented |

## P2 — Product Maturity

| ID | Work Item | Acceptance |
|---|---|---|
| AIS-P2-001 | Generated documentation site | Searchable catalog with health cards |
| AIS-P2-002 | Capability graph | Dependencies, alternatives, conflicts queryable |
| AIS-P2-003 | Runtime adapters | Core-neutral contract with tested adapters |
| AIS-P2-004 | Project lockfile | Repeatable per-project installation |
| AIS-P2-005 | Semantic skill diff | Breaking contract changes detected |
| AIS-P2-006 | Stable/candidate channels | Installer can select release channel |
| AIS-P2-007 | Token footprint metrics | Catalog shows load cost |
| AIS-P2-008 | Team profile bundles | Organization policy overlay supported |

## P3 — Expansion

| ID | Work Item |
|---|---|
| AIS-P3-001 | Private registry support |
| AIS-P3-002 | Signed third-party publisher model |
| AIS-P3-003 | Local opt-in effectiveness feedback |
| AIS-P3-004 | Bundle recommendation engine |
| AIS-P3-005 | Visual catalog and dependency explorer |
