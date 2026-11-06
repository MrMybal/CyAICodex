---
id: tools
title: MCP tools and compatibility
description: MCP transports, tool contracts, resources and compatibility names.
section: Reference / Public API
order: 17
revision: 2
---


## MCP operations {#content}


| Tool | Use |
| --- | --- |
| get_context | Read scope, global inclusion and write permissions. |
| search_skills / get_skill | Find published Skills and read full content/version. |
| create_skill / update_skill | Write when authorized; updates require expected_version. |
| search_images / get_image / view_image | Find images, read their rules and view a preview. |
| import_image | Add a local absolute file path or base64 image and its description. |
| update_image | Update rules with expected_version; original pixels remain intact. |
| get_setup_guide | Client setup guidance in English or French. |

Legacy search_methods, get_method, create_method and update_method remain supported. skills://context and methodes://context expose scope. apply_skills is the current prompt; appliquer_methodes remains compatible.

Transport is Streamable HTTP on the local /mcp endpoint or the generated stdio command. Standard port: 8765. Source/CLI options include --port, --data-dir, --no-open, --headless, --mcp-stdio and --stop for deliberately managed custom instances.


Tools are MCP protocol operations. Their Python-shaped signatures describe the wire arguments; they are not importable module functions. See the child pages for parameters and return values, and [data contracts](doc:data-contracts#content) for Skill and image payloads.

Read scope first, search concise results, then fetch the selected record. After a version conflict, fetch it again and reconcile the changes before updating. Missing, unpublished or inaccessible records are not exposed.

## Short call example {#example}

On an established MCP session, the arguments for a `tools/call` request can be:

```json
{"name":"search_skills","arguments":{"query":"github","limit":5}}
```


## Compatibility names {#compatibility}

Older clients can continue to call the following tools. Parameters and results match the current Skill operations; `method_id` corresponds to `skill_id`, and `method` to `skill`.

```python
search_methods(query: str = '', category: str = '', limit: int = 10, offset: int = 0) -> dict[str, Any]
get_method(method_id: str) -> dict[str, Any]
create_method(method: Method) -> dict[str, Any]
update_method(method_id: str, expected_version: int, method: Method) -> dict[str, Any]
```

## Resources and prompts {#resources}

`skills://context` and `methodes://context` return the same connection context as JSON text. The `apply_skills(task: str)` prompt returns task-specific instruction text; `appliquer_methodes(task: str)` is its older French counterpart. These prompts do not execute tools or edit records by themselves.

## Public HTTP discovery {#http-discovery}

These read-only routes belong to the local FastAPI application in `skills.server`. They need the server running and do not require a connection token. They return no personal library content. Administration routes under `/api` are intended for the authenticated application interface.

| Request | Parameters | Response |
| --- | --- | --- |
| `GET /health` | None | JSON: `app`, `status`, `version`, `packaged`, `tray`. The compatibility `app` identifier remains `methodes`; `status` is `ok`. |
| `GET /mcp-info` | None | JSON: name/version, transport/URL, token requirement, supported clients, workflow and guide links. Some legacy explanatory strings remain French. |
| `GET /mcp-guide` | `client=all`, `lang=en` | Markdown attachment for the chosen client and language. Client values match `get_setup_guide`; language is `en` or `fr`. Invalid query values return HTTP 422. |

```bash
curl http://127.0.0.1:8765/health
```

Change the port when using a deliberately configured custom instance. Requesting `/mcp` in a browser does not establish an MCP session; follow your client’s [connection steps](doc:mcp#content).
