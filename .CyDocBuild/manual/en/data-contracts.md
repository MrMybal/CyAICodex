---
id: data-contracts
title: Skill and image data contracts
description: Payload fields, scope rules and versioned record formats.
section: Reference / Public API
parent: tools
order: 220
revision: 1
---

## Shared payload rules {#content}

The MCP tool schemas expose `Method` (the compatibility name of a Skill payload) and `ImageDescription`. Their Python definitions use Pydantic in `skills.store` and `skills.images`. MCP clients pass JSON objects rather than importing these internal classes.

| Field | Type / default | Meaning |
| --- | --- | --- |
| `title` | `str`, required | Nonblank, 1–160 characters. |
| `category` | `str` | 1–80 characters; legacy defaults are `Général` for Skills and `Référence` for images. Pass an explicit label to choose your own language. |
| `tags` | `list[str]`, `[]` | Up to 30, trimmed and deduplicated; at most 60 characters each. |
| `scope` | `global`, `type`, `project`; default `global` | Visibility rule, checked against the connection. |
| `scope_id` | `str`, `""` | Required existing group ID for type/project; cleared for globals. |
| `status` | `published`, `draft`, `archived`; default `published` | MCP reads expose published records only. |

## Skill fields {#skill}

`Method` adds required nonblank `content` (up to 100,000 characters) and optional `summary` (default empty, up to 600). Returned records add `id`, `version`, `created_at` and `updated_at`. Search returns `{items, total}`; its Skill items contain summaries rather than the full content. Read the selected ID to retrieve its content.

```json
{"title":"Review a release","content":"Review the outgoing files before publishing.","category":"Publishing","tags":["github"],"scope":"global","status":"published"}
```

## Image fields {#image}

`ImageDescription` adds required nonblank `description` (up to 30,000 characters), `preserve`, `avoid` and `usage` (default empty, up to 15,000 each), and `source` (default empty, up to 2,000). Returned image records add ID, version, timestamps and original-file metadata such as dimensions, format and SHA-256. `get_image` additionally returns `original_path`; `view_image` returns MCP text/image content blocks.

Image import requires exactly one of `file_path` and `data_base64`. Still PNG, JPEG and WebP are accepted: 20 MiB, 8192 pixels per side and 25 million pixels maximum. An update changes descriptions, never the original pixels. See [image references](doc:images#content).

## Updates and errors {#updates}

Pass the current integer `version` as `expected_version` when updating. A stale version produces a conflict rather than overwriting another edit. Fetch and reconcile the latest record. Writes also require a writable connection and an allowed scope; invalid data, inaccessible records and unsupported images fail without granting extra access.
