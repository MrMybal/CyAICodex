---
id: welcome
title: Welcome & how it works
description: Understand the shared library, its Windows server and connected AI clients.
section: Start here
order: 0
revision: 2
---


## Your shared library {#content}


CyAICodex keeps reusable instructions (Skills) and image references in one local library. Edit them yourself, ask the integrated assistant for help, and let connected AI clients consult the same published resources.

## One library, multiple clients {#diagram-1}

```diagram
{"type": "flow", "title": "One library, multiple clients", "nodes": [{"id": "n0", "label": "You & the browser", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "CyAICodex on Windows", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "Your AI clients", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **You & the browser** — Create, organize and review resources.
- **CyAICodex on Windows** — Local library, MCP server and notification-area icon.
- **Your AI clients** — Codex, Claude, OpenCode or another MCP client.

The browser is the interface. The Windows process runs the server. Closing the browser tab leaves the server available while the PC is awake. External AI clients connect through MCP; the integrated assistant is a separate way to draft content.

```callout
{"type": "tip", "title": "Remember", "body": "This manual, screenshots and diagrams are bundled with the application. Reading them needs no Internet, AI account or API key. External providers, GitHub downloads and online references require their respective services."}
```

Use the chapter list or search, which ignores accents. The manual follows the interface language; English is the default and French is available. Screenshots contain sample data.
