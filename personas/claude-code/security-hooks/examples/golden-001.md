# Security Hooks Response
## Example Output
```
PreToolUse hook receives stdin JSON
         │
         ▼
  ┌─────────────────┐
  │ Parse tool_name  │
  │ + tool_input     │
  └────────┬────────┘
           │
     ┌─────┴─────┐
     │            │
     ▼            ▼
  Pattern      No match
  matches?     → exit 0 (allow)
     │
     ▼
  ┌──────────┐
  │ Severity │
  └────┬─────┘
       │
  ┌────┴────┐
  │         │
  ▼         ▼
 HARD      SOFT
 BLOCK     GATE
  │         │
  ▼         ▼
exit 2    JSON output:
+stderr   permissionDecision: "ask"
(deny)    (user confirms)
```
