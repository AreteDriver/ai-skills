# Testing and Evaluation Strategy

## Core Principle

Syntax validation answers, "Can this artifact be parsed?"  
Behavioral evaluation answers, "Does this artifact improve the agent without causing unacceptable side effects?"

Both are required.

## Test Pyramid

### 1. Static Contract Tests

Validate:

- manifest schema;
- required sections by kind;
- unique IDs and names;
- path/name consistency;
- description limits;
- enums;
- references;
- dependencies;
- conflicts;
- schema presence;
- generated registry exactness;
- generated documentation freshness.

### 2. Unit Tests

For the CLI and compiler:

- manifest parsing;
- dependency resolution;
- bundle resolution;
- version constraints;
- collision handling;
- permission union;
- digest calculation;
- install manifest serialization;
- rollback logic.

### 3. Integration Tests

Use isolated temporary homes.

Cases:

- install one skill;
- install each bundle;
- bundle with hooks declined;
- bundle with hooks accepted;
- repeated install is idempotent;
- update;
- rollback;
- uninstall managed files only;
- symlink mode;
- collision;
- missing dependency;
- incompatible runtime;
- corrupted downloaded artifact.

CI matrix:

- Ubuntu current
- macOS current
- Python supported floor and latest
- Bash compatibility lane only if shell remains supported

### 4. Behavioral Evals

Each case includes:

```yaml
id: code-reviewer/sql-injection
skill: persona/engineering/code-reviewer
input_fixture: fixtures/sql-injection.py
task: Review this function.
assertions:
  must_identify:
    - SQL injection
  must_include:
    - severity
    - line reference
    - concrete remediation
  must_not:
    - execute code
    - invent unrelated findings
rubric:
  correctness: 0.40
  completeness: 0.25
  actionability: 0.20
  calibration: 0.15
threshold: 0.85
```

### 5. Adversarial Evals

Test:

- prompt injection in source files;
- requests outside skill scope;
- attempts to escalate tools;
- conflicting user instructions;
- secret-containing fixtures;
- malicious filenames;
- partial tool failures;
- repeated retry traps.

### 6. Regression and Comparative Evals

Compare:

- no skill vs skill;
- v1 vs v2;
- stable vs candidate;
- adapter A vs adapter B;
- smaller core skill vs full reference load.

## Stable Skill Quality Gate

A stable skill requires:

- contract checks: 100% pass;
- required eval cases present;
- behavioral aggregate at or above threshold;
- no safety blocker;
- no unexplained regression greater than configured tolerance;
- maintainer review;
- `last_reviewed` within policy window.

## CI Lanes

### Fast Pull Request Lane

- schema validation
- generated-artifact drift
- unit tests
- changed-skill evals
- lint and security static checks

### Full Main-Branch Lane

- all integration tests
- full behavioral suite
- adapter compatibility
- dependency audit
- docs build

### Release Lane

- clean full lane
- reproducibility check
- signed artifact generation
- install smoke test from release archive
- changelog and migration notes

## Current Validator Repairs

The existing scripts should immediately be changed so that:

- missing agent schemas fail for stable agents;
- orphan skills fail unless lifecycle is `experimental` or `archived`;
- Python warnings increment the shell warning total;
- stable CI uses `--strict` and treats warnings as failure;
- registry stats are recomputed and compared;
- `has_schema` is derived;
- README and generated docs drift fails CI;
- documented checks exactly match implemented checks.

## Metrics

Track:

- skills by lifecycle state;
- contract pass rate;
- eval pass rate;
- average quality score;
- regression count;
- stale-review count;
- installer success rate in CI;
- unresolved security waivers;
- documentation drift incidents;
- median token footprint.
