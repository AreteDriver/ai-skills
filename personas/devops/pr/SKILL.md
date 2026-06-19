---
name: pr
description: Pull Request Creator
lifecycle: experimental
---

# /pr - Pull Request Creator

Create well-formatted pull requests from branch commits.

## Usage
```
/pr                      # Create PR for current branch
/pr --draft              # Create as draft PR
/pr --base develop       # Target specific base branch
```

## What This Skill Does

1. **Analyze Commits** - Read all commits on branch vs base
2. **Generate Title** - From branch name or primary commit
3. **Write Description** - Summary, changes, test plan
4. **Add Labels** - Based on commit types (feat, fix, etc.)
5. **Create PR** - Using gh CLI

## PR Template

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Change 1
- Change 2
- Change 3

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing performed
- [ ] Edge cases considered

## Screenshots (if applicable)

## Related Issues
Closes #123
```

## Branch Name Conventions

| Pattern | PR Type | Label |
|---------|---------|-------|
| `feat/*` | Feature | `enhancement` |
| `fix/*` | Bug Fix | `bug` |
| `docs/*` | Documentation | `documentation` |
| `refactor/*` | Refactor | `refactor` |
| `test/*` | Tests | `tests` |

## Commands Used

```bash
# Get current branch
git branch --show-current

# Get commits not in base
git log main..HEAD --oneline

# Get changed files
git diff main..HEAD --stat

# Create PR
gh pr create --title "Title" --body "Description"

# Create draft PR
gh pr create --draft --title "Title" --body "Description"
```

## Instructions for Claude

When /pr is invoked:

1. **Get current branch** - Ensure not on main/master
2. **Find base branch** - Default to main or master
3. **Analyze commits** - Extract types, scopes, descriptions
4. **Generate title** - From branch name or summarize commits
5. **Write description** - Summary, bullet points of changes
6. **Identify related issues** - From commit messages (#123)
7. **Add test plan** - Based on what changed
8. **Create PR** - Use gh CLI with generated content
9. **Report URL** - Show the created PR link
