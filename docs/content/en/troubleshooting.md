---
id: troubleshooting
title: Troubleshooting
description: The rotating log is cyaicodex.log in the application data folder. Installation writes installation.log beside that folder. Earlier releases may use methodes.log. Share only the relevant redacted error and app version, never the whole library, credentials or tokens.
section: User guide
order: 16
revision: 1
---

## Troubleshooting {#content}


| Symptom | What to check |
| --- | --- |
| Page unavailable | Start CyAICodex, check the tray and that the PC is awake. Default port 8765 may be occupied by another app. |
| Reopen from icon requested | Use the tray icon or shortcut to establish the administration session. Do not share launch links. |
| Configured, but tools missing | Reconnect MCP or restart the AI client, then Test only. Saved configuration is not proof the client reloaded. |
| Missing/revoked token | Reconfigure the intended connection; do not paste tokens in support chats. |
| Missing Skill/image | Check Published state, scope, Include global, search/category filters and get_context. |
| Save conflict | Reload and compare edits; do not overwrite blindly. |
| Local client not detected | Check installation and native login, then set its executable path. Desktop and CLI can be separate. |
| Ollama models empty | Start Ollama and install a model separately, then Check and select it. |
| Image refused | Check adapter/model vision support, file format and size limits. |
| Private GitHub update fails | Check local Git access or the limited repository token, network and release availability. |
| No launch before Windows sign-in | This is a user sign-in startup setting, not a pre-login system service. |
| Manual image missing | Keep _internal/help intact and repair/reinstall the app; all exported CyDoc files must stay together. |

The rotating log is cyaicodex.log in the application data folder. Installation writes installation.log beside that folder. Earlier releases may use methodes.log. Share only the relevant redacted error and app version, never the whole library, credentials or tokens.

```callout
{"type": "tip", "title": "Remember", "body": "Keep data and backups after startup/update failures. Diagnose first; do not delete your library to fix a connection issue."}
```
