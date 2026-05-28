# /refactor - Code Refactoring Analysis

Identify refactoring opportunities and code improvements.

## Usage
```
/refactor path/to/file.py      # Analyze specific file
/refactor path/to/module/      # Analyze entire module
/refactor --apply              # Apply suggested refactorings
/refactor --complexity         # Focus on complexity reduction
```

## What This Skill Does

1. **Complexity Analysis** - Find functions with high cyclomatic complexity
2. **Duplication Detection** - Identify repeated code patterns
3. **Code Smells** - Long methods, large classes, deep nesting
4. **Design Issues** - Single responsibility, coupling, cohesion
5. **Suggest Improvements** - Actionable refactoring steps

## Analysis Categories

### Complexity Issues
- Cyclomatic complexity > 10
- Nesting depth > 4
- Function length > 50 lines
- Class length > 300 lines
- Too many parameters (> 5)

### Duplication
- Repeated code blocks
- Similar function patterns
- Copy-paste with slight variations

### Code Smells
- God classes/functions
- Feature envy
- Long parameter lists
- Magic numbers
- Dead code

### Design Issues
- Tight coupling
- Low cohesion
- Missing abstractions
- Inconsistent patterns

## Report Format

```markdown
# Refactoring Report: module_name

## Summary
| Issue Type | Count | Priority |
|------------|-------|----------|
| High Complexity | 3 | High |
| Duplication | 5 | Medium |
| Code Smells | 8 | Low |

## High Priority Issues

### 1. Complex Function: `process_data()` (file.py:45)
**Complexity**: 15 (threshold: 10)
**Lines**: 87

**Problem**: Function does too many things - validates, transforms, saves.

**Suggested Refactoring**:
```python
# Before (simplified)
def process_data(data):
    # validation (20 lines)
    # transformation (40 lines)
    # saving (25 lines)

# After
def process_data(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    return save_data(transformed)

def validate_data(data): ...
def transform_data(data): ...
def save_data(data): ...
```

### 2. Duplicated Code: `calculate_*` functions
**Location**: math_utils.py:23, math_utils.py:67, math_utils.py:112
**Similarity**: 85%

**Problem**: Three functions share nearly identical structure.

**Suggested Refactoring**:
```python
# Before
def calculate_sum(items): ...
def calculate_avg(items): ...
def calculate_max(items): ...

# After
def calculate(items, operation: Callable):
    return operation(items)
```

## Medium Priority Issues

### 3. Long Parameter List: `create_report()`
**Parameters**: 8

**Suggested Refactoring**: Use a dataclass or config object.
```python
@dataclass
class ReportConfig:
    title: str
    format: str
    ...

def create_report(config: ReportConfig): ...
```

## Metrics
- **Total Functions**: 45
- **Complex Functions**: 3 (7%)
- **Average Complexity**: 5.2
- **Duplicated Lines**: ~120 (8%)
```

## Instructions for Claude

When /refactor is invoked:

1. **Read code** - Parse and understand structure
2. **Calculate metrics** - Complexity, length, nesting
3. **Find duplication** - Similar code blocks
4. **Identify smells** - God classes, feature envy, etc.
5. **Prioritize issues** - High/Medium/Low based on impact
6. **Suggest fixes** - Concrete, actionable refactorings
7. **Show before/after** - Code examples for each fix
8. **If --apply** - Implement the refactorings
9. **Verify** - Run tests after changes
