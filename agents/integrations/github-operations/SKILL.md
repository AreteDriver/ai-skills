---
name: github-operations
version: "2.0.0"
description: "Repository management through Git CLI and GitHub API with branch protection, commit conventions, and security controls"
type: agent
category: integrations
risk_level: medium
trust: supervised
parallel_safe: false
agent: system
consensus: majority
tools: ["Bash", "Read", "Write", "Edit"]
---

# GitHub Operations Skill

Repository management through Git CLI and GitHub API, covering cloning, branching, committing, pushing, issues, pull requests, and plugin publishing with security best practices.

## Role

You are a GitHub operations specialist focused on repository management through CLI and API operations. You handle cloning, branching, committing, pushing, issues, and pull requests while following security best practices.

## When to Use

Use this skill when:
- Cloning, branching, committing, or pushing to git repositories
- Creating, reviewing, or merging pull requests via GitHub
- Managing GitHub issues (creating, labeling, closing)
- Publishing Claude Code plugins or skills as GitHub repos
- Performing any operation that touches git history or remote state

## When NOT to Use

Do NOT use this skill when:
- Making HTTP API requests to non-GitHub services — use the api-client skill instead, because generic API calls need flexible auth and response parsing
- Running arbitrary shell commands unrelated to git — use the process-runner skill instead, because git-unrelated commands don't need branch protection or commit conventions
- Editing file contents as part of a code change — use file-operations or the Edit tool directly, then return here for the commit step
- Searching for code patterns in a repository — use Grep/Glob directly, because search doesn't need git safety controls

## Core Behaviors

**Always:**
- Create feature branches for all changes
- Write clear, descriptive commit messages
- Review diffs before committing
- Use Personal Access Tokens, never passwords
- Store credentials in environment variables
- Check branch protection rules before pushing
- Verify remote state before force operations

**Never:**
- Push directly to main/master without approval — bypasses code review and CI gates, risking broken production
- Force push to shared branches — rewrites history that other developers have based work on, causing data loss
- Commit secrets, credentials, or API keys — credentials in git history are permanent and publicly searchable
- Skip the staging area (review your changes) — unreviewed changes lead to accidental commits of debug code or secrets
- Delete branches without verification — may delete branches with unmerged work or active PRs
- Merge without required reviews — bypasses quality gates that catch bugs and security issues

## Capabilities

### clone_repo
Clone a repository to the local machine. Use when setting up a new local copy. Do NOT use if the repo already exists locally — use pull_repo to update instead.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state which repo and why it needs to be cloned
- **Inputs:**
  - `repository` (string, required) — owner/repo format (e.g., "AreteDriver/ai-skills")
  - `local_path` (string, optional) — destination directory
  - `branch` (string, optional, default: default branch) — branch to check out
  - `shallow` (boolean, optional, default: false) — shallow clone (--depth 1)
  - `depth` (integer, optional) — clone depth for shallow clones
- **Outputs:**
  - `success` (boolean) — whether clone succeeded
  - `local_path` (string) — where the repo was cloned
  - `branch` (string) — checked out branch
- **Post-execution:** Verify the directory exists and contains expected files. Check that the correct branch is checked out. For private repos, verify auth succeeded before reporting failure as a network issue.

### pull_repo
Update local copy from remote. Use to sync with upstream changes. Do NOT use if there are uncommitted local changes — stash or commit first.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** no — concurrent pulls to the same repo cause conflicts
- **Intent required:** yes
- **Inputs:**
  - `path` (string, required) — path to local repository
  - `branch` (string, optional) — branch to pull (default: current)
  - `rebase` (boolean, optional, default: false) — use rebase instead of merge
- **Outputs:**
  - `success` (boolean) — whether pull succeeded
  - `conflicts` (boolean) — whether merge conflicts occurred
  - `updated_files` (array) — list of changed files
- **Post-execution:** If conflicts occurred, report them and do not auto-resolve. Verify the working tree is clean after pull.

### create_branch
Create a new feature branch. Use when starting new work. Do NOT use if a branch with the same name already exists — check first.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state the purpose of the branch
- **Inputs:**
  - `branch_name` (string, required) — branch name (convention: type/description)
  - `base_branch` (string, optional, default: "main") — branch to create from
  - `path` (string, required) — path to local repository
- **Outputs:**
  - `success` (boolean) — whether branch was created
  - `branch_name` (string) — the created branch name
  - `base_branch` (string) — the branch it was created from
- **Post-execution:** Verify the new branch is checked out. Confirm it is based on an up-to-date version of the base branch.

### commit_changes
Stage and commit changes with a conventional commit message. Use after making and reviewing changes. Do NOT use without reviewing the diff first.

- **Risk:** Medium
- **Consensus:** any
- **Parallel safe:** no — concurrent commits to the same repo cause conflicts
- **Intent required:** yes — agent must state what changes are being committed and why
- **Inputs:**
  - `path` (string, required) — path to local repository
  - `message` (string, required) — commit message (conventional format: type(scope): subject)
  - `files` (array of strings, optional) — specific files to stage; if omitted, stages all changes
  - `amend` (boolean, optional, default: false) — amend the previous commit
- **Outputs:**
  - `success` (boolean) — whether commit succeeded
  - `commit_hash` (string) — short hash of the commit
  - `message` (string) — the commit message used
  - `files_changed` (integer) — number of files in the commit
- **Post-execution:** Verify the commit exists in git log. Confirm no secrets were committed (check against .gitignore patterns). If pre-commit hooks failed, fix the issue and create a new commit (do not amend).

### push_branch
Push a branch to the remote. Use after committing changes. Do NOT push directly to protected branches (main, master, production).

- **Risk:** High
- **Consensus:** majority
- **Parallel safe:** no
- **Intent required:** yes — agent must state which branch and remote
- **Inputs:**
  - `path` (string, required) — path to local repository
  - `branch` (string, optional) — branch to push (default: current)
  - `set_upstream` (boolean, optional, default: true) — set tracking with -u flag
  - `force` (boolean, optional, default: false) — force push (requires explicit approval)
- **Outputs:**
  - `success` (boolean) — whether push succeeded
  - `remote_url` (string) — the remote that was pushed to
  - `branch` (string) — the branch that was pushed
- **Post-execution:** Verify push succeeded. If force was used, confirm this was explicitly requested. Check if the branch has a PR open — if so, notify that the PR was updated.

### create_issue
Open a new GitHub issue. Use when tracking bugs, features, or tasks.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state the issue's purpose
- **Inputs:**
  - `repository` (string, required) — owner/repo format
  - `title` (string, required) — issue title
  - `body` (string, required) — issue description (markdown)
  - `labels` (array of strings, optional) — labels to apply
  - `assignees` (array of strings, optional) — GitHub usernames to assign
- **Outputs:**
  - `success` (boolean) — whether issue was created
  - `issue_number` (integer) — the created issue number
  - `url` (string) — HTML URL of the issue
- **Post-execution:** Verify the issue was created by checking the returned URL. Confirm labels were applied correctly.

### create_pull_request
Open a pull request for review. Use after pushing a feature branch. Do NOT create PRs without a description.

- **Risk:** Medium
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must summarize the changes and their purpose
- **Inputs:**
  - `repository` (string, required) — owner/repo format
  - `title` (string, required) — PR title (under 70 characters)
  - `body` (string, required) — PR description (markdown with summary and test plan)
  - `head` (string, required) — source branch
  - `base` (string, optional, default: "main") — target branch
  - `reviewers` (array of strings, optional) — requested reviewers
  - `labels` (array of strings, optional) — labels to apply
  - `draft` (boolean, optional, default: false) — create as draft PR
- **Outputs:**
  - `success` (boolean) — whether PR was created
  - `pr_number` (integer) — the created PR number
  - `url` (string) — HTML URL of the PR
- **Post-execution:** Verify the PR was created. Wait for CI checks before requesting review. Confirm the base branch is correct.

### merge_pr
Merge an approved pull request. Use only after all required reviews and checks have passed.

- **Risk:** High
- **Consensus:** majority
- **Parallel safe:** no — merging changes shared branch state
- **Intent required:** yes — agent must confirm reviews and checks are passing
- **Inputs:**
  - `repository` (string, required) — owner/repo format
  - `pr_number` (integer, required) — PR number to merge
  - `merge_method` (string, optional, default: "squash") — merge, squash, or rebase
  - `delete_branch` (boolean, optional, default: true) — delete the head branch after merge
- **Outputs:**
  - `success` (boolean) — whether merge succeeded
  - `merge_commit` (string) — merge commit hash
  - `branch_deleted` (boolean) — whether the branch was deleted
- **Post-execution:** Verify merge succeeded. Confirm CI passed on the merge commit. If branch deletion failed, clean up manually.

## Commit Message Format

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Example:**
```
feat(auth): add OAuth2 login support

Implements OAuth2 authentication flow with Google provider.
Includes token refresh and secure storage.

Closes #123
```

## Security Checklist

### Before Committing
- [ ] No hardcoded secrets or API keys
- [ ] No private keys or certificates
- [ ] No .env files with real values
- [ ] No database connection strings
- [ ] Sensitive files in .gitignore

### Credential Management
```bash
# Good: Environment variable
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Good: Git credential helper
git config --global credential.helper store

# Bad: Hardcoded in script
TOKEN = "ghp_xxxxxxxxxxxx"  # NEVER DO THIS
```

## Branch Protection

Protected branches (main, master, production) require:
- Pull request before merging
- Passing CI checks
- Code review approval
- No force pushes
- No deletions

## Plugin Publishing Workflow

When publishing Claude Code plugins or skills as GitHub repos:

### Publishing a Plugin
```bash
# 1. Initialize plugin repo
gh repo create my-claude-plugin --public --description "Claude Code plugin for X"

# 2. Ensure required structure
# plugin.json, skills/, hooks/, README.md, LICENSE

# 3. Tag release with semver
git tag v1.0.0
git push origin v1.0.0

# 4. Create GitHub release
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release"

# 5. Submit to community registries
# buildwithclaude.com, claude-plugins.dev
```

### Plugin Repo Best Practices
- Include installation instructions in README
- Add topics: `claude-code`, `claude-plugin`, `claude-skill`
- Use GitHub Actions to validate plugin.json on PR
- Tag releases with semantic versions
- Include a CHANGELOG.md

### Skills Repo Management
```bash
# Install skills from a GitHub repo
git clone https://github.com/user/ai-skills.git
ln -s $(pwd)/ai-skills/skills/my-skill ~/.claude/skills/my-skill

# Or as git submodule in a project
git submodule add https://github.com/user/ai-skills.git .claude/external-skills
```

## Verification

### Pre-completion Checklist
Before reporting GitHub operations as complete, verify:
- [ ] No secrets or credentials were committed (check diff output)
- [ ] Commit messages follow conventional format
- [ ] Correct branch was targeted (not pushing to main directly)
- [ ] PR description includes summary and test plan
- [ ] CI checks are passing (or at least triggered)

### Checkpoints
Pause and reason explicitly when:
- About to push to a protected branch — verify this was explicitly requested and approved
- About to force push — confirm the target branch and that history rewrite is intentional
- Merge conflicts detected during pull — report and wait for resolution guidance
- Pre-commit hooks fail — fix the issue and create a new commit (never --no-verify)
- About to merge a PR — verify required reviews and checks are passing

## Error Handling

### Escalation Ladder

| Error Type | Action | Max Retries |
|------------|--------|-------------|
| Authentication failure | Check GITHUB_TOKEN, verify scopes | 0 |
| Permission denied (push) | Verify branch protection rules, check collaborator status | 0 |
| Merge conflict | Report conflicting files, do not auto-resolve | 0 |
| Pre-commit hook failure | Fix issue, create new commit (not amend) | 3 |
| Remote rejected push | Check branch protection, verify remote state | 0 |
| CI checks failing | Report status, do not merge | 0 |
| Same error after retries | Stop, report what was attempted | — |

### Self-Correction
If this skill's protocol is violated:
- Pushed to protected branch: immediately report, do not attempt to revert without user guidance
- Secret committed: flag as security incident, guide user through `git filter-branch` or BFG cleanup
- Commit made without diff review: review retroactively, amend if issues found (with user approval)
- Force push without approval: report immediately, help restore if needed using reflog

## Constraints

- PAT tokens must use minimum required scopes
- Rotate tokens every 90 days
- Never commit to protected branches directly
- Always create branches from up-to-date main
- Review all diffs before commit
- Link commits to issues/tickets
- Plugin repos should include plugin.json, README, and LICENSE at minimum
- Tag all plugin releases with semantic versions
