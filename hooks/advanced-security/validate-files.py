#!/usr/bin/env python3
"""
Security Hook: Validate file changes against security policies.
Blocks modifications to critical system and configuration files.

This hook runs on PreToolUse for Write/Edit operations.
"""
import json
import sys
import os
from datetime import datetime, timezone

# Audit log location
AUDIT_LOG = os.path.expanduser("~/.claude/audit-log.txt")

# Files/directories that should NEVER be modified
PROTECTED_PATHS = [
    # Git internals
    '.git/config',
    '.git/hooks/',
    '.gitconfig',

    # Environment and secrets
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    'secrets/',
    'credentials/',
    '.secrets',

    # SSH and security
    '.ssh/',
    '.gnupg/',
    '.gpg/',

    # System files
    '/etc/',
    '/root/',
    '/usr/',
    '/bin/',
    '/sbin/',

    # Cloud credentials
    '.aws/credentials',
    '.aws/config',
    '.azure/',
    '.kube/config',
    '.docker/config.json',
]

# Files that need extra scrutiny (warn but allow)
SENSITIVE_PATHS = [
    'package-lock.json',
    'yarn.lock',
    'Cargo.lock',
    'poetry.lock',
    'Pipfile.lock',
    'Gemfile.lock',
    'composer.lock',
    '.npmrc',
    '.yarnrc',
    'requirements.txt',
    'setup.py',
    'pyproject.toml',
]


def log_audit(event_type: str, message: str, severity: str = "info"):
    """Write to audit log."""
    try:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(AUDIT_LOG, 'a') as f:
            f.write(f"[{timestamp}] [{severity.upper()}] {event_type}: {message}\n")
    except Exception:
        pass


def normalize_path(file_path: str) -> str:
    """Normalize a file path for comparison."""
    # Expand user home directory
    expanded = os.path.expanduser(file_path)
    # Normalize the path
    normalized = os.path.normpath(expanded)
    return normalized


def is_protected(file_path: str) -> tuple[bool, str]:
    """Check if file path is protected. Returns (is_protected, reason).

    Tightened 2026-04-19: directory patterns now match path components,
    not substrings. Previously `secrets/` would flag any filename containing
    "secrets" (e.g. detect-secrets.py).
    """
    normalized = normalize_path(file_path)
    components = normalized.split(os.sep)

    for protected in PROTECTED_PATHS:
        # Handle directory patterns (ending with /)
        if protected.endswith('/'):
            check_path = protected.rstrip('/')
            # Match only as a full path component, not substring
            if check_path in components:
                return True, f"Protected directory: {protected}"
            # Also check if path starts with ~/<dir>
            home_path = os.path.expanduser(f'~/{check_path}')
            if normalized == home_path or normalized.startswith(home_path + os.sep):
                return True, f"Protected directory: {protected}"
        else:
            # Exact file match or path contains the protected pattern
            if normalized.endswith(protected) or f'{os.sep}{protected}' in normalized:
                return True, f"Protected file: {protected}"
            # Check home directory paths
            home_path = os.path.expanduser(f'~/{protected}')
            if normalized == home_path or normalized.startswith(home_path + os.sep):
                return True, f"Protected path: {protected}"

    return False, ""


def is_sensitive(file_path: str) -> tuple[bool, str]:
    """Check if file path is sensitive (warn but allow)."""
    normalized = normalize_path(file_path)

    for sensitive in SENSITIVE_PATHS:
        if normalized.endswith(sensitive):
            return True, f"Sensitive file: {sensitive}"

    return False, ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log_audit("HOOK_ERROR", f"Failed to parse input: {e}", "error")
        sys.exit(1)

    hook_event = input_data.get('hook_event_name', '')

    if hook_event != 'PreToolUse':
        sys.exit(0)

    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Only check Write and Edit operations
    if tool_name not in ['Write', 'Edit']:
        sys.exit(0)

    file_path = tool_input.get('file_path', '')

    if not file_path:
        sys.exit(0)

    # Check if protected
    protected, reason = is_protected(file_path)
    if protected:
        log_audit("BLOCKED_WRITE", f"Blocked write to protected file: {file_path} ({reason})", "warning")
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Security policy violation: {reason}. This file is protected and cannot be modified."
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Check if sensitive (log but allow)
    sensitive, reason = is_sensitive(file_path)
    if sensitive:
        log_audit("SENSITIVE_WRITE", f"Write to sensitive file: {file_path} ({reason})", "info")

    # Allow the operation
    sys.exit(0)


if __name__ == '__main__':
    main()
