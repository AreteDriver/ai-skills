---
name: agent-pipeline
version: "1.0.0"
lifecycle: experimental
description: "Automated Issue-to-PR-to-Merge pipeline using GitHub Actions and AI agents with review loops"
metadata: {"openclaw": {"emoji": "🔄", "os": ["darwin", "linux", "win32"]}}
type: workflow
category: automation
risk_level: medium
---

# Agent Pipeline Workflow

## Role

You orchestrate a fully automated Issue-to-PR-to-Merge pipeline. When a GitHub issue is labeled, an AI agent implements the change, opens a PR, handles review feedback in a fix loop, and promotes to the target branch after approval — all through GitHub Actions workflows.

## Why This Exists

Manual implementation of well-specified issues is a bottleneck. If the issue has clear acceptance criteria, an AI agent can implement, iterate on review feedback, and merge — reducing human involvement to writing the issue and reviewing the PR. Total human time: writing the issue + one review pass.

## When to Use

Use this workflow when:
- Setting up automated agent implementation in a GitHub repository
- Configuring the Issue → PR → Review → Merge pipeline
- Adding CI/CD automation where AI agents handle implementation from issues
- Repos with well-defined issue templates and coding conventions (CLAUDE.md)

## When NOT to Use

Do NOT use this workflow when:
- The repository has no tests or CI — because the pipeline depends on test gates to validate agent output
- Issues are vague or lack acceptance criteria — because agents need specific requirements to produce useful implementations
- The codebase has no CLAUDE.md or coding conventions — because agents need context to follow project patterns
- Security-critical changes that require human implementation — because agent-generated code for auth/crypto/secrets needs human authorship

## Pipeline Flow

```
Issue labeled "agent"
       ↓
1-implement.yml: Agent reads issue + CLAUDE.md + agent_context
       ↓
Agent implements → opens PR to target_branch
       ↓
2-fix-review.yml: Reviewer runs (CodeRabbit, human, or any)
       ↓
Changes requested? → Agent reads comments → fixes → pushes
       ↓                    (up to max_review_iterations)
Approved → 3-merge-develop.yml: squash-merge to target_branch
       ↓
4-test-promote.yml: Build + test → promotion PR to production_branch
```

## Configuration

Create `.github/agent-pipeline.yml` in the target repository:

```yaml
agent: claude                  # or "codex"
trigger_label: agent           # label that triggers the pipeline
target_branch: develop         # agent PRs go here
production_branch: main        # promotion target
max_review_iterations: 3       # max fix cycles before human escalation
agent_timeout: 30              # minutes per agent run

test:
  build: npm run build         # or: python -m pytest, cargo test, etc.
  unit: npm test -- --run
  e2e: npx playwright test     # optional

skip_promotion: false          # true for single-branch repos
auto_promote: false            # true to skip manual promotion PR review

agent_context: |
  Follow CLAUDE.md for all conventions.
  [Project-specific constraints here]
```

### Single-Branch Repos
```yaml
target_branch: main
skip_promotion: true
```

## Workflow Files

| File | Trigger | What It Does |
|------|---------|--------------|
| `1-implement.yml` | Issue labeled with `trigger_label` | Agent implements, opens PR |
| `2-fix-review.yml` | PR review requests changes | Agent fixes feedback, pushes |
| `3-merge-develop.yml` | PR review approved + checks pass | Squash-merge to target branch |
| `4-test-promote.yml` | Push to target branch | Build, test, create promotion PR |

## Safety Guardrails

| Guardrail | Mechanism |
|-----------|-----------|
| Opt-in only | Issue must have trigger label — won't fire on random issues |
| Iteration cap | Max N review fix cycles, then labels `needs-human-review` |
| Concurrency | One agent run per issue/PR at a time |
| Timeouts | Hard cap per agent run (default 30 min) |
| No direct push | All changes go through PRs, never direct to branch |
| Human escape hatch | Remove label OR add `needs-human-review` to stop |
| Audit trail | Comments on issue + PR at every pipeline step |

### Stopping the Pipeline
- Remove the `agent-pr` label from the PR
- Add `needs-human-review` label
- Close the PR
- Cancel the workflow in the Actions tab

## Required Secrets

| Secret | Purpose |
|--------|---------|
| `ANTHROPIC_API_KEY` | For Claude agent (required if agent: claude) |
| `OPENAI_API_KEY` | For Codex agent (required if agent: codex) |

## Required Repo Settings

- Enable "Allow auto-merge" in Settings → General
- Branch protection on target and production branches recommended
- **Org-level**: Settings → Actions → General → "Allow GitHub Actions to create and approve pull requests" (org setting overrides repo)
- **Repo-level**: Same setting under repo Settings → Actions → General

## Known Gotchas (Battle-Tested)

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing `id-token: write` | `is_error: true`, `total_cost_usd: 0`, `duration_ms: ~160` | Add `id-token: write` to job permissions |
| Git auth after claude-code-action | Push fails with "Invalid username or token" | Re-set remote URL with `GITHUB_TOKEN` before push step |
| Agent doesn't commit | "No commits between main and branch" | Add explicit commit instructions in prompt + `git config user.name/email` |
| Agent modifies workflow files | Push rejected — "refusing to allow...without workflows permission" | Add "Do NOT modify .github/workflows/" to prompt |
| Tool permission denials | `permission_denials_count > 0`, no file changes | Use `claude_args: "--allowedTools Bash Read Write Edit Glob Grep"` |
| GitHub throttles label toggles | No new workflow run after re-labeling | Add `workflow_dispatch` trigger as fallback, use `gh workflow run` |
| `workflows: write` in YAML | Workflow fails to parse | Not a valid job-level permission — protect via instructions instead |
| PR creation blocked | "GitHub Actions is not permitted to create or approve pull requests" | Enable at **org level**, not just repo level |
| Stale branch from prior run | Push fails — branch already exists | Add cleanup step: `git push origin --delete "$BRANCH" 2>/dev/null \|\| true` |

## agent_context Best Practices

The `agent_context` field is injected into every agent run. Put your most critical constraints here:

```yaml
agent_context: |
  - Never modify pricing constants in src/config/pricing.js
  - All new API routes must have rate limiting middleware
  - Test coverage must stay above 80%
  - Follow the scoring output contract defined in SCORING.md
  - Use conventional commits: feat:, fix:, docs:, refactor:
```

This prevents agents from making well-intentioned but destructive changes.

## Setup Checklist

When setting up agent-pipeline in a new repo:

- [ ] Repository has CI (tests, lint) that runs on PRs
- [ ] `CLAUDE.md` exists with project conventions
- [ ] `.github/agent-pipeline.yml` config created
- [ ] 4 workflow files copied to `.github/workflows/`
- [ ] Required secrets configured in repo settings
- [ ] "Allow auto-merge" enabled
- [ ] Trigger label created (default: `agent`)
- [ ] Branch protection configured on target branches
- [ ] Test issue created and labeled to verify pipeline

## Implementation Priority (AreteDriver)

| Repo | Config Notes |
|------|-------------|
| BenchGoblins | `target_branch: main`, `skip_promotion: true`, active dev |
| Animus | `target_branch: develop`, `production_branch: main`, monorepo |
| Dossier | Portfolio piece, lower velocity |
| arete-guard | Conservative: `max_review_iterations: 1`, human review required |

## Constraints

- Pipeline is reviewer-agnostic — works with CodeRabbit, human reviews, or any tool that uses standard GitHub review events
- Pipeline is agent-agnostic — switch between Claude and Codex with one config line
- All agent output goes through PRs — never direct to branch
- Agent runs are time-boxed — no runaway processes
- The pipeline stops after max iterations — always has a human escape hatch
- Issues must have acceptance criteria for agent implementation to be useful

## Error Handling

| Failure | Response |
|---------|----------|
| Agent fails to implement | Comment on issue with error, label `needs-human-review` |
| Agent exceeds timeout | Kill run, comment with partial progress |
| Review iterations exhausted | Label `needs-human-review`, stop auto-fixing |
| Tests fail after merge | Promotion PR blocked, notify via PR comment |
| Config missing | Workflow fails fast with clear error message |

## Source

Derived from TheCraigHewitt/agent-pipeline (MIT License). Adapted for AreteDriver repository conventions.
