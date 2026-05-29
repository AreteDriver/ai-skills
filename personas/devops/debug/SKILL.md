---
name: debug
description: Systematic Debugging Workflow
---

# /debug - Systematic Debugging Workflow

Structured approach to debugging issues.

## Usage
```
/debug <error message or description>
/debug --trace                # Include stack trace analysis
/debug --bisect               # Git bisect guidance
```

## What This Skill Does

1. **Understand the Problem** - Parse error, reproduce issue
2. **Form Hypotheses** - Likely causes based on error type
3. **Systematic Investigation** - Step-by-step debugging
4. **Identify Root Cause** - Narrow down to exact issue
5. **Propose Fix** - Solution with verification

## Debugging Framework

```markdown
# Debug Session: [Issue Description]

## 1. Problem Statement
**Error**: [Exact error message]
**When**: [When does it occur]
**Frequency**: [Always / Sometimes / Once]

## 2. Reproduction Steps
1. Step 1
2. Step 2
3. Error occurs

**Minimal Reproduction**:
```python
# Smallest code that reproduces the issue
```

## 3. Initial Hypotheses
| # | Hypothesis | Likelihood | Test |
|---|------------|------------|------|
| 1 | Null pointer | High | Add null check |
| 2 | Race condition | Medium | Add logging |
| 3 | Config issue | Low | Check config |

## 4. Investigation Log

### Test 1: [Hypothesis being tested]
**Action**: What I did
**Result**: What happened
**Conclusion**: Confirmed / Ruled out

### Test 2: ...

## 5. Root Cause
[Exact cause identified]

## 6. Fix
```python
# Before
problematic_code()

# After
fixed_code()
```

## 7. Verification
- [ ] Fix applied
- [ ] Original issue resolved
- [ ] No regression introduced
- [ ] Test added to prevent recurrence
```

## Common Error Patterns

### Python
| Error | Common Causes |
|-------|---------------|
| `AttributeError` | None value, wrong type, typo |
| `KeyError` | Missing dict key, wrong key name |
| `ImportError` | Missing dep, circular import, wrong path |
| `TypeError` | Wrong arg type, wrong arg count |
| `ValueError` | Invalid value, parsing error |

### Rust
| Error | Common Causes |
|-------|---------------|
| `unwrap() panic` | None/Err not handled |
| `borrow checker` | Ownership, lifetime issues |
| `type mismatch` | Generic constraints, conversions |

## Debugging Commands

```bash
# Python with debugger
python -m pdb script.py

# Python with verbose imports
python -v script.py

# Rust with backtrace
RUST_BACKTRACE=1 cargo run

# Git bisect
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
```

## Instructions for Claude

When /debug is invoked:

1. **Parse the error** - Extract error type, message, location
2. **Ask for context** - Reproduction steps, when it started
3. **Form hypotheses** - Rank by likelihood
4. **Test systematically** - One variable at a time
5. **Log findings** - Document each test and result
6. **Identify root cause** - Narrow down definitively
7. **Propose fix** - With before/after code
8. **Verify** - Confirm fix works, no regression
9. **Prevent recurrence** - Suggest test to add
