---
name: arch
description: Architecture Diagram Generator
---

# /arch - Architecture Diagram Generator

Generate Mermaid architecture diagrams from code analysis.

## Usage
```
/arch [component]        # Diagram specific component
/arch                    # Diagram entire project
/arch --type flowchart   # Specify diagram type
```

## Diagram Types

- `flowchart` - Control flow and decision trees
- `class` - Class relationships and inheritance
- `sequence` - Component interactions over time
- `er` - Entity relationships (database schemas)
- `c4` - C4 model (context, container, component)

## What This Skill Does

1. **Scan Codebase** - Identify modules, classes, functions, dependencies
2. **Map Relationships** - Imports, inheritance, composition, calls
3. **Generate Mermaid** - Create diagram in requested format
4. **Output Markdown** - Ready to paste into docs or GitHub

## Output Format

```markdown
## Architecture: [Component/Project]

### Overview
Brief description of the architecture.

### Diagram

\`\`\`mermaid
flowchart TD
    A[Module A] --> B[Module B]
    B --> C[Module C]
    A --> C
\`\`\`

### Components

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| Module A  | Does X  | None         |
| Module B  | Does Y  | Module A     |

### Key Flows
1. **Flow Name**: A -> B -> C (description)
```

## Instructions for Claude

When /arch is invoked:

1. **Identify scope** - Single component or whole project?
2. **Read code** - Use Glob/Grep/Read to understand structure
3. **Map dependencies** - Imports, function calls, class relationships
4. **Choose diagram type** - Pick most appropriate for the code
5. **Generate Mermaid** - Create valid Mermaid syntax
6. **Add context** - Include component table and key flows
7. **Keep it readable** - Limit nodes to ~15-20 per diagram, split if larger
