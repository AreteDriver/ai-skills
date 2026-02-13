# 🔧 Build a Claude Skill: Local Linux Development Access

## For Senior Linux Developer/Engineer

---

## 📋 **Executive Summary**

**Goal**: Create a Claude Skill (`.skill` package) that enables Claude to access local Linux filesystem directories when using Claude Code CLI.

**Deliverable**: A packaged `local-dev.skill` file that I can install.

---

## 🎯 **What is a Claude Skill?**

A Claude Skill is a modular package that extends Claude's capabilities. Skills consist of:

```
skill-name/
├── SKILL.md           # REQUIRED: Instructions Claude reads (YAML frontmatter + Markdown)
├── scripts/           # Optional: Executable Python/Bash scripts
├── references/        # Optional: Documentation Claude loads as needed
└── assets/            # Optional: Templates, files used in output
```

**Key Points:**
- Only `SKILL.md` is required
- Claude reads the `description` field in YAML frontmatter to decide WHEN to trigger the skill
- The Markdown body is only loaded AFTER the skill triggers
- Keep it concise - context window is shared with conversation

---

## 📁 **Desired Skill Structure**

```
local-dev/
├── SKILL.md                    # Main instructions
├── scripts/
│   ├── mount_workspace.py      # Mount local dirs to container
│   ├── project_analyzer.py     # Analyze project structure
│   └── github_prep.py          # Prepare projects for GitHub
├── references/
│   ├── available_paths.md      # List of accessible directories
│   └── security_boundaries.md  # What Claude cannot access
└── assets/
    ├── gitignore_templates/    # Common .gitignore files
    └── readme_templates/       # README templates by project type
```

---

## 📝 **Required SKILL.md Content**

```yaml
---
name: local-dev
description: >
  Linux local development environment access skill. Enables Claude to read,
  analyze, and modify files in the user's local project directories. Use this
  skill when: (1) User references local paths like /home/arete/projects,
  (2) User asks to analyze their codebase, (3) User wants to prepare projects
  for GitHub, (4) User needs to work with files on their local machine,
  (5) User mentions "my projects" or "my code".
---

# Local Development Access

## Available Paths

The following directories are mounted and accessible:
- `/mnt/workspace/projects` → User's projects directory
- `/mnt/workspace/documents` → User's documents

## Quick Start

To list user's projects:
\`\`\`bash
ls /mnt/workspace/projects
\`\`\`

To analyze a project:
\`\`\`bash
python /path/to/skill/scripts/project_analyzer.py /mnt/workspace/projects/ProjectName
\`\`\`

## Security Boundaries

NEVER attempt to access:
- ~/.ssh
- ~/.gnupg
- ~/.aws
- Any credential stores

## Common Workflows

### Analyzing a Project
1. List directory structure
2. Read key files (README, package.json, requirements.txt, etc.)
3. Identify project type and dependencies
4. Provide analysis and recommendations

### Preparing for GitHub
1. Run `scripts/github_prep.py` with project path
2. Review generated files
3. Guide user through publishing steps

## References

For detailed path configuration, see `references/available_paths.md`
For security guidelines, see `references/security_boundaries.md`
```

---

## 🔧 **Technical Challenge: The Mount Problem**

### Current State
- Claude Code runs in a container
- Container has `/mnt/user-data/uploads/` for uploaded files
- Container has `/mnt/skills/` for skills
- Container CANNOT access host filesystem directly

### Required Solution

You need to figure out one of these approaches:

**Option A: Docker Bind Mount**
```bash
# If Claude Code uses Docker, modify launch to include:
docker run -v /home/arete/projects:/mnt/workspace/projects ...
```

**Option B: FUSE Filesystem**
```bash
# Create a FUSE mount that bridges container and host
# Skill scripts interact with this mount point
```

**Option C: SSH/SFTP Bridge**
```python
# Skill scripts connect back to host via SSH
# Read/write files through SSH connection
```

**Option D: Shared Volume**
```bash
# Configure a Docker volume shared between host and container
# Skill accesses this shared volume
```

**Option E: Socket Communication**
```python
# Daemon on host exposes filesystem via Unix socket
# Skill scripts communicate via socket
```

### Investigation Needed

```bash
# Run these in Claude Code to understand the environment:
cat /proc/1/cgroup          # Container type
mount                        # Current mounts
ls -la /mnt/                # Available mount points
env | grep -i docker        # Docker-related vars
cat /etc/os-release         # Container OS
```

---

## 🛠️ **Scripts to Create**

### 1. `scripts/mount_workspace.py`

```python
#!/usr/bin/env python3
"""
Mount local workspace directories into Claude's environment.
This is the KEY script that makes the skill work.
"""

# TODO: Implement based on investigation of Claude Code's container

def mount_workspace(local_path: str, mount_point: str) -> bool:
    """Mount a local directory into the container."""
    pass

def verify_mount(mount_point: str) -> bool:
    """Verify a mount is working."""
    pass

def get_available_paths() -> list:
    """Return list of mounted paths."""
    pass
```

### 2. `scripts/project_analyzer.py`

```python
#!/usr/bin/env python3
"""Analyze a project directory and return structured information."""

import os
import json
from pathlib import Path

def analyze_project(project_path: str) -> dict:
    """
    Analyze project and return:
    - Project type (python, node, rust, etc.)
    - Dependencies
    - Structure
    - Missing files (README, LICENSE, etc.)
    - Recommendations
    """
    pass
```

### 3. `scripts/github_prep.py`

```python
#!/usr/bin/env python3
"""Prepare a project for GitHub publication."""

def prepare_for_github(project_path: str) -> dict:
    """
    Generate/check:
    - README.md
    - LICENSE
    - .gitignore
    - CONTRIBUTING.md (if applicable)
    - GitHub Actions workflows
    
    Returns dict of created/missing files.
    """
    pass
```

---

## 🔐 **Security Requirements**

### Mandatory Exclusions
```python
EXCLUDED_PATHS = [
    "~/.ssh",
    "~/.gnupg", 
    "~/.aws",
    "~/.password-store",
    "~/.config/gcloud",
    "~/.kube",
    "~/.docker/config.json",
    "**/.*credentials*",
    "**/*secret*",
    "**/*token*",
]
```

### Security Script
```python
def is_path_allowed(path: str) -> bool:
    """Check if path is safe to access."""
    pass

def sanitize_path(path: str) -> str:
    """Ensure path doesn't escape allowed directories."""
    pass
```

---

## 📦 **Packaging**

Once complete, package using:
```bash
# From skill-creator's scripts:
python scripts/package_skill.py ./local-dev
```

This creates `local-dev.skill` which I can install.

---

## 🎯 **Success Criteria**

After skill installation, Claude should be able to:

```bash
# List my projects
ls /mnt/workspace/projects

# Read files
cat /mnt/workspace/projects/G13LogitechOPS/README.md

# Analyze a project
python scripts/project_analyzer.py /mnt/workspace/projects/EVE-Overview-Pro

# Prepare for GitHub
python scripts/github_prep.py /mnt/workspace/projects/some-project
```

---

## 🌍 **My Environment**

```yaml
Host System:
  os: Ubuntu 24.04 LTS
  user: arete
  home: /home/arete
  shell: zsh
  
Projects Location:
  path: /home/arete/projects
  count: 37 projects
  types: Python, JavaScript, C, Shell, Flutter
  
Claude Code:
  version: Latest
  install: Standard installation
```

---

## 📞 **Questions You May Need Answered**

1. What container runtime does Claude Code use?
2. Can I modify how Claude Code launches its container?
3. Is there a config file for Claude Code I can edit?
4. Are there hooks for adding custom mounts?

I can help investigate these by running commands in Claude Code.

---

## 💡 **Alternative: Simpler Approach**

If full mount access isn't possible, a simpler skill could:

1. **On-demand copying**: Script that copies specified project to `/mnt/user-data/uploads/`
2. **Project index**: Maintain an index file of all projects that Claude can read
3. **CLI wrapper**: Script user runs BEFORE Claude Code to set up mounts

Example simpler workflow:
```bash
# User runs before starting Claude:
./setup-claude-workspace.sh /home/arete/projects

# This creates symlinks or copies to accessible location
# Skill then works with those files
```

---

## ⏱️ **Estimated Effort**

- **Investigation phase**: 2-4 hours (understand Claude Code container)
- **Core implementation**: 4-6 hours (mount solution + scripts)
- **Testing & packaging**: 2-3 hours
- **Total**: 8-13 hours

---

## 📚 **References**

### Skill Documentation Location
```
/mnt/skills/examples/skill-creator/SKILL.md     # How to create skills
/mnt/skills/examples/skill-creator/scripts/     # Packaging scripts
/mnt/skills/public/docx/SKILL.md                # Example: document skill
/mnt/skills/public/pdf/SKILL.md                 # Example: PDF skill
```

### Key Patterns from Existing Skills
- Use Python scripts for complex operations
- Keep SKILL.md under 500 lines
- Use references/ for detailed docs
- Test scripts before packaging

---

## ✅ **Deliverables Checklist**

- [ ] Working mount/access solution
- [ ] `local-dev/SKILL.md` with proper frontmatter
- [ ] `scripts/mount_workspace.py` (or equivalent)
- [ ] `scripts/project_analyzer.py`
- [ ] `scripts/github_prep.py`
- [ ] `references/available_paths.md`
- [ ] `references/security_boundaries.md`
- [ ] Packaged `local-dev.skill` file
- [ ] Installation instructions
- [ ] Testing verification

---

**Thank you! This skill will dramatically improve my development workflow with Claude.**

*Contact me with any questions - I'm happy to run investigative commands or provide more details about my setup.*
