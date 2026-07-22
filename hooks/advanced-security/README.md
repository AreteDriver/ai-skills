# Advanced Security Hooks

These hooks provide deeper security coverage beyond the baseline set in the parent `hooks/` directory. They are opt-in: copy only the ones you need into your personal or project `.claude/hooks/`.

## Hooks

| Hook | Event | Matcher | Purpose |
|------|-------|---------|---------|
| `audit-bash.sh` | PreToolUse | Bash | Comprehensive dangerous-command blocking (destructive ops, fork bombs, reverse shells, curl/wget pipe-to-shell, LLM client config protection) |
| `detect-secrets.py` | PreToolUse + UserPromptSubmit | Write,Edit,Bash,UserPromptSubmit | Multi-surface secret detection (17 pattern categories) with false-positive filtering |
| `validate-files.py` | PreToolUse | Write,Edit | Path-component-based write protection for system/config files |
| `session-logger.sh` | SessionStart / SessionEnd | — | Audit trail for session boundaries |
| `wrap-it-up.sh` | UserPromptSubmit | — | NL trigger for `/session-end` workflow |
| `test-marker.sh` | PostToolUse | Bash | Heuristic test-run marker for `tdd-guard.sh` companion |

## Installation

```bash
# Copy the hooks you want
cp hooks/advanced-security/audit-bash.sh ~/.claude/hooks/
cp hooks/advanced-security/detect-secrets.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh ~/.claude/hooks/*.py
```

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "command": "~/.claude/hooks/audit-bash.sh" },
      { "matcher": "Write,Edit", "command": "python3 ~/.claude/hooks/detect-secrets.py" },
      { "matcher": "Write,Edit", "command": "python3 ~/.claude/hooks/validate-files.py" }
    ],
    "PostToolUse": [
      { "matcher": "Bash", "command": "~/.claude/hooks/test-marker.sh" }
    ],
    "SessionStart": [
      { "command": "~/.claude/hooks/session-logger.sh" }
    ],
    "SessionEnd": [
      { "command": "~/.claude/hooks/session-logger.sh" }
    ],
    "UserPromptSubmit": [
      { "command": "~/.claude/hooks/detect-secrets.py" },
      { "command": "~/.claude/hooks/wrap-it-up.sh" }
    ]
  }
}
```

## Dependencies

- `bash` + `jq` (for `.sh` hooks)
- `python3` (for `.py` hooks — no external packages)

## Notes

- `detect-secrets.py` runs on three surfaces: prompts, file writes, and bash commands. It blocks only **critical** severity findings; lower severities are logged but allowed.
- `audit-bash.sh` includes LLM client config protection (added 2026-04-20 after an agent accidentally wiped `~/.claude/mcp.json`, `~/.cursor/mcp.json`, and `~/.codeium/…/mcp_config.json`).
- `test-marker.sh` is a companion to the baseline `tdd-guard.sh`. It auto-detects pass/fail from test runner output and sets/clears the marker file. Without it, `tdd-guard.sh` requires manual marker management.
- `wrap-it-up.sh` assumes your notes repo is at `~/projects/notes/` and your session-end skill is at `~/projects/ai-skills/workflows/session-end/SKILL.md`. Adjust paths for your layout.
