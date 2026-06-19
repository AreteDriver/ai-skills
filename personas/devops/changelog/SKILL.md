---
name: changelog
description: Generate Changelog from Commits
lifecycle: experimental
---

# /changelog - Generate Changelog from Commits

Generate or update CHANGELOG.md from conventional commits.

## Usage
```
/changelog                    # Generate from last tag to HEAD
/changelog v1.0.0..v1.1.0     # Specific range
/changelog --init             # Create new CHANGELOG.md
/changelog --unreleased       # Add unreleased section
```

## What This Skill Does

1. **Parse Commits** - Extract conventional commit messages
2. **Categorize Changes** - Group by type (feat, fix, etc.)
3. **Generate Markdown** - Format as Keep a Changelog style
4. **Update File** - Insert new version section

## Conventional Commit Types

| Prefix | Category | Description |
|--------|----------|-------------|
| `feat:` | Added | New features |
| `fix:` | Fixed | Bug fixes |
| `docs:` | Documentation | Doc changes only |
| `refactor:` | Changed | Code refactoring |
| `perf:` | Changed | Performance improvements |
| `test:` | Other | Test additions/changes |
| `chore:` | Other | Maintenance tasks |
| `breaking:` | Breaking | Breaking changes |
| `security:` | Security | Security fixes |

## Output Format (Keep a Changelog)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2024-01-15

### Added
- New feature X for better Y (#123)
- Support for Z configuration

### Fixed
- Bug where A caused B (#456)
- Crash on startup with invalid config

### Changed
- Improved performance of data loading
- Refactored authentication module

### Security
- Updated dependency with CVE fix

## [1.1.0] - 2024-01-01
...
```

## Git Commands Used

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Get commits between tags
git log v1.0.0..v1.1.0 --pretty=format:"%s"

# Get latest tag
git describe --tags --abbrev=0

# Get all tags sorted by version
git tag --sort=-v:refname
```

## Instructions for Claude

When /changelog is invoked:

1. **Find version range** - Last tag to HEAD, or specified range
2. **Get commits** - Use git log to extract messages
3. **Parse conventional commits** - Extract type, scope, description
4. **Categorize** - Group by Added, Fixed, Changed, etc.
5. **Format markdown** - Keep a Changelog format
6. **Handle non-conventional** - Include as "Other" or skip
7. **Update file** - Insert new section or create file
8. **Include PR/issue refs** - Extract (#123) references
