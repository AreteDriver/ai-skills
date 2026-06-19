---
name: spec
description: Technical Specification Writer
lifecycle: experimental
---

# /spec - Technical Specification Writer

Write technical specifications from requirements.

## Usage
```
/spec <feature description>
/spec --template api      # Use API spec template
/spec --template feature  # Use feature spec template
```

## What This Skill Does

1. **Gather Requirements** - Clarify what needs to be built
2. **Research Context** - Understand existing code and patterns
3. **Write Spec** - Create detailed technical specification
4. **Define Interfaces** - API contracts, data structures, protocols
5. **Identify Edge Cases** - Error handling, validation, limits

## Output Format

```markdown
# Technical Specification: [Feature Name]

## Status
- **Author**: [name]
- **Status**: Draft | Review | Approved
- **Last Updated**: [date]

## Summary
One paragraph describing what this feature does and why.

## Goals
- Goal 1
- Goal 2

## Non-Goals
- Explicitly out of scope item

## Background
Context needed to understand this feature.

## Design

### Architecture
How this fits into the existing system.

### Data Model
```python
@dataclass
class NewEntity:
    id: str
    name: str
    created_at: datetime
```

### API / Interface
```python
def new_function(param: str) -> Result:
    """
    Args:
        param: Description
    Returns:
        Result object
    Raises:
        ValueError: When param is invalid
    """
```

### Error Handling
| Error | Cause | Response |
|-------|-------|----------|
| ValidationError | Invalid input | 400 + message |

## Security Considerations
- Authentication requirements
- Authorization rules
- Input validation

## Testing Strategy
- Unit tests for X
- Integration tests for Y

## Rollout Plan
1. Phase 1: Internal testing
2. Phase 2: Limited release
3. Phase 3: General availability

## Open Questions
- [ ] Question 1?
```

## Instructions for Claude

When /spec is invoked:

1. **Clarify requirements** - Ask questions before writing
2. **Research existing code** - Understand patterns and conventions
3. **Be specific** - Include actual function signatures, data structures
4. **Consider edge cases** - Error handling, validation, limits
5. **Security first** - Always include security considerations
6. **Keep actionable** - Spec should be directly implementable
