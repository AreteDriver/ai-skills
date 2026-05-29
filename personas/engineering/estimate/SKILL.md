---
name: estimate
description: Task Estimation Techniques
---

# /estimate - Task Estimation Techniques

Structured approach to estimating development tasks.

## Usage
```
/estimate "add user authentication"    # Estimate a task
/estimate --breakdown                  # Detailed breakdown
/estimate --range                      # Provide ranges
/estimate --compare                    # Compare techniques
```

## What This Skill Does

1. **Analyze Task** - Understand scope, complexity
2. **Break Down** - Decompose into subtasks
3. **Identify Risks** - Unknowns, dependencies
4. **Apply Techniques** - T-shirt, story points, hours
5. **Provide Ranges** - Optimistic/realistic/pessimistic

## Estimation Report Format

```markdown
# Estimate: [Task Description]

## Task Analysis

### Scope
What's included in this task.

### Not Included
What's explicitly out of scope.

### Assumptions
- Assumption 1
- Assumption 2

### Dependencies
- Dependency 1
- Dependency 2

---

## Breakdown

| Subtask | Complexity | Estimate |
|---------|------------|----------|
| Design/planning | Low | S |
| Core implementation | Medium | M |
| Tests | Low | S |
| Documentation | Low | XS |
| Code review | Low | XS |
| **Total** | | **M-L** |

---

## Estimate

### T-Shirt Size
**M** (Medium)

| Size | Typical Range |
|------|---------------|
| XS | < 2 hours |
| S | 2-4 hours |
| M | 4-8 hours (1 day) |
| L | 1-3 days |
| XL | 3-5 days |
| XXL | 1-2 weeks |

### Three-Point Estimate
| Scenario | Estimate | Notes |
|----------|----------|-------|
| Optimistic | 4 hours | Everything goes smoothly |
| Realistic | 8 hours | Some minor issues |
| Pessimistic | 16 hours | Unexpected complications |

**Expected**: 8-10 hours (weighted average)

### Story Points
**5 points** (Fibonacci: 1, 2, 3, 5, 8, 13, 21)

Reference:
- 1 point = trivial change, < 1 hour
- 3 points = straightforward, half day
- 5 points = moderate complexity, 1 day
- 8 points = significant work, 2-3 days
- 13+ points = should be broken down

---

## Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unclear requirements | Medium | High | Clarify before starting |
| Integration issues | Low | Medium | Spike first |
| Learning curve | Low | Low | Time-box research |

### Confidence Level
**Medium** (70%)

Factors affecting confidence:
- [+] Well-understood domain
- [+] Similar work done before
- [-] External API integration
- [-] Some unknowns in requirements

---

## Recommendations

1. **Clarify before starting**: [specific questions]
2. **Spike if needed**: [area of uncertainty]
3. **Break down further**: [if XXL]
4. **Add buffer**: Include 20% for unknowns
```

## Estimation Techniques

### T-Shirt Sizing
Best for: Rough estimates, backlog grooming

| Size | Effort | Complexity | Risk |
|------|--------|------------|------|
| XS | Trivial | None | None |
| S | Small | Low | Low |
| M | Medium | Medium | Low-Med |
| L | Large | High | Medium |
| XL | Very Large | High | High |
| XXL | Epic | Very High | High |

### Story Points (Fibonacci)
Best for: Sprint planning, relative sizing

```
1  - Trivial (< 1 hour)
2  - Simple (1-2 hours)
3  - Straightforward (half day)
5  - Moderate (1 day)
8  - Complex (2-3 days)
13 - Very complex (1 week)
21 - Epic (break it down!)
```

### Three-Point Estimation
Best for: Schedule planning, risk assessment

```
Expected = (Optimistic + 4×Realistic + Pessimistic) / 6

Example:
- Optimistic: 2 days
- Realistic: 4 days
- Pessimistic: 10 days
- Expected: (2 + 16 + 10) / 6 = 4.7 days
```

### PERT (with standard deviation)
```
Expected = (O + 4M + P) / 6
Std Dev = (P - O) / 6

95% confidence = Expected ± 2×StdDev
```

## Common Estimation Mistakes

### Underestimation
- Forgetting tests
- Forgetting code review time
- Forgetting documentation
- Ignoring integration time
- Optimism bias

### Overestimation
- Adding too much buffer
- Accounting for same risk multiple times
- Not recognizing reusable components

### General Mistakes
- Estimating without understanding scope
- Not breaking down large tasks
- Ignoring dependencies
- Treating estimates as commitments
- Not tracking actuals vs estimates

## Estimation Checklist

```markdown
Before estimating:
- [ ] Requirements are clear
- [ ] Scope is defined
- [ ] Dependencies identified
- [ ] Similar past work referenced

Include in estimate:
- [ ] Design/planning time
- [ ] Implementation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Code review
- [ ] Documentation
- [ ] Bug fixes (buffer)
- [ ] Meetings/communication

After estimating:
- [ ] Confidence level stated
- [ ] Risks identified
- [ ] Assumptions documented
- [ ] Range provided (not single number)
```

## Instructions for Claude

When /estimate is invoked:

1. **Understand the task** - What's being estimated
2. **Clarify scope** - What's in, what's out
3. **Break down** - Decompose into subtasks
4. **Identify unknowns** - Risks, dependencies
5. **Apply techniques** - T-shirt, points, hours
6. **Provide range** - Not a single number
7. **State confidence** - How sure are we
8. **Document assumptions** - What we're assuming
9. **Recommend actions** - Clarify, spike, break down
