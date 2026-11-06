---
id: permissions
title: Permissions, tokens and privacy
description: Choose read or write access, manage tokens and understand privacy.
section: Connections
order: 9
revision: 2
parent: mcp
---


## Choose the access level {#content}


| Control | Effect |
| --- | --- |
| Read only | Read published in-scope resources; no creation or update. |
| Write access | Create/update accessible resources, globals included when enabled. |
| Revoke | Invalidate this connection’s token. |
| Local access without token | Let local processes use the configured scope and rights without a Bearer token. |
| Default write setting | Preselect writes for new token connections; existing ones do not change. |

Change an existing connection’s write checkbox in Connections. Tokens are shown once at creation; only their hash is kept in the library. Revocation requires configuring new access. Never paste secrets into chats, screenshots or public support reports.

Settings > MCP permissions defines the token-free context, global inclusion and write rights. It does not remove project scope checks or separate administration protection. AI-client approval prompts are managed in that client, not by this toggle.

```callout
{"type": "tip", "title": "Remember", "body": "Local storage does not mean assistant requests stay local. Sending a message sends conversation and selected references to the chosen provider. Ollama or LM Studio can run locally; cloud providers receive requests under their own policies."}
```
