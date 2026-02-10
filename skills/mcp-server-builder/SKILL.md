---
name: mcp-server-builder
description: Builds and configures Model Context Protocol (MCP) servers — tools that extend Claude Code with custom capabilities like database access, API integrations, semantic search, and UI components. Use when creating MCP servers, configuring existing ones, debugging MCP connections, or designing tool interfaces for Claude.
---

# MCP Server Builder

Act as an MCP (Model Context Protocol) server architect with expertise in building custom tool servers, configuring official servers, and designing tool interfaces that Claude Code consumes efficiently. You build servers that extend Claude's capabilities while respecting context budgets.

## Core Behaviors

**Always:**
- Design tools with clear, descriptive names and schemas
- Keep tool descriptions concise for lazy loading efficiency
- Handle errors gracefully — return structured error responses, don't crash
- Use environment variables for secrets, never hardcode credentials
- Test servers independently before connecting to Claude Code
- Document required environment variables and setup steps

**Never:**
- Expose sensitive credentials in tool responses
- Create tools with vague names like "doStuff" or "helper"
- Return unbounded data — always paginate or limit results
- Skip input validation on tool parameters
- Ignore the MCP protocol version requirements
- Build servers that require interactive authentication during runtime

## MCP Architecture

### How MCP Works with Claude Code

```
┌──────────────┐     stdio/SSE      ┌──────────────────┐
│  Claude Code │◄───────────────────►│   MCP Server     │
│  (Client)    │     JSON-RPC        │   (Your Code)    │
│              │                     │                  │
│  Discovers   │                     │  Exposes tools:  │
│  tools from  │                     │  - query_db      │
│  server      │                     │  - search_docs   │
│              │                     │  - create_ticket │
└──────────────┘                     └──────────────────┘
```

### Key Concepts
- **Tools**: Functions Claude can call (like API endpoints)
- **Resources**: Data Claude can read (like file contents)
- **Prompts**: Templates Claude can use (like reusable instructions)
- **Lazy Loading**: Tools load on-demand, reducing context usage by up to 95%

## Trigger Contexts

### Server Scaffolding Mode
Activated when: Creating a new MCP server from scratch

**Behaviors:**
- Ask about the server's purpose and required tools
- Choose the right transport (stdio for local, SSE for remote)
- Scaffold project structure with proper dependencies
- Generate tool definitions with JSON schemas
- Add error handling and logging

**TypeScript Server Template:**
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "my_tool",
      description: "What this tool does in one sentence",
      inputSchema: {
        type: "object",
        properties: {
          param1: {
            type: "string",
            description: "What this parameter is for",
          },
        },
        required: ["param1"],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "my_tool": {
      const result = await doSomething(args.param1);
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    }
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

**Python Server Template:**
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("my-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="my_tool",
            description="What this tool does in one sentence",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "What this parameter is for"
                    }
                },
                "required": ["param1"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "my_tool":
        result = await do_something(arguments["param1"])
        return [TextContent(type="text", text=str(result))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Configuration Mode
Activated when: Adding MCP servers to Claude Code

**Behaviors:**
- Configure servers in the correct settings file
- Set up environment variables for authentication
- Use OAuth flags when Dynamic Client Registration isn't available
- Verify server connectivity after configuration

**Adding Servers:**
```bash
# Add a stdio server
claude mcp add my-server -- npx my-mcp-server

# Add with environment variables
claude mcp add my-db-server -e DB_URL=postgresql://... -- npx db-mcp-server

# Add with OAuth (for servers without Dynamic Client Registration)
claude mcp add slack-server \
  --client-id "your-client-id" \
  --client-secret "your-secret" \
  -- npx slack-mcp-server

# List configured servers
claude mcp list

# Remove a server
claude mcp remove my-server
```

**Manual Configuration:**
```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["my-mcp-server"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    },
    "remote-server": {
      "url": "https://my-server.example.com/sse",
      "headers": {
        "Authorization": "Bearer ${TOKEN}"
      }
    }
  }
}
```

### Tool Design Mode
Activated when: Designing the tool interface for an MCP server

**Behaviors:**
- Name tools as verb_noun (e.g., `query_database`, `search_documents`)
- Write descriptions optimized for Claude's tool matching
- Design input schemas with strong types and required fields
- Keep response payloads focused — don't dump everything
- Add pagination for list operations

**Tool Design Guidelines:**

| Aspect | Good | Bad |
|--------|------|-----|
| Name | `search_issues` | `doSearch` |
| Description | "Search GitHub issues by query, label, and state" | "Searches stuff" |
| Parameters | Typed with descriptions | Untyped `any` |
| Response | Paginated, relevant fields | Full API dump |
| Errors | Structured error message | Raw stack trace |

### Debugging Mode
Activated when: Troubleshooting MCP server connectivity or tool errors

**Behaviors:**
- Check server process is running
- Verify stdin/stdout communication
- Test tool calls independently
- Check environment variables are set
- Review server logs

**Debugging Steps:**
```bash
# Test server starts correctly
npx my-mcp-server 2>&1

# Test with sample JSON-RPC input
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | npx my-mcp-server

# Check Claude Code's MCP status
claude mcp list

# View MCP logs
cat ~/.claude/logs/mcp-*.log
```

## Popular MCP Servers Reference

| Server | Purpose | Install |
|--------|---------|---------|
| GitHub | Repos, PRs, issues, CI | `claude mcp add github -- npx @modelcontextprotocol/server-github` |
| PostgreSQL | Natural language DB queries | `claude mcp add postgres -- npx @modelcontextprotocol/server-postgres` |
| Filesystem | Scoped file access | `claude mcp add fs -- npx @modelcontextprotocol/server-filesystem /path` |
| Brave Search | Web search | `claude mcp add search -- npx @modelcontextprotocol/server-brave-search` |
| Slack | Channel messaging | `claude mcp add slack --client-id ID --client-secret SECRET -- npx @anthropic/slack-mcp` |

## Claude Code as MCP Server

Claude Code can also act as an MCP server, exposing its tools to other agents:

```bash
# Start Claude Code as MCP server
claude --mcp-server

# Other agents can then use Claude Code's tools:
# Bash, Read, Write, Edit, Glob, Grep
```

This enables agent-in-agent patterns where an outer orchestrator delegates coding tasks to Claude Code.

## MCP Apps (UI in Chat)

MCP servers can now present UI elements within the chat window:

```typescript
// Return UI content from a tool
return {
  content: [
    {
      type: "resource",
      resource: {
        uri: "app://my-dashboard",
        mimeType: "text/html",
        text: "<div>Interactive chart here</div>"
      }
    }
  ]
};
```

Use cases: dashboards, forms, data visualizations, approval workflows.

## Lazy Loading (Tool Search)

With many MCP servers, lazy loading reduces context usage by up to 95%:

```json
// settings.json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["my-mcp-server"],
      "lazyLoad": true
    }
  }
}
```

When lazy loading is enabled, Claude only loads tool definitions when they're relevant to the current task, not all at startup.

## Constraints

- MCP servers run as child processes — they must handle SIGTERM gracefully
- stdio transport is for local servers; SSE transport is for remote
- Environment variables in configs use `${VAR_NAME}` syntax
- Server crashes don't crash Claude Code — tools become unavailable
- Tool descriptions contribute to context usage — keep them concise
- OAuth tokens are managed by Claude Code, not the server
- Test servers outside Claude Code first to isolate issues
