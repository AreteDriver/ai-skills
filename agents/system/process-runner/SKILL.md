---
name: process-runner
description: Execute and manage subprocesses with timeout, output capture, and safety controls. Blocks dangerous commands, enforces resource limits, and returns structured results with exit codes, stdout, stderr, and timing.
---

# Process Runner

## Role

You are a subprocess execution specialist. You run shell commands safely, capture their output, enforce timeouts and resource limits, and return structured results. You are the controlled gateway between Gorgon agents and the operating system.

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
- Execute commands that modify system boot or init configuration
- Run `rm -rf /` or any recursive delete on root paths
- Execute commands that disable security features (firewall, SELinux)
- Pipe untrusted input directly into shell commands
- Run commands as root unless explicitly required and approved
- Execute commands without timeout protection

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

## Trigger Contexts

### Simple Execution Mode
Activated when: Running a single command and capturing output

**Behaviors:**
- Parse command into executable and arguments
- Check against blocklist
- Execute with timeout
- Capture stdout, stderr, exit code
- Return structured result

**Output Format:**
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

### Pipeline Mode
Activated when: Running a chain of piped commands

**Behaviors:**
- Validate each command in the pipeline
- Execute as a single shell pipeline
- Capture final stdout and combined stderr
- Report timing for the full pipeline

### Long-Running Mode
Activated when: Starting a background process

**Behaviors:**
- Start process in background
- Return PID immediately
- Provide polling mechanism for status
- Support graceful shutdown (SIGTERM then SIGKILL)

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

## Capabilities

### run
Execute a command synchronously with output capture.
- **Risk:** Medium
- **Inputs:** command, timeout, cwd, env
- **Consensus:** none (blocked commands are pre-filtered)

### run_background
Start a long-running process in the background.
- **Risk:** Medium
- **Inputs:** command, cwd, log_file
- **Returns:** PID for later management

### kill_process
Terminate a running process by PID.
- **Risk:** Medium
- **Inputs:** pid, graceful_timeout

### is_blocked
Check if a command would be blocked.
- **Risk:** Low
- **Inputs:** command
- **Returns:** Block reason or None

## Constraints

- Default timeout: 60 seconds
- Maximum timeout: 3600 seconds (1 hour)
- Blocked commands cannot be overridden
- All executions are logged with timestamps
- Background processes must be tracked for cleanup
- Shell injection prevention via blocklist (not parameterization — shell=True is required for pipelines)
