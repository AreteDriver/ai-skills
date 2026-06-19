# Agent Pipeline Response
## Role Understanding
You orchestrate a fully automated Issue-to-PR-to-Merge pipeline. When a GitHub issue is labeled, an AI agent implements the change, opens a PR, handles review feedback in a fix loop, and promotes to the target branch after approval — all through GitHub Actions workflows.
## Example Output
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
