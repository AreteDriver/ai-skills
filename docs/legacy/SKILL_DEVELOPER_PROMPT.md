# 🔧 Build a Claude Skill: Linux Development Environment Access

## Request for Senior Linux Developer/Engineer

---

## 📋 **Overview**

I need you to build a **Claude Skill** that enables Claude AI to have persistent, reliable access to my local Linux development environment. This skill should allow Claude to read, analyze, and work with my project files directly from the terminal using Claude Code.

---

## 🎯 **Objective**

Create a skill package that:
1. Mounts/exposes my local filesystem to Claude's containerized environment
2. Provides secure, controlled access to specific directories
3. Enables Claude to run common development tools (git, python, npm, etc.)
4. Persists across sessions where possible
5. Follows security best practices

---

## 📁 **What is a Claude Skill?**

A Claude Skill is a folder containing:
- `SKILL.md` - Main instructions file that Claude reads before performing tasks
- Supporting files (scripts, templates, configurations)
- Documentation for usage

Skills are stored in:
- `/mnt/skills/public/` - Anthropic's built-in skills
- `/mnt/skills/user/` - User-created skills (what we're building)
- `/mnt/skills/examples/` - Example skills

When Claude needs to perform a task, it reads the relevant `SKILL.md` file first to learn best practices.

---

## 🏗️ **Required Components**

### 1. **Filesystem Bridge Script**

Create a script that:
```bash
# Mounts or symlinks user directories to Claude-accessible paths
# Example: /home/arete/projects → /mnt/user-data/uploads/projects
```

Requirements:
- Mount my home directory or specific subdirectories
- Handle permissions correctly (read/write as needed)
- Work with Claude Code's container environment
- Be easily configurable for different paths

### 2. **SKILL.md File**

Create `/mnt/skills/user/linux-dev-access/SKILL.md` containing:
- Instructions for Claude on how to access local files
- Available commands and tools
- Directory structure information
- Security boundaries
- Common workflows

### 3. **Configuration File**

Create a config that specifies:
```yaml
# Example config structure
accessible_paths:
  - /home/arete/projects
  - /home/arete/Documents
  - /home/arete/.config

excluded_paths:
  - /home/arete/.ssh
  - /home/arete/.gnupg
  - /home/arete/.password-store

permissions:
  read: true
  write: true
  execute: true

tools_available:
  - git
  - python3
  - pip
  - npm
  - node
  - docker
  - make
  - gcc
```

### 4. **Installation Script**

Create `install-skill.sh` that:
- Sets up the skill directory structure
- Configures mounts/symlinks
- Sets appropriate permissions
- Integrates with Claude Code
- Provides verification tests

---

## 🔐 **Security Requirements**

### Must Have:
- [ ] No access to SSH keys, GPG keys, or credential stores
- [ ] No access to browser profiles or saved passwords
- [ ] Configurable path whitelist/blacklist
- [ ] Read-only option for sensitive directories
- [ ] Logging of all file access (optional)
- [ ] Easy revocation of access

### Nice to Have:
- [ ] Per-project permission scoping
- [ ] Time-limited access sessions
- [ ] Audit trail of changes
- [ ] Rollback capability for file changes

---

## 🛠️ **Technical Context**

### My Environment:
- **OS**: Ubuntu 24.04 LTS
- **Shell**: zsh
- **User**: arete
- **Home**: /home/arete
- **Projects**: /home/arete/projects (37 projects)

### Claude Code Environment:
- Runs in containerized environment
- Has access to `/mnt/user-data/uploads/` for uploaded files
- Has access to `/mnt/user-data/outputs/` for generated files
- Has access to `/mnt/skills/` for skill files
- Can execute bash commands
- Can create/edit files

### Current Limitation:
Claude cannot directly access `/home/arete/` - files must be uploaded through web interface or copied to mounted paths.

---

## 📝 **Desired SKILL.md Structure**

```markdown
# Linux Development Environment Access Skill

## Overview
This skill enables Claude to access and work with local Linux development files.

## Available Paths
[List of accessible directories]

## Available Tools
[List of CLI tools Claude can use]

## Common Workflows

### Analyzing a Project
1. Navigate to project directory
2. Read project structure
3. Analyze key files
4. Provide recommendations

### Making Changes
1. Create backup
2. Make modifications
3. Verify changes
4. Provide summary

### Git Operations
[Git workflow instructions]

## Security Boundaries
[What Claude cannot access]

## Troubleshooting
[Common issues and solutions]
```

---

## 🎯 **Use Cases to Support**

1. **Project Analysis**
   - Read and understand codebases
   - Review project structure
   - Analyze dependencies
   - Suggest improvements

2. **File Operations**
   - Create new files
   - Edit existing files
   - Organize directories
   - Search across projects

3. **Development Tasks**
   - Run tests
   - Build projects
   - Manage dependencies
   - Version control operations

4. **Documentation**
   - Generate READMEs
   - Create changelogs
   - Write technical docs
   - Update configuration files

5. **GitHub Preparation**
   - Initialize repositories
   - Create .gitignore files
   - Set up CI/CD configs
   - Prepare releases

---

## 📦 **Deliverables**

Please provide:

### 1. **Skill Package** (`linux-dev-access/`)
```
linux-dev-access/
├── SKILL.md              # Main skill instructions
├── README.md             # Human documentation
├── config.yaml           # Configuration file
├── scripts/
│   ├── setup.sh          # Initial setup
│   ├── mount.sh          # Mount directories
│   ├── unmount.sh        # Clean unmount
│   └── verify.sh         # Test access
├── templates/
│   └── project-analysis.md  # Template for project analysis
└── examples/
    └── usage-examples.md    # Example workflows
```

### 2. **Installation Guide**
- Step-by-step setup instructions
- Troubleshooting guide
- Verification tests

### 3. **Integration Instructions**
- How to integrate with Claude Code
- How to update/modify the skill
- How to add new accessible paths

---

## 🔍 **Questions to Consider**

1. **Container Access**: How does Claude Code's container handle mounts? Can we use Docker volumes, bind mounts, or symlinks?

2. **Persistence**: How do we make this access persistent across Claude sessions?

3. **Claude Code Internals**: What hooks or configuration does Claude Code expose for custom skills?

4. **Security Model**: What's the threat model we should design against?

5. **Performance**: How to handle large directories without timeout issues?

---

## 📚 **Reference Materials**

### Existing Skill Examples (from Claude's system):
- `/mnt/skills/public/docx/SKILL.md` - Document creation skill
- `/mnt/skills/public/pdf/SKILL.md` - PDF manipulation skill
- `/mnt/skills/public/pptx/SKILL.md` - Presentation skill
- `/mnt/skills/public/xlsx/SKILL.md` - Spreadsheet skill

### Skill Structure Pattern:
```markdown
# Skill Name

## When to Use This Skill
[Trigger conditions]

## Prerequisites
[Required tools/access]

## Instructions
[Step-by-step guidance for Claude]

## Best Practices
[Quality guidelines]

## Common Pitfalls
[What to avoid]

## Examples
[Usage examples]
```

---

## ✅ **Acceptance Criteria**

The skill is complete when:

1. [ ] Claude can list files in `/home/arete/projects`
2. [ ] Claude can read file contents from my projects
3. [ ] Claude can create/edit files in my projects
4. [ ] Claude can run git commands in my repositories
5. [ ] Claude can run Python/Node scripts
6. [ ] Sensitive directories are properly excluded
7. [ ] Setup is documented and reproducible
8. [ ] Skill can be easily enabled/disabled
9. [ ] Works with Claude Code terminal interface

---

## 💰 **Budget/Timeline**

- **Priority**: High
- **Complexity**: Medium-High
- **Estimated Time**: 4-8 hours for experienced Linux engineer

---

## 📞 **Contact**

For questions about:
- Claude's capabilities: Reference system prompt documentation
- My environment: Ask for any system info needed
- Use cases: I can provide more specific examples

---

## 🚀 **Getting Started**

1. Review Claude Code documentation (if available)
2. Examine existing skills in `/mnt/skills/public/`
3. Test basic file access mechanisms
4. Design the mount/access strategy
5. Implement and test the skill
6. Document everything

---

**Thank you for helping build this skill! This will significantly improve my workflow with Claude for software development tasks.**

---

## 📝 **Notes**

- This is for personal development use, not production deployment
- Security is important but this is a trusted local environment
- Flexibility and ease of use are priorities
- I'm happy to test iterations and provide feedback

---

*Created: December 24, 2025*
*For: Claude AI Skill Development*
*Author: Arete*
