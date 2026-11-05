---
id: windows
title: Windows startup and daily use
description: Startup occurs after user sign-in, not before login. The PC must be awake. Closing the browser does not stop the server; sleep and shutdown make it unavailable.
section: User guide
order: 12
revision: 1
---

## Windows startup and daily use {#content}


1. In Connections > Server availability, enable Start with Windows, or use the same setting in the tray menu.
2. On the next Windows sign-in, CyAICodex starts in the background without opening the browser. Reopen it from the tray icon.
3. To stop it, choose Quit and stop server in the tray. Clients lose access until the server starts again.

Startup occurs after user sign-in, not before login. The PC must be awake. Closing the browser does not stop the server; sleep and shutdown make it unavailable.

If a copied URL asks you to reopen from the icon, use the tray icon or application shortcut. It establishes the protected administration session. Do not share its temporary launch link.

```callout
{"type": "tip", "title": "Remember", "body": "Keep _internal next to the executable. The application and MCP use these installed components without unpacking a new Temp copy for every connection."}
```
