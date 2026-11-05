---
id: manual-setup
title: Other clients and AI setup guides
description: Under Information to share with another AI, download an English or French Markdown guide and attach it to the conversation. A connected AI can call get_setup_guide(client, language). Claude Desktop and Claude Code are distinct clients; automatic setup covers Codex, Claude Desktop and OpenCode.
section: User guide
order: 8
revision: 1
---

## Other clients and AI setup guides {#content}


1. Create a named connection in Connections with the required scope and rights.
2. Copy its generated configuration while the token is visible. Choose your client’s format and follow its MCP settings.
3. For Streamable HTTP, use the local /mcp address and Bearer token with the server running. For stdio, use the generated executable command and arguments.
4. Reconnect the client and run a real MCP test. A browser opening /mcp is not a protocol test.

Under Information to share with another AI, download an English or French Markdown guide and attach it to the conversation. A connected AI can call get_setup_guide(client, language). Claude Desktop and Claude Code are distinct clients; automatic setup covers Codex, Claude Desktop and OpenCode.

Local discovery uses /mcp-info and the guide /mcp-guide. Neither contains tokens or library content. Markdown describes the steps; a user or authorized capable agent still has to configure the client.

```text
At the start of each task, call get_context, then search_skills and get_skill for applicable practices. Respect this connection’s scope. Create or update a skill only when I ask; use expected_version for updates.
```

```callout
{"type": "tip", "title": "Remember", "body": "A cloud AI cannot directly reach this PC’s localhost. Use a local client or compatible local execution environment; do not expose the server to the Internet as a shortcut."}
```
