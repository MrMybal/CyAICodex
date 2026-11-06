---
id: mcp
title: Connect Codex, Claude Desktop or OpenCode
description: Connect a supported client to your local MCP library.
section: Connections
order: 7
revision: 2
---


## Configure and test a connection {#content}


1. Start CyAICodex and open Connections > Configure and test.
2. Choose token access, or existing local token-free access if deliberately enabled. Select scope, Include global and write rights where available.
3. On the target client’s card, click Configure and test. Recognized configurations are backed up; other servers are preserved. Invalid files and unrelated same-name entries are not overwritten.
4. Reconnect CyAICodex in the target client or restart that client. An open client may retain an older tool list.
5. Use Test only, then ask the AI itself for get_context, search_skills and get_skill to verify what it actually reads.

## MCP connection stages {#diagram-1}

```diagram
{"type": "flow", "title": "MCP connection stages", "nodes": [{"id": "n0", "label": "Server running", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "Client configured", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "MCP connection tested", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **Server running** — CyAICodex answers locally.
- **Client configured** — The client has a CyAICodex entry.
- **MCP connection tested** — Initialize, tools/list and get_context completed.

The same CyAICodex.exe handles the interface and --mcp-stdio. Stdio clients can start the shared server on demand. Closing a client does not quit the independent tray server. A separate bridge executable is unnecessary.

```callout
{"type": "tip", "title": "Remember", "body": "Access to the library does not connect an assistant account. MCP setup and the integrated assistant’s provider login are separate tasks."}
```
