---
name: review
description: Code Review Checklist
lifecycle: experimental
---

# /review - Code Review Checklist

Systematic code review with comprehensive checklist.

## Usage
```
/review                          # Review staged changes
/review path/to/file.py          # Review specific file
/review --pr 123                  # Review pull request
/review --security               # Security-focused review
```

## What This Skill Does

1. **Analyze Changes** - Parse diff, understand context
2. **Check Quality** - Code standards, patterns, clarity
3. **Verify Correctness** - Logic, edge cases, error handling
4. **Security Scan** - Vulnerabilities, input validation
5. **Generate Report** - Findings with line references

## Code Review Checklist

```markdown
# Code Review: [PR/File]

## Summary
Brief description of changes being reviewed.

## Review Checklist

### Correctness
- [ ] Logic is correct and handles all cases
- [ ] Edge cases are handled
- [ ] Error conditions are handled appropriately
- [ ] No obvious bugs or regressions

### Code Quality
- [ ] Code is readable and self-documenting
- [ ] Functions/methods are focused (single responsibility)
- [ ] No unnecessary complexity
- [ ] DRY - no copy-paste duplication
- [ ] Naming is clear and consistent

### Testing
- [ ] Tests are included for new functionality
- [ ] Tests cover edge cases
- [ ] Tests are readable and maintainable
- [ ] All tests pass

### Security
- [ ] Input is validated/sanitized
- [ ] No hardcoded secrets
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities (if web)
- [ ] Authentication/authorization checked

### Performance
- [ ] No obvious performance issues
- [ ] No N+1 queries
- [ ] Appropriate data structures used
- [ ] No unnecessary allocations in hot paths

### Documentation
- [ ] Public APIs are documented
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] CHANGELOG updated if needed

### Style
- [ ] Follows project conventions
- [ ] Consistent formatting
- [ ] No commented-out code
- [ ] No debug prints/logs left in

## Findings

### Critical (Must Fix)
| Location | Issue | Suggestion |
|----------|-------|------------|
| file.py:42 | SQL injection risk | Use parameterized query |

### Major (Should Fix)
| Location | Issue | Suggestion |
|----------|-------|------------|
| file.py:78 | Missing error handling | Add try/except |

### Minor (Nice to Have)
| Location | Issue | Suggestion |
|----------|-------|------------|
| file.py:15 | Unclear variable name | Rename `x` to `user_count` |

### Positive Feedback
- Good test coverage for the new feature
- Clean separation of concerns
- Well-documented public API

## Verdict
- [ ] Approve
- [ ] Request Changes
- [ ] Comment (no blocking issues)
```

## Review by Category

### Security Review Focus
```markdown
## Security Checklist
- [ ] All user input validated
- [ ] SQL queries use parameterization
- [ ] No eval() or exec() with user input
- [ ] File paths sanitized (no path traversal)
- [ ] Secrets not logged or exposed
- [ ] Authentication on all sensitive endpoints
- [ ] Authorization checks in place
- [ ] CSRF protection (if web)
- [ ] Rate limiting considered
- [ ] Sensitive data encrypted
```

### Performance Review Focus
```markdown
## Performance Checklist
- [ ] Database queries optimized
- [ ] No N+1 query patterns
- [ ] Appropriate indexes exist
- [ ] Caching used where beneficial
- [ ] No blocking I/O in async code
- [ ] Memory usage reasonable
- [ ] No unbounded collections
- [ ] Pagination for large datasets
```

### API Review Focus
```markdown
## API Checklist
- [ ] RESTful conventions followed
- [ ] Status codes appropriate
- [ ] Error responses consistent
- [ ] Request validation complete
- [ ] Response format documented
- [ ] Versioning strategy clear
- [ ] Rate limiting implemented
- [ ] Authentication required
```

## Review Comments Format

### Blocking Issue
```
🚫 **Blocking**: SQL injection vulnerability

The user input is directly interpolated into the query.

```python
# Current (vulnerable)
query = f"SELECT * FROM users WHERE id = {user_id}"

# Suggested fix
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```
```

### Suggestion
```
💡 **Suggestion**: Consider using a constant here

This magic number appears multiple times. A named constant would improve clarity.

```python
MAX_RETRY_COUNT = 3
```
```

### Question
```
❓ **Question**: Is this intentional?

This seems to silently ignore the error. Should we log it?
```

### Praise
```
✨ **Nice**: Good use of the factory pattern here. Clean and extensible.
```

## Instructions for Claude

When /review is invoked:

1. **Get context** - What's being reviewed (diff, file, PR)
2. **Understand changes** - Read the code, understand intent
3. **Check correctness** - Logic, edge cases, error handling
4. **Check quality** - Readability, maintainability, patterns
5. **Security scan** - Vulnerabilities, input validation
6. **Performance check** - Obvious issues, N+1, complexity
7. **Verify tests** - Coverage, quality of tests
8. **Generate report** - Findings with severity and suggestions
9. **Be constructive** - Include positive feedback too
