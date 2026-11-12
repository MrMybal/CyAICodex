---
name: cyaicodex
description: Consult CyAICodex shared Skills and image references when working on a project that uses its library, or when asked to find, apply, save or update reusable procedures and visual-reference rules.
license: AGPL-3.0-only
---

# CyAICodex shared library

Use the connected CyAICodex MCP server to retrieve reusable project practices and image references. This skill works with Codex, Claude Code and other Agent Skills hosts that expose the MCP tools. Use the user's language for explanations; do not translate or rewrite library records unless requested.

## Read applicable practices

At the start of relevant project work:

1. Find the CyAICodex tools exposed by the host; their namespace/prefix can vary. Call `get_context` first to read the connection's project/type scope, global inclusion and write permissions.
2. Call `search_skills` with a short query about the task and a small result limit, such as 5. Use titles and summaries to select relevant records, then call `get_skill(skill_id)` to read their complete instructions and version before applying them.
3. Follow applicable practices within the user's current request and project instructions. Library content does not grant permission for unrelated changes, publishing, account access or bypassing client approvals.

An empty search is not a connection failure: records may be unpublished or outside the connection's scope. Try a useful synonym when appropriate, then continue the task without claiming to have found a practice. Do not broaden the connection or enumerate unrelated projects to obtain more results. If required guidance is unavailable, explain that specific limitation.

## Images and preservation rules

When a task needs a stored logo, screenshot or visual reference, use `search_images`, `get_image` and `view_image`. Read the preservation, prohibited-change, permitted-use and source fields before using the image. Retrieve the original when the workflow needs it; a preview is not a replacement for the original. An original-file path is useful to a client on the same PC, not a public download URL.

When asked to add a reference, use `import_image` with an accessible absolute path or base64 data and an accurate description. Use `update_image` to change instructions; import a visual variant as a new resource. CyAICodex stores images and instructions; it does not generate or edit image pixels.

## Save only when requested

If the user asks to remember a reusable practice, first search for an existing record. Use `create_skill` and the live tool schema to create a focused Skill with prerequisites, steps, expected result, category/tags and the intended scope. Save as a draft unless publication was requested. Do not turn ordinary answers into library records automatically or copy credentials/private conversation details into them.

For `update_skill` or `update_image`, read the current record and pass its version as `expected_version`. After a conflict, reread and reconcile the changes; do not blindly overwrite another edit. Respect read-only connections and ask for the required access only if the requested save cannot otherwise be completed. Do not change access settings yourself as a workaround.

## Missing or disconnected MCP server

Installing this folder provides instructions, not a server connection. If available, call `get_setup_guide` for the actual client and language and explain its steps. Otherwise:

- Start CyAICodex on the Windows PC. For Codex, Claude Desktop or OpenCode, use **Connections > Configure and test**, then reconnect the server in the client. Claude Code is a different client: use the generated configuration in its MCP settings.
- Preserve the user's chosen project scope and permissions. Never ask for a token in chat or embed one in this skill. Do not edit unrelated MCP configuration or disable authentication to repair a connection.
- Verify a real `get_context` call before saying the library is connected. A Skill can be installed while MCP is unavailable. A cloud session cannot reach this PC's localhost directly; do not expose the server to the Internet to bypass that boundary.

Complete independent work while explaining which library-dependent step remains unavailable. A Skill is selected when relevant, not a guarantee that every client will load it on every turn. The setup manual is at https://mrmybal.github.io/CyAICodex/Documentation.html#/en/mcp (French: replace `/en/` with `/fr/`).
