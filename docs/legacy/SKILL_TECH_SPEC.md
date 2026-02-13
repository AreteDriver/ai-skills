# Claude Skill: Local Filesystem Access - Technical Specification

## TL;DR

Build a Claude Skill that lets Claude AI access `/home/arete/projects` and other local directories when using Claude Code in terminal.

---

## Problem Statement

When using Claude Code (Anthropic's CLI tool), Claude runs in a containerized environment and cannot access my local filesystem directly. Files must be uploaded via web interface or copied manually.

**Goal**: Create a skill that bridges this gap securely.

---

## Technical Requirements

### 1. Directory Mounting

```bash
# Required mounts
/home/arete/projects     → /mnt/user-data/projects
/home/arete/Documents    → /mnt/user-data/documents

# Excluded (NEVER mount)
/home/arete/.ssh
/home/arete/.gnupg
/home/arete/.password-store
/home/arete/.aws
```

### 2. Skill File Structure

```
/mnt/skills/user/local-dev/
├── SKILL.md           # Claude reads this before tasks
├── config.yaml        # Paths and permissions
├── setup.sh           # One-time setup
└── mount.sh           # Runtime mount script
```

### 3. SKILL.md Content Requirements

Claude needs to know:
- What paths are available
- What tools can be used (git, python, npm, etc.)
- What NOT to do (security boundaries)
- Common workflows (analyze project, prepare for GitHub, etc.)

### 4. Integration Points

Investigate:
- How Claude Code handles `/mnt/` paths
- Whether Docker bind mounts work
- If FUSE filesystems are supported
- Claude Code's skill loading mechanism

---

## Deliverables

1. **Working skill package** that enables local file access
2. **Install script** for one-command setup
3. **Documentation** for usage and troubleshooting

---

## Environment Details

```yaml
os: Ubuntu 24.04 LTS
user: arete
home: /home/arete
shell: zsh
claude_tool: Claude Code (CLI)

projects_path: /home/arete/projects
project_count: 37
languages: Python, JavaScript, C, Shell
```

---

## Success Criteria

```bash
# These should work after skill installation:

# List my projects
ls /mnt/user-data/projects

# Read a file
cat /mnt/user-data/projects/G13LogitechOPS/README.md

# Run git
cd /mnt/user-data/projects/some-repo && git status

# Edit files
echo "test" >> /mnt/user-data/projects/test.txt
```

---

## Questions for Investigation

1. Does Claude Code use Docker? Podman? Custom container?
2. What's in `/mnt/` by default? Can we add to it?
3. Are there existing skill examples that do filesystem access?
4. Can we use `--mount` or `-v` flags when launching Claude Code?

---

## Reference: Existing Skills

Check these for patterns:
- `/mnt/skills/public/docx/SKILL.md`
- `/mnt/skills/public/pdf/SKILL.md`

These skills create/read files, so there's precedent for filesystem access.

---

## Contact

Questions? Need more info about my setup? Just ask.

**Priority**: High - This significantly improves my dev workflow.
