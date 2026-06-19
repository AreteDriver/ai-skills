# Hooks Designer Response
## Example Output
```
User Request
     │
     ▼
Claude decides to use a tool
     │
     ▼
┌─────────────────┐
│  PreToolUse     │──▶ Hook fires BEFORE tool executes
│  (Gate/Block)   │    Exit 0 = proceed, Exit 2 = block
└────────┬────────┘
         │ (if allowed)
         ▼
┌─────────────────┐
│  Tool Executes  │──▶ Bash, Write, Edit, etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostToolUse    │──▶ Hook fires AFTER tool completes
│  (Log/Validate) │    Can log, validate output, trigger actions
└─────────────────┘
```
