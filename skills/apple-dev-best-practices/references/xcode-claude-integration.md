# Xcode + Claude Code Integration

## Table of Contents
- XcodeBuildMCP Setup
- CLAUDE.md for iOS Projects
- Claude Code Hooks for Swift
- Sandbox Mode for Safe Development
- Slash Commands for iOS Workflows
- Xcode 26+ Native Claude Integration

---

## XcodeBuildMCP Setup

XcodeBuildMCP connects Claude Code to Xcode for building, testing, and running apps.

### Installation

```bash
# Add XcodeBuildMCP to Claude Code
claude mcp add --transport stdio XcodeBuildMCP \
  --env INCREMENTAL_BUILDS_ENABLED=true \
  --env XCODEBUILDMCP_DYNAMIC_TOOLS=true \
  -- npx -y xcodebuildmcp@latest
```

### Project Config (`.mcp.json` — committed to git)

```json
{
  "mcpServers": {
    "XcodeBuildMCP": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest"],
      "env": {
        "INCREMENTAL_BUILDS_ENABLED": "true",
        "XCODEBUILDMCP_SENTRY_DISABLED": "true",
        "XCODEBUILDMCP_DYNAMIC_TOOLS": "true"
      }
    }
  }
}
```

### Available Tools

| Tool | Purpose |
|---|---|
| `mcp__xcodebuildmcp__build_sim_name_proj` | Build for simulator |
| `mcp__xcodebuildmcp__test_sim_name_proj` | Run tests on simulator |
| `mcp__xcodebuildmcp__clean` | Clean build products |
| `mcp__xcodebuildmcp__list_simulators` | List available simulators |
| `mcp__xcodebuildmcp__boot_simulator` | Boot a simulator |
| `mcp__xcodebuildmcp__install_app` | Install app on sim |
| `mcp__xcodebuildmcp__launch_app` | Launch installed app |
| `mcp__xcodebuildmcp__capture_logs` | Runtime logs |
| `mcp__xcodebuildmcp__screenshot` | Capture sim screenshot |
| `mcp__xcodebuildmcp__swift_package_test` | Test Swift packages |

## CLAUDE.md Template

Place in project root. Claude loads this at session start:

```markdown
# Project: [AppName]

## Quick Reference
- Platform: iOS 17+ / macOS 14+
- Language: Swift 6.0
- UI: SwiftUI
- Architecture: MVVM with @Observable
- Persistence: SwiftData
- Build: mcp__xcodebuildmcp__build_sim_name_proj
- Test: mcp__xcodebuildmcp__test_sim_name_proj

## DO NOT
- Modify .pbxproj files (create files, add to Xcode manually)
- Use force unwrapping without justification
- Use deprecated NavigationView
- Put network calls in view body
- Use @StateObject — use @State + @Observable instead

## Project-Specific Patterns
[Document your actual patterns here as you build them]
```

**Critical rule from real-world experience:** Never let Claude modify `.pbxproj` files. One corruption wastes hours. Create files with Claude, add to Xcode manually.

## Hooks for Swift

### Auto-lint on file save (`.claude/settings.json`)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read f; [[ \"$f\" == *.swift ]] && swiftlint lint --path \"$f\" --quiet; }"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json,sys; d=json.load(sys.stdin); p=d.get('tool_input',{}).get('file_path',''); sys.exit(2 if '.pbxproj' in p or '.env' in p or 'Secrets.swift' in p else 0)\""
          }
        ]
      }
    ]
  }
}
```

This auto-lints every Swift file Claude writes and **blocks edits to .pbxproj, .env, and Secrets.swift**.

## Sandbox Modes

Graduated permission levels for learning safely:

### Level 1: Read + Build Only (Safest)
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "mcp__xcodebuildmcp__*"],
    "deny": ["Write", "Edit"]
  }
}
```

### Level 2: + Docs Writing
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Write(docs/*)", "Edit(docs/*)", "mcp__xcodebuildmcp__*"],
    "deny": ["Write(*.swift)", "Edit(*.swift)"]
  }
}
```

### Level 3: + Test Files
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Write(*Tests/*.swift)", "Edit(*Tests/*.swift)", "mcp__xcodebuildmcp__*"],
    "deny": ["Write(*/App/*)", "Write(*/Features/*)"]
  }
}
```

### Level 4: Full Development
```json
{
  "permissions": {
    "allow": ["Read", "Write", "Edit", "mcp__xcodebuildmcp__*", "Bash(swift *)", "Bash(git *)"],
    "deny": ["Write(.env*)", "Write(**/Secrets.swift)", "Bash(rm -rf *)"]
  }
}
```

## Xcode 26+ Native Claude Integration

As of Xcode 26.3, Apple ships native Claude Agent SDK support:
- Claude can capture Xcode Previews for visual verification
- MCP protocol for CLI integration (Claude Code can connect)
- Enabled in Xcode > Settings > Intelligence > Claude

This means Claude can see what the UI looks like and iterate on design — particularly powerful for SwiftUI views where visual output is what matters.
