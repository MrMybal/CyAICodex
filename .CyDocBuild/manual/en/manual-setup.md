---
id: manual-setup
title: Configure another MCP client
description: Configure another MCP client and obtain client-specific setup help.
section: Connections
order: 8
revision: 3
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

## Install the portable Agent Skill {#agent-skill}

CyAICodex provides one standard `cyaicodex/SKILL.md` for Codex, Claude Code and compatible Agent Skills hosts. It teaches the client when and how to consult this MCP library. It does not install the application, connect MCP or copy your personal records into the client.

[Download the Skill ZIP](https://mrmybal.github.io/CyAICodex/AgentSkills/CyAICodex-Skill.zip). Source builds also place the ZIP in `Documentation/AgentSkills/CyAICodex-Skill.zip`; existing installed versions can use the separate download.

- **Codex:** extract the archive and copy its `cyaicodex` folder into `~/.agents/skills/` (all projects) or your project's `.agents/skills/`. A legacy/custom client that reads `~/.codex/skills/` can use the same folder there instead.
- **Claude Code:** copy the same folder into `~/.claude/skills/` or your project's `.claude/skills/`.
- **Claude app / claude.ai:** upload and enable the ZIP in Customize > Skills if your plan/workspace supports custom Skills. A cloud environment still cannot reach your PC's localhost directly.

Refresh the client's skills or start a new session, then invoke `$cyaicodex` in Codex or `/cyaicodex` in Claude Code. Verify an actual `get_context` call. Automatic skill selection depends on the client and task; add a standing instruction if consultation is required for every task.

From a source checkout, PowerShell 7 can install for both local clients with `pwsh -File .\integrations\skills\Install-Skill.ps1 -Client all`. Existing customizations are preserved unless an update is explicitly requested. The shared instructions are in English; the agent answers in your language. [Detailed installation instructions](https://github.com/MrMybal/CyAICodex/tree/main/integrations/skills).
