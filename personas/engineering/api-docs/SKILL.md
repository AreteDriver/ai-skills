---
name: api-docs
description: API Documentation Generator
lifecycle: experimental
---

# /api-docs - API Documentation Generator

Generate API documentation from code.

## Usage
```
/api-docs                     # Document all public APIs
/api-docs path/to/module.py   # Document specific module
/api-docs --format markdown   # Output format
/api-docs --format openapi    # Generate OpenAPI spec
```

## What This Skill Does

1. **Parse Code** - Extract functions, classes, methods
2. **Read Docstrings** - Google, NumPy, or Sphinx style
3. **Infer Types** - From annotations and usage
4. **Generate Docs** - Markdown or OpenAPI format
5. **Include Examples** - From docstrings or tests

## Output Formats

### Markdown API Docs

```markdown
# API Reference

## module_name

### `function_name(param1, param2)`

Description from docstring.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| param1 | `str` | What param1 does |
| param2 | `int` | What param2 does |

**Returns:**
| Type | Description |
|------|-------------|
| `Result` | What it returns |

**Raises:**
| Exception | Condition |
|-----------|-----------|
| `ValueError` | When param1 is empty |

**Example:**
```python
result = function_name("hello", 42)
```

---

### `ClassName`

Class description.

#### `__init__(self, arg1)`
Constructor description.

#### `method_name(self, param)`
Method description.
```

### OpenAPI Spec (for REST APIs)

```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0
paths:
  /endpoint:
    get:
      summary: Get something
      parameters:
        - name: id
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Response'
```

## Docstring Styles Supported

### Google Style
```python
def func(param1: str, param2: int) -> Result:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When something is wrong.

    Example:
        >>> func("hello", 42)
        Result(...)
    """
```

### NumPy Style
```python
def func(param1, param2):
    """
    Short description.

    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int
        Description of param2.

    Returns
    -------
    Result
        Description of return value.
    """
```

## Instructions for Claude

When /api-docs is invoked:

1. **Find public API** - Modules, classes, functions without _ prefix
2. **Parse docstrings** - Detect style, extract sections
3. **Get type info** - From annotations or docstrings
4. **Find examples** - In docstrings or test files
5. **Generate docs** - In requested format
6. **Organize by module** - Logical grouping
7. **Add navigation** - Table of contents for large APIs
8. **Write output** - docs/api.md or similar
