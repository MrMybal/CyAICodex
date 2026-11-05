---
id: tools
title: MCP tools and compatibility
description: Legacy search_methods, get_method, create_method and update_method remain supported. skills://context and methodes://context expose scope. apply_skills is the current prompt; appliquer_methodes remains compatible.
section: User guide
order: 17
revision: 1
---

## MCP tools and compatibility {#content}


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

```callout
{"type": "tip", "title": "Remember", "body": "MCP makes resources available, but cannot force a model to consult them. Put get_context → search_skills → get_skill in client instructions. Permissions and context always apply."}
```
