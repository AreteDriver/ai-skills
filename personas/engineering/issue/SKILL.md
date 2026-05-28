# /issue - GitHub Issue Creator

Generate well-structured GitHub issues from descriptions.

## Usage
```
/issue bug: App crashes when clicking save
/issue feature: Add dark mode support
/issue --template bug         # Use bug template
/issue --template feature     # Use feature template
```

## What This Skill Does

1. **Parse Description** - Extract type, title, details
2. **Select Template** - Bug report, feature request, etc.
3. **Generate Content** - Structured issue body
4. **Create Issue** - Using gh CLI
5. **Add Labels** - Based on issue type

## Bug Report Template

```markdown
## Bug Description
Clear description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: Ubuntu 22.04
- Python: 3.11
- Version: 1.2.3

## Screenshots/Logs
```
Error traceback here
```

## Additional Context
Any other relevant information.
```

## Feature Request Template

```markdown
## Feature Description
Clear description of the feature.

## Problem It Solves
What problem does this address?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches you've thought about.

## Additional Context
Mockups, examples, or references.
```

## Commands Used

```bash
# Create issue
gh issue create --title "Title" --body "Body" --label "bug"

# Create with template
gh issue create --template bug_report.md

# List labels
gh label list
```

## Label Mapping

| Keyword | Label |
|---------|-------|
| bug, crash, error | `bug` |
| feature, add, new | `enhancement` |
| docs, documentation | `documentation` |
| help, question | `question` |
| urgent, critical | `priority: high` |

## Instructions for Claude

When /issue is invoked:

1. **Parse input** - Extract type (bug/feature) and description
2. **Select template** - Bug report or feature request
3. **Gather details** - Ask clarifying questions if needed
4. **Generate content** - Fill in template sections
5. **Suggest labels** - Based on content
6. **Create issue** - Use gh CLI
7. **Report URL** - Show the created issue link
