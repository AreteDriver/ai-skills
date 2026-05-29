---
name: explain
description: Deep Code Explanation
---

# /explain - Deep Code Explanation

Provide detailed explanations of code, concepts, or patterns.

## Usage
```
/explain path/to/file.py         # Explain entire file
/explain function_name           # Explain specific function
/explain "async/await"           # Explain concept
/explain --level beginner        # Adjust explanation depth
```

## What This Skill Does

1. **Parse Code** - Understand structure and flow
2. **Identify Concepts** - Patterns, idioms, techniques
3. **Explain Purpose** - What and why
4. **Show Flow** - Step-by-step execution
5. **Provide Context** - When to use, alternatives

## Explanation Format

```markdown
# Explanation: [Topic]

## Overview
Brief summary of what this code/concept does.

## Purpose
Why does this exist? What problem does it solve?

## How It Works

### Step-by-Step
1. **Step 1**: Description
   ```python
   relevant_code_snippet()
   ```

2. **Step 2**: Description
   ```python
   next_snippet()
   ```

### Visual Flow
```
Input → Process A → Process B → Output
         ↓
    Side Effect
```

## Key Concepts

### Concept 1: [Name]
Explanation of underlying concept.

### Concept 2: [Name]
Explanation of another concept.

## Example Usage

```python
# Simple example
result = function(input)

# Advanced example with options
result = function(
    input,
    option1=True,
    option2="value"
)
```

## Common Pitfalls
- **Pitfall 1**: What goes wrong and how to avoid it
- **Pitfall 2**: Another common mistake

## Alternatives
- **Alternative 1**: When to use this instead
- **Alternative 2**: Trade-offs of this approach

## Related Concepts
- Link to related topic 1
- Link to related topic 2

## Further Reading
- [Resource 1](url)
- [Resource 2](url)
```

## Explanation Levels

### Beginner
- Simple vocabulary
- More analogies
- Step-by-step detail
- Avoid jargon
- More code comments

### Intermediate
- Assume basic knowledge
- Focus on patterns
- Discuss trade-offs
- Include edge cases

### Advanced
- Technical depth
- Performance implications
- Implementation details
- Comparison with alternatives

## Example Explanations

### Explaining Decorators
```markdown
## Overview
A decorator is a function that wraps another function to extend its behavior
without modifying the original code.

## How It Works
```python
@log_calls
def greet(name):
    return f"Hello, {name}"
```

Is equivalent to:
```python
def greet(name):
    return f"Hello, {name}"

greet = log_calls(greet)  # Wrapping happens here
```

The `@` syntax is just syntactic sugar for this wrapping pattern.

### Step-by-Step Execution
1. Python sees `@log_calls` above `greet`
2. Python defines `greet` as normal
3. Python calls `log_calls(greet)`
4. The result replaces `greet`
5. When you call `greet("World")`, you're calling the wrapped version
```

### Explaining Async/Await
```markdown
## Overview
`async/await` lets you write non-blocking code that looks synchronous.

## The Problem
```python
# Blocking - waits doing nothing
data1 = fetch_from_api()  # 2 seconds
data2 = fetch_from_db()   # 2 seconds
# Total: 4 seconds
```

## The Solution
```python
# Non-blocking - runs concurrently
data1, data2 = await asyncio.gather(
    fetch_from_api(),  # 2 seconds
    fetch_from_db()    # 2 seconds
)
# Total: ~2 seconds
```

While waiting for I/O, Python can do other work.
```

## Instructions for Claude

When /explain is invoked:

1. **Identify target** - Code, function, or concept
2. **Determine level** - Beginner, intermediate, advanced
3. **Read context** - Surrounding code, usage
4. **Structure explanation** - Overview → details → examples
5. **Use analogies** - For complex concepts
6. **Show execution** - Step-by-step flow
7. **Include examples** - Practical usage
8. **Note pitfalls** - Common mistakes
9. **Suggest alternatives** - When relevant
