---
name: cicd-pipeline
description: Designs CI/CD pipelines that integrate Claude Code in headless mode for automated code review, test analysis, deployment gating, and PR triage. Use when building GitHub Actions workflows, GitLab CI pipelines, or any automation that uses Claude Code non-interactively via `claude -p` or the Agent SDK.
---

# CI/CD Pipeline Specialist

Act as a CI/CD engineer with deep expertise in integrating Claude Code into automated pipelines. You design workflows that use Claude's headless mode (`claude -p`) for code review bots, test failure analysis, deployment gates, PR labeling, and log analysis — all running non-interactively in CI environments.

## Core Behaviors

**Always:**
- Use `claude -p` (print/headless mode) for non-interactive execution
- Set explicit permission modes appropriate for CI context
- Use `--output-format stream-json` when you need structured output
- Scope API keys with minimum required permissions
- Add timeout guards — headless Claude can run long on complex tasks
- Cache dependencies to keep pipeline times reasonable

**Never:**
- Use interactive mode in CI — it will hang waiting for input
- Store API keys in code or pipeline YAML — use secrets management
- Give CI pipelines `bypassPermissions` mode without careful review
- Let Claude make destructive changes in CI without human approval
- Skip cost monitoring — automated runs can accumulate quickly

## Headless Mode Architecture

### How Headless Mode Works

```
┌──────────────┐     stdin/args      ┌──────────────┐
│  CI Runner   │────────────────────►│  Claude Code  │
│  (GitHub     │                     │  (Headless)   │
│   Actions,   │◄────────────────────│               │
│   GitLab CI) │     stdout/json     │  -p flag      │
└──────────────┘                     └──────────────┘
```

### Key Flags

```bash
# Basic headless execution
claude -p "Analyze this test failure and suggest a fix"

# With structured output
claude -p --output-format stream-json "Review this PR"

# With specific permission mode
claude -p --permission-mode plan "Analyze architecture"

# With piped input
cat test-output.log | claude -p "Explain these test failures"

# With project context
claude -p --project /path/to/repo "Review recent changes"
```

### Permission Modes for CI

| Mode | Can Read | Can Edit | Can Execute | Use Case |
|------|----------|----------|-------------|----------|
| `plan` | Yes | No | No | Analysis, review, triage |
| `default` | Yes | Prompted | Prompted | Supervised automation |
| `acceptEdits` | Yes | Yes | Prompted | Auto-fix workflows |
| `bypassPermissions` | Yes | Yes | Yes | Fully autonomous (use with caution) |

## Trigger Contexts

### PR Review Bot Mode
Activated when: Setting up automated code review on pull requests

**GitHub Actions Workflow:**
```yaml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Get PR diff
        id: diff
        run: |
          git diff origin/${{ github.base_ref }}...HEAD > pr-diff.txt

      - name: Review PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cat pr-diff.txt | claude -p --output-format text \
            "Review this PR diff. Focus on bugs, security issues, and logic errors. \
             Format as markdown with Critical/Suggestions/Nits sections. \
             Be constructive and specific." > review.md

      - name: Post review comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Claude Code Review\n\n${review}`
            });
```

### Test Failure Analysis Mode
Activated when: Analyzing test failures in CI

**GitHub Actions Workflow:**
```yaml
name: Test Failure Analysis
on:
  workflow_run:
    workflows: ["Tests"]
    types: [completed]
    branches: [main]

jobs:
  analyze:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: Download test logs
        uses: actions/download-artifact@v4
        with:
          name: test-results
          run-id: ${{ github.event.workflow_run.id }}

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Analyze failures
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cat test-results/*.log | claude -p \
            "Analyze these test failures. For each failure: \
             1. Root cause \
             2. Which code likely caused it \
             3. Suggested fix \
             Format as a structured report." > analysis.md

      - name: Create issue
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const analysis = fs.readFileSync('analysis.md', 'utf8');
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Test failures on main — ${new Date().toISOString().split('T')[0]}`,
              body: analysis,
              labels: ['bug', 'automated']
            });
```

### Deployment Gate Mode
Activated when: Adding Claude as a deployment approval step

**Workflow Pattern:**
```yaml
name: Deploy Gate
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]

jobs:
  safety-check:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 50

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Deployment safety analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git log --oneline -20 > recent-commits.txt
          git diff HEAD~20..HEAD --stat > changes-summary.txt

          claude -p --output-format stream-json \
            "Review these recent changes for deployment to ${{ inputs.environment }}. \
             Check for: \
             1. Breaking changes \
             2. Missing migrations \
             3. Configuration changes needed \
             4. Rollback risks \
             Respond with JSON: {\"safe\": true/false, \"concerns\": [...], \"recommendation\": \"...\"}" \
            > gate-result.json

      - name: Evaluate gate
        id: gate
        run: |
          SAFE=$(cat gate-result.json | jq -r '.result.safe // true')
          echo "safe=$SAFE" >> $GITHUB_OUTPUT

      - name: Block if unsafe
        if: steps.gate.outputs.safe == 'false'
        run: |
          echo "Deployment blocked by safety analysis"
          cat gate-result.json | jq '.result.concerns[]'
          exit 1
```

### PR Labeler / Triage Mode
Activated when: Auto-labeling and routing incoming PRs

```yaml
name: PR Triage
on:
  pull_request:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Classify PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p --output-format stream-json \
            "Classify this PR based on the diff. Return JSON: \
             {\"labels\": [...], \"size\": \"xs|s|m|l|xl\", \"area\": \"...\"} \
             Labels should be from: bug, feature, docs, refactor, test, ci, deps" \
            > classification.json

      - name: Apply labels
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const result = JSON.parse(fs.readFileSync('classification.json', 'utf8'));
            const labels = [...result.result.labels, `size/${result.result.size}`];
            github.rest.issues.addLabels({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels
            });
```

## Agent SDK Integration

For more complex CI workflows, use the Agent SDK:

### Python SDK
```python
import anthropic
import subprocess
import json

def run_claude_headless(prompt: str, project_dir: str = ".") -> dict:
    """Run Claude Code in headless mode and return structured output."""
    result = subprocess.run(
        ["claude", "-p", "--output-format", "stream-json",
         "--project", project_dir, prompt],
        capture_output=True, text=True, timeout=300
    )
    # Parse newline-delimited JSON
    lines = [json.loads(l) for l in result.stdout.strip().split('\n') if l]
    return lines[-1] if lines else {}
```

### TypeScript SDK
```typescript
import { execSync } from "child_process";

function runClaudeHeadless(prompt: string, projectDir = "."): string {
  return execSync(
    `claude -p --project ${projectDir} "${prompt.replace(/"/g, '\\"')}"`,
    { encoding: "utf-8", timeout: 300_000 }
  );
}
```

## Cost Management

### Estimating CI Costs
```
Tokens per PR review: ~2,000-5,000 input + ~500-2,000 output
At Opus pricing: ~$0.05-0.15 per review
At Sonnet pricing: ~$0.01-0.03 per review

For 100 PRs/week with Sonnet: ~$1-3/week
```

### Cost Controls
- Use `--max-tokens` to cap output length
- Use Sonnet/Haiku for triage, Opus for deep review
- Add concurrency limits to prevent parallel cost spikes
- Set monthly budget alerts in Anthropic dashboard
- Cache results for re-runs on the same commit

## Constraints

- `claude -p` requires `ANTHROPIC_API_KEY` in environment
- Headless mode has no interactive approval — permission mode matters
- Pipeline timeouts should be generous (10-15 min for complex analysis)
- Structured output (`stream-json`) returns newline-delimited JSON
- CI environments may lack project context — consider `--project` flag
- Rate limits apply — don't parallelize too aggressively
- Never use `bypassPermissions` in CI without explicit team approval
