---
id: manual-setup
title: Configure another MCP client
description: Configure another MCP client and obtain client-specific setup help.
section: Connections
order: 8
revision: 2
parent: mcp
---


## Use a generated client configuration {#content}


1. Create a named connection in Connections with the required scope and rights.
2. Copy its generated configuration while the token is visible. Choose your client’s format and follow its MCP settings.
3. For Streamable HTTP, use the local /mcp address and Bearer token with the server running. For stdio, use the generated executable command and arguments.
4. Reconnect the client and run a real MCP test. A browser opening /mcp is not a protocol test.

Under Information to share with another AI, download an English or French Markdown guide and attach it to the conversation. A connected AI can call get_setup_guide(client, language). Claude Desktop and Claude Code are distinct clients; automatic setup covers Codex, Claude Desktop and OpenCode.

Local discovery uses /mcp-info and the guide /mcp-guide. Neither contains tokens or library content. Markdown describes the steps; a user or authorized capable agent still has to configure the client.


```callout
{"type": "tip", "title": "Remember", "body": "A cloud AI cannot directly reach this PC’s localhost. Use a local client or compatible local execution environment; do not expose the server to the Internet as a shortcut."}
```
