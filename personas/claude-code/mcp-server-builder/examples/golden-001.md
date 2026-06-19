# Mcp Server Builder Response
## Example Output
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
