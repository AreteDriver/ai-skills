---
name: commit
description: Create well-formatted git commits with conventional commit style. Analyzes staged changes and generates appropriate commit messages. Invoke with /commit or after completing a task.
lifecycle: experimental
---

# Commit Skill

Create clean, conventional commits from staged changes.

## Process

1. **Check state**
   ```bash
   git status --short
   git diff --cached --stat
   ```

2. **Analyze changes**
   - What files changed?
   - What's the primary change type? (feat/fix/docs/refactor/test/chore)
   - Is there a clear scope? (ui, api, core, etc.)

3. **Write commit message**
   - Format: `type(scope): short description`
   - Body: Explain "why" if not obvious
   - Keep subject under 72 chars

4. **Commit**
   ```bash
   git commit -m "$(cat <<'EOF'
   type(scope): description

   Optional body explaining why.

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <co-author>
   EOF
   )"
   ```

5. **Verify**
   ```bash
   git log --oneline -1
   ```

## Commit Types

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change (no new feature, no fix) |
| `test` | Adding/updating tests |
| `chore` | Maintenance, deps, config |
| `perf` | Performance improvement |

## Examples

```
feat(auth): add OAuth2 login flow
fix(api): handle null response from ESI
docs: update installation instructions
refactor(ui): extract button component
test(combat): add damage calculation tests
chore: bump bevy to 0.15
```

## Rules

- Never commit secrets, .env, or build artifacts
- One logical change per commit
- Run tests before committing if available
- Don't amend pushed commits without explicit request
