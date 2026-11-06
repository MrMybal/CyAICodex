---
id: providers
title: Provider and connector reference
description: Choose among local clients, local models and API providers.
section: Assistant
order: 11
revision: 2
parent: assistant
---


## Choose your provider {#content}


Install the provider’s client or start its server first. Custom executable paths in Settings can override detection. Checking availability, loading model names and testing a response are distinct actions.

| Provider | Requirement / setup | Images |
| --- | --- | --- |
| Codex | Local Codex client; check account and sign in through Connections. | Model-dependent |
| Claude Code | Local Claude Code client and native account login. | Model-dependent |
| OpenCode | Local OpenCode with configured provider; model format provider/model. | Model-dependent |
| Ollama | Local server, default http://127.0.0.1:11434; install a model separately. | Vision model required |
| OpenAI API | Separate API key and exact model identifier. | Model-dependent |
| Claude API | Separate Anthropic API key and exact model identifier. | Model-dependent |
| Antigravity | Detected agy CLI and its signed-in account. | No |
| Command Code | Detected cmdc / command-code CLI and account. | No |
| CodeBuddy | Detected codebuddy / cbc CLI and account. | No |
| OpenRouter | OpenRouter API key and model identifier. | Model-dependent |
| LM Studio | Start local server; default http://127.0.0.1:1234/v1. | Model-dependent |

## Additional connectors {#additional-connectors}

1. In Settings > Additional connectors, save the client path or server address and credentials as applicable.
2. Check, then Load models where supported. Choose a returned model or enter a supported identifier.
3. Optionally Test a response. This sends a small control message, may consume quota, and does not send the library’s Skills.
4. Select the same provider/model in Assistant for your real request.

Model catalogs and account entitlements can change. Availability does not prove access to every model. These buttons do not install models. LM Studio requires a local HTTP address ending in /v1; Ollama also requires a local address.

Antigravity and Command Code use native plan modes and integrations; CyAICodex does not relay approval prompts. CodeBuddy disables tools in this adapter. Do not assume all CLI adapters have identical execution capabilities.
