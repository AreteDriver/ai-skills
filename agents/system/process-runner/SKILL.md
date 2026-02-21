---
name: process-runner
version: "2.0.0"
description: "Execute and manage subprocesses with timeout, output capture, and safety controls. Blocks dangerous commands, enforces resource limits, and returns structured results with exit codes, stdout, stderr, and timing."
metadata: {"openclaw": {"emoji": "📁", "os": ["darwin", "linux", "win32"]}}
type: agent
category: system
risk_level: medium
trust: supervised
parallel_safe: true
agent: system
consensus: any
tools: ["Bash"]
---

# Process Runner

Execute and manage subprocesses safely with command blocklisting, timeout enforcement, output capture, and structured results.

## Role

You are a subprocess execution specialist. You run shell commands safely, capture their output, enforce timeouts and resource limits, and return structured results. You are the controlled gateway between Gorgon agents and the operating system.

## When to Use

Use this skill when:
- Running shell commands that need safety controls (blocklist, timeout, audit logging)
- Executing build tools, test suites, or linters where exit codes and stderr matter
- Starting long-running background processes that need PID tracking and graceful shutdown
- Running command pipelines where each step must be validated against the blocklist

## When NOT to Use

Do NOT use this skill when:
- Reading, writing, or editing files — use the file-operations skill instead, because file operations need backup and path protection logic, not subprocess execution
- Making HTTP API requests — use the api-client skill instead, because API clients handle auth, retry, and response parsing natively
- Running git or GitHub operations — use the github-operations skill instead, because git workflows need branch protection and commit conventions
- The command is a simple, safe, single-step operation with no safety concerns — use the Bash tool directly, because skill overhead is unnecessary

## Core Behaviors

**Always:**
- Validate commands against the blocklist before execution
- Set timeouts for every subprocess (default: 60 seconds)
- Capture both stdout and stderr separately
- Record execution timing and exit codes
- Use absolute paths when possible
- Run with minimum required privileges
- Log every execution for audit trail

**Never:**
- Execute commands that modify system boot or init configuration — causes unbootable system state
- Run `rm -rf /` or any recursive delete on root paths — irreversible destruction of the entire filesystem
- Execute commands that disable security features (firewall, SELinux) — opens the system to network attacks
- Pipe untrusted input directly into shell commands — enables shell injection attacks
- Run commands as root unless explicitly required and approved — privilege escalation increases blast radius of any error
- Execute commands without timeout protection — runaway processes consume resources indefinitely

## Blocked Commands

The following patterns are always blocked:

```yaml
blocked_patterns:
  - "rm -rf /"
  - "rm -rf /*"
  - "mkfs"
  - "dd if=* of=/dev/sd*"
  - "> /dev/sda"
  - "chmod -R 777 /"
  - ":(){ :|:& };:"          # fork bomb
  - "shutdown"
  - "reboot"
  - "init 0"
  - "init 6"
  - "systemctl disable firewalld"
  - "iptables -F"             # flush all firewall rules
```

## Capabilities

### run
Execute a command synchronously with output capture. Use when the command completes in a bounded time and you need stdout/stderr. Do NOT use for commands expected to run longer than the timeout — use run_background instead.

- **Risk:** Medium
- **Consensus:** any
- **Parallel safe:** yes — each subprocess is independent
- **Intent required:** yes — agent must state what command is being run and why
- **Inputs:**
  - `command` (string, required) — the shell command to execute
  - `timeout` (integer, optional, default: 60) — maximum execution time in seconds
  - `cwd` (string, optional) — working directory for the command
  - `env` (dict, optional) — environment variables (merged with current env)
  - `shell` (boolean, optional, default: false) — run through shell (required for pipelines)
- **Outputs:**
  - `success` (boolean) — whether exit code was 0
  - `command` (string) — the command that was executed
  - `exit_code` (integer) — process exit code (-1 for errors/timeout)
  - `stdout` (string) — captured standard output
  - `stderr` (string) — captured standard error
  - `duration_ms` (integer) — execution time in milliseconds
  - `timed_out` (boolean) — whether the timeout was hit
  - `blocked` (boolean) — whether the command was blocked
  - `block_reason` (string) — why the command was blocked, if applicable
- **Post-execution:** Check exit_code — non-zero indicates failure. Examine stderr for error details. If timed_out is true, the command may still be running as a zombie process. If blocked is true, report the block_reason and do not attempt workarounds.

### run_background
Start a long-running process in the background and return its PID. Use for servers, watchers, or any process expected to outlive the current task. Do NOT use when you need the command's output immediately — use run instead.

- **Risk:** Medium
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state what background process is being started and its expected lifecycle
- **Inputs:**
  - `command` (string, required) — the command to run in the background
  - `cwd` (string, optional) — working directory
  - `log_file` (string, optional) — file path to redirect stdout/stderr
- **Outputs:**
  - `success` (boolean) — whether the process was started
  - `pid` (integer) — process ID for later management
  - `command` (string) — the command that was started
- **Post-execution:** Record the PID for later cleanup. If log_file was specified, verify the file is being written to. Background processes must be tracked — use kill_process for cleanup when done.

### kill_process
Terminate a running process by PID. Sends SIGTERM first, then SIGKILL after a grace period. Use to clean up background processes or terminate runaway commands.

- **Risk:** Medium
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — agent must state which process (PID) and why it is being terminated
- **Inputs:**
  - `pid` (integer, required) — process ID to terminate
  - `graceful_timeout` (integer, optional, default: 5) — seconds to wait after SIGTERM before SIGKILL
- **Outputs:**
  - `success` (boolean) — whether the process was terminated
- **Post-execution:** Verify the process is no longer running. If success is false, the process may require elevated privileges to kill — escalate to user.

### is_blocked
Check if a command would be blocked by the safety filter without executing it. Use for pre-validation before constructing complex command sequences.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** no
- **Inputs:**
  - `command` (string, required) — the command to check
- **Outputs:**
  - `blocked` (boolean) — whether the command matches a blocked pattern
  - `block_reason` (string or null) — the matched pattern, if blocked
- **Post-execution:** If blocked, do not attempt to reformulate the command to bypass the filter. Report the block reason and suggest a safe alternative.

## Implementation

### Core Runner (Python)

```python
"""Process runner with safety controls and structured output."""

import subprocess
import shlex
import time
import re
import os
import signal
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ProcessResult:
    """Structured result from a process execution."""
    success: bool
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool
    pid: Optional[int] = None
    blocked: bool = False
    block_reason: Optional[str] = None


BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/\s*$",
    r"rm\s+-rf\s+/\*",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/sd",
    r">\s*/dev/sd",
    r"chmod\s+-R\s+777\s+/\s*$",
    r":\(\)\{\s*:\|:&\s*\};:",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+[06]\b",
    r"systemctl\s+disable\s+firewalld",
    r"iptables\s+-F",
]


def is_blocked(command: str) -> Optional[str]:
    """Check if a command matches any blocked pattern."""
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command):
            return f"Command matches blocked pattern: {pattern}"
    return None


def run(
    command: str,
    timeout: int = 60,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    shell: bool = False,
) -> ProcessResult:
    """
    Execute a command with safety controls.

    Args:
        command: The command string to execute.
        timeout: Maximum execution time in seconds.
        cwd: Working directory for the command.
        env: Environment variables (merged with current env).
        shell: Whether to run through shell (default True).

    Returns:
        ProcessResult with exit code, stdout, stderr, and timing.
    """
    # Safety check
    block_reason = is_blocked(command)
    if block_reason:
        return ProcessResult(
            success=False,
            command=command,
            exit_code=-1,
            stdout="",
            stderr=block_reason,
            duration_ms=0,
            timed_out=False,
            blocked=True,
            block_reason=block_reason,
        )

    # Prepare environment
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    start = time.monotonic()
    timed_out = False

    try:
        proc = subprocess.run(
            command if shell else shlex.split(command),
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=run_env,
        )
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        exit_code = -1
        stdout = e.stdout or ""
        stderr = e.stderr or ""
    except Exception as e:
        exit_code = -1
        stdout = ""
        stderr = str(e)

    duration_ms = int((time.monotonic() - start) * 1000)

    return ProcessResult(
        success=exit_code == 0,
        command=command,
        exit_code=exit_code,
        stdout=stdout if isinstance(stdout, str) else stdout.decode("utf-8", errors="replace"),
        stderr=stderr if isinstance(stderr, str) else stderr.decode("utf-8", errors="replace"),
        duration_ms=duration_ms,
        timed_out=timed_out,
    )


def run_background(
    command: str,
    cwd: Optional[str] = None,
    log_file: Optional[str] = None,
) -> ProcessResult:
    """
    Start a process in the background and return its PID.

    Args:
        command: The command to run.
        cwd: Working directory.
        log_file: File to redirect output to.

    Returns:
        ProcessResult with PID set.
    """
    block_reason = is_blocked(command)
    if block_reason:
        return ProcessResult(
            success=False, command=command, exit_code=-1,
            stdout="", stderr=block_reason, duration_ms=0,
            timed_out=False, blocked=True, block_reason=block_reason,
        )

    stdout_dest = subprocess.DEVNULL
    if log_file:
        stdout_dest = open(log_file, "w")

    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=stdout_dest,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        start_new_session=True,
    )

    return ProcessResult(
        success=True, command=command, exit_code=0,
        stdout="", stderr="", duration_ms=0,
        timed_out=False, pid=proc.pid,
    )


def kill_process(pid: int, graceful_timeout: int = 5) -> bool:
    """
    Kill a process, trying SIGTERM first then SIGKILL.

    Args:
        pid: Process ID to kill.
        graceful_timeout: Seconds to wait after SIGTERM before SIGKILL.

    Returns:
        True if process was terminated.
    """
    try:
        os.kill(pid, signal.SIGTERM)
        start = time.monotonic()
        while time.monotonic() - start < graceful_timeout:
            try:
                os.kill(pid, 0)  # Check if still running
                time.sleep(0.1)
            except ProcessLookupError:
                return True
        # Force kill
        os.kill(pid, signal.SIGKILL)
        return True
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
```

### Usage Examples

```python
# Simple command
result = run("ls -la /tmp")
print(result.stdout)

# With timeout
result = run("sleep 100", timeout=5)
assert result.timed_out is True

# Blocked command
result = run("rm -rf /")
assert result.blocked is True

# Background process
result = run_background("python server.py", log_file="/tmp/server.log")
print(f"Server PID: {result.pid}")

# Later: kill it
kill_process(result.pid)
```

## Output Format

### Process Result
Use when: Returning results from any command execution

```json
{
  "success": true,
  "command": "ls -la /tmp",
  "exit_code": 0,
  "stdout": "total 8\ndrwxrwxrwt 2 root root ...",
  "stderr": "",
  "duration_ms": 12,
  "timed_out": false
}
```

## Verification

### Pre-completion Checklist
Before reporting process execution as complete, verify:
- [ ] Command was checked against the blocklist before execution
- [ ] Timeout was set (no unbounded execution)
- [ ] Exit code was checked and reported
- [ ] Both stdout and stderr were captured and included in output
- [ ] Background processes have their PIDs recorded for later cleanup

### Checkpoints
Pause and reason explicitly when:
- Command contains shell metacharacters (pipes, redirects, semicolons) — verify each component against the blocklist
- Exit code is non-zero — examine stderr before retrying or reporting
- Command timed out — the process may still be running; decide whether to kill or extend
- About to execute a command with `sudo` or as root — verify this is explicitly required and approved
- Multiple commands are being chained — validate each independently before execution

## Error Handling

### Escalation Ladder

| Error Type | Action | Max Retries |
|------------|--------|-------------|
| Command blocked | Report block reason, suggest alternative | 0 |
| Non-zero exit code | Examine stderr, report details | 0 |
| Timeout expired | Report partial output, offer to extend timeout or kill | 0 |
| Permission denied | Report, suggest running with appropriate permissions | 0 |
| Command not found | Check PATH, suggest installation | 0 |
| Process won't terminate | Escalate from SIGTERM to SIGKILL | 1 |
| Same error after retries | Stop, report what was attempted | — |

### Self-Correction
If this skill's protocol is violated:
- Blocklist check skipped: halt immediately, run the check retroactively, report the violation
- Timeout not set: terminate the process immediately if still running, apply timeout on retry
- Output not captured: re-run the command with capture enabled if safe to do so
- Background process PID not recorded: attempt to find the process by command name, log for cleanup

## Constraints

- Default timeout: 60 seconds
- Maximum timeout: 3600 seconds (1 hour)
- Blocked commands cannot be overridden
- All executions are logged with timestamps
- Background processes must be tracked for cleanup
- Shell injection prevention via blocklist (not parameterization — shell=True is required for pipelines)
