---
name: types
description: Python Type Hint Generator
---

# /types - Python Type Hint Generator

Add type hints to untyped Python code.

## Usage
```
/types path/to/file.py         # Add types to specific file
/types path/to/module/         # Add types to all files in module
/types --check                 # Report type coverage without changes
/types --strict                # Use strict typing (no Any)
```

## What This Skill Does

1. **Analyze Code** - Parse functions, classes, variables
2. **Infer Types** - From usage, defaults, docstrings
3. **Add Annotations** - Function signatures, class attributes
4. **Import Types** - Add necessary typing imports
5. **Validate** - Run mypy to verify additions

## Type Inference Rules

### From Default Values
```python
# Before
def greet(name, count=1):
    ...

# After
def greet(name: str, count: int = 1) -> None:
    ...
```

### From Usage
```python
# Before
def process(items):
    for item in items:
        item.upper()
    return len(items)

# After
def process(items: list[str]) -> int:
    ...
```

### From Docstrings
```python
# Before
def fetch(url):
    """
    Fetch data from URL.

    Args:
        url: The URL to fetch

    Returns:
        Response data as dict
    """

# After
def fetch(url: str) -> dict:
    ...
```

### Common Patterns
```python
# Collections
list[str]           # List of strings
dict[str, int]      # Dict with string keys, int values
set[int]            # Set of integers
tuple[str, int]     # Tuple with specific types

# Optional
str | None          # Optional string (Python 3.10+)
Optional[str]       # Optional string (older syntax)

# Callable
Callable[[int, str], bool]  # Function taking int, str returning bool

# Union
int | str           # Either int or string

# Any (avoid when possible)
Any                 # Unknown type
```

## Output Format

```markdown
## Type Hints Added: path/to/file.py

### Summary
- Functions typed: 12/15
- Classes typed: 3/3
- Variables typed: 8/10
- Type coverage: 87%

### Changes Made
```python
# Line 23: Added parameter and return types
- def process(data):
+ def process(data: list[dict[str, Any]]) -> ProcessResult:

# Line 45: Added class attribute types
+ items: list[Item]
+ cache: dict[str, bytes]
```

### Imports Added
```python
from typing import Any
from collections.abc import Callable
```

### Unable to Infer
- Line 67: `unknown_param` - insufficient context
- Line 89: `dynamic_result` - runtime-dependent
```

## Instructions for Claude

When /types is invoked:

1. **Read the file** - Parse Python AST
2. **Find untyped code** - Functions, methods, class attributes
3. **Infer types** - From defaults, usage, docstrings
4. **Prefer modern syntax** - `list[str]` over `List[str]`
5. **Use | for unions** - `str | None` over `Optional[str]`
6. **Add imports** - Only what's needed
7. **Avoid Any** - Unless truly dynamic
8. **Validate with mypy** - Check additions are correct
9. **Report coverage** - Before/after type coverage
