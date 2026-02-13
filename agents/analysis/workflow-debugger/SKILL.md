---
name: workflow-debugger
description: Diagnoses why Gorgon workflows fail. Reads checkpoint state, agent logs, budget traces, and output contracts to produce root-cause analysis. The technical-debt-auditor inspects repos; this skill inspects workflow runs. Use when a Gorgon pipeline fails, produces bad output, exceeds budget, or hangs. Also useful for post-mortem analysis of completed workflows to find optimization opportunities.
---

# Workflow Debugger

When a Gorgon workflow fails at step 4 of 7, this skill figures out why and
what to do about it. Think of it as the technical-debt-auditor for workflow
runs instead of repositories.

## When to Activate

- "Why did this workflow fail?"
- "The builder agent produced garbage output"
- "This workflow ran out of budget at step 3"
- "The pipeline hung and never completed"
- "Debug the last run"
- Post-mortem analysis after any workflow execution

## Failure Taxonomy

Workflows fail for a finite set of reasons. Knowing which category you're in
determines the fix.

| Category | Symptoms | Root Cause | Fix |
|----------|----------|-----------|-----|
| **Contract Violation** | Agent output doesn't match expected schema | Prompt ambiguity, missing output spec | Tighten agent instructions, add validation |
| **Budget Exhaustion** | Agent hits token limit mid-response | Task too large for budget, or agent is rambling | Increase budget or decompose task |
| **Timeout** | Agent doesn't complete in allotted time | Task too complex, or infinite loop in tool use | Increase timeout or simplify task |
| **Dependency Failure** | Upstream agent output missing or malformed | Previous agent failed silently | Add output validation between stages |
| **Context Overflow** | Agent loses track of instructions in long context | Too much injected context, or conversation too long | Compress context, split workflow |
| **Hallucination** | Agent fabricates files, APIs, or capabilities | Insufficient grounding in context map | Better context mapping, add verification |
| **Checkpoint Corruption** | Resume from checkpoint produces different results | State not fully captured at checkpoint | Review checkpoint serialization |
| **External Failure** | API rate limit, Docker timeout, network error | Infrastructure, not workflow logic | Retry with backoff, or fix infrastructure |

## Diagnostic Procedure

### Step 1: Locate the Failure Point

```bash
# Read Gorgon checkpoint database
sqlite3 .gorgon/checkpoints.db "
  SELECT agent_role, status, started_at, completed_at, error_message
  FROM checkpoints
  WHERE workflow_run_id = '{run_id}'
  ORDER BY started_at
"
```

Expected output:
```
scanner     | completed | 2026-02-12 10:00:01 | 2026-02-12 10:00:45 | NULL
executor    | completed | 2026-02-12 10:00:46 | 2026-02-12 10:02:12 | NULL
analyzer    | failed    | 2026-02-12 10:02:13 | 2026-02-12 10:02:58 | "KeyError: 'execution_results'"
reporter    | skipped   | NULL                 | NULL                 | "dependency failed"
```

→ Failure at **analyzer**, caused by missing key in executor output.

### Step 2: Examine Agent Outputs

```bash
# Check the output that broke things
cat .gorgon/runs/{run_id}/executor/execution-results.json | python3 -m json.tool

# Compare against expected schema
# Does execution-results.json have the keys the analyzer expects?
```

### Step 3: Check Budget Consumption

```bash
sqlite3 .gorgon/checkpoints.db "
  SELECT agent_role, tokens_used, token_budget, 
         ROUND(tokens_used * 100.0 / token_budget, 1) as pct_used
  FROM budget_log
  WHERE workflow_run_id = '{run_id}'
"
```

```
scanner     | 823  | 1500 | 54.9%
executor    | 412  | 500  | 82.4%   ← Running hot
analyzer    | 1987 | 2000 | 99.4%   ← Budget exhaustion likely
```

### Step 4: Read Agent Logs

```bash
# Structured JSON logs per agent
cat .gorgon/runs/{run_id}/analyzer/agent.log | \
  python3 -c "import sys,json; [print(json.dumps(json.loads(l), indent=2)) for l in sys.stdin]" | \
  head -100
```

Look for:
- Repeated tool calls (looping)
- "I don't have enough context" messages
- Truncated outputs (hit token limit)
- Unexpected tool errors

### Step 5: Classify and Report

Produce a diagnostic report:

```
WORKFLOW DEBUG REPORT
═════════════════════

Workflow:  technical_debt_audit
Run ID:    run_2026-02-12_001
Status:    FAILED at analyzer (step 3 of 5)
Duration:  2m 57s (of 10m budget)

ROOT CAUSE: Contract Violation
  The executor agent produced execution-results.json without the
  'tests' key because Docker was not available on the host. The
  executor's on_failure:continue policy meant it returned a partial
  result, but the analyzer expected a complete schema.

EVIDENCE:
  1. executor output missing 'tests' key (expected by analyzer)
  2. executor log shows: "Docker not found, skipping runtime checks"
  3. analyzer crashes at: analysis.py line 42, KeyError('tests')

FIX OPTIONS:
  1. [Quick] Make analyzer handle missing executor fields gracefully
     Effort: 15 min | Prevents: this exact failure
  2. [Proper] Add output schema validation between stages
     Effort: 1 hour | Prevents: all contract violations
  3. [Infrastructure] Install Docker on host
     Effort: 5 min | Prevents: executor partial results

BUDGET ANALYSIS:
  Total spent: 3,222 / 5,500 tokens (58.6%)
  Waste: ~1,987 tokens on analyzer that crashed
  If fixed: run would cost ~4,500 tokens

RECOMMENDATION: Fix #2 (schema validation) — it's a systemic fix
  that prevents an entire category of failures.
```

## Post-Mortem Mode

For completed (successful) workflows, analyze efficiency:

```
WORKFLOW POST-MORTEM
════════════════════

Workflow:  document_analysis
Status:    COMPLETED (all 5 stages)
Duration:  4m 12s
Budget:    4,800 / 6,000 tokens (80%)

STAGE BREAKDOWN:
  context_mapper  | 0:32 |  800 tokens | ✅ Clean
  scanner         | 1:05 | 1,200 tokens | ⚠️ Scanned 3 languages, only Python present
  executor        | 1:45 |   400 tokens | ✅ Clean
  analyzer        | 0:35 | 1,800 tokens | ⚠️ 60% of budget on scoring justifications
  reporter        | 0:15 |   600 tokens | ✅ Clean

OPTIMIZATION OPPORTUNITIES:
  1. Scanner: Skip language detection for non-present languages → save ~300 tokens
  2. Analyzer: Shorten justifications (not user-facing) → save ~600 tokens
  3. Context mapper cache hit possible for repeated runs → save 800 tokens

POTENTIAL SAVINGS: ~1,700 tokens (35% reduction)
```

## Gorgon Integration

The workflow debugger itself can be a Gorgon agent:

```yaml
# Add to any workflow as an error handler
workflow:
  error_handler:
    role: workflow_debugger
    agent_ref: skills/workflow-debugger/SKILL.md
    trigger: "any agent fails"
    inputs:
      run_id: "{{ workflow.run_id }}"
      checkpoint_db: "{{ workflow.checkpoint_path }}"
      agent_logs: "{{ workflow.log_path }}"
    output: debug-report.md
```

## Constraints

- **Read-only** — never modifies workflow state, checkpoints, or outputs
- **Non-blocking** — debugger runs after failure, doesn't interfere with retry logic
- **Evidence-based** — every diagnosis must reference specific log lines or data
- **Actionable** — every report includes concrete fix options with effort estimates
- **No guessing** — if root cause is uncertain, say so and list possibilities ranked by likelihood
