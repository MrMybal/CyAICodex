---
id: assistant
title: Use the integrated assistant
description: Draft reusable Skills with a provider and selected references.
section: Assistant
order: 10
revision: 2
---


## Start a conversation {#content}


1. In Connections or Settings, verify the local client or save the provider API credentials. Use its native login when offered.
2. In Assistant, select provider and model, or leave the model blank where the provider supports a default.
3. Optionally select a Skill and an image reference. Describe the reusable procedure or preservation instructions you want, then send.
4. Review the answer. Turn into a skill opens a draft editor: choose scope, category and status, then save. Answer text alone does not save a record.

The conversation and selected references are resent with the request. Clear the conversation to start again. The assistant tab is not a guaranteed resumable native provider session; save important work as a Skill or another document.

Image support depends on both adapter and model. Choose a vision-capable model. The assistant analyzes references and drafts text; it does not generate images.

```callout
{"type": "tip", "title": "Remember", "body": "Claude Desktop MCP access lets Claude read the library. To chat inside CyAICodex with a Claude account, use supported Claude Code access or a separate Anthropic API key. Consumer subscriptions are not API credentials."}
```
