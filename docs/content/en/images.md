---
id: images
title: Image references and preservation rules
description: Published images follow the same context/write rules as Skills. get_image supplies metadata and the local original-file path for clients on this PC; view_image supplies a smaller preview. A PC file path is not a cloud download link.
section: User guide
order: 6
revision: 1
---

## Image references and preservation rules {#content}


1. Open Image resources > Import an image and select a still PNG, JPEG or WebP.
2. Describe it, specifying what to preserve, changes to avoid, allowed usage and source. Add category, tags, scope and status.
3. Save and inspect transparency on the preview checkerboard. Download original returns the imported file.
4. Edit instructions on the existing resource; import a visual variant as a new resource. Use with assistant selects the reference for the next request.

| Limit | Value |
| --- | --- |
| File size | 20 MiB maximum. |
| Dimensions | 8192 pixels per side and 25 million pixels maximum. |
| Preview | PNG, up to 1024 pixels. |
| Original | Stored unchanged with SHA-256, dimensions and format metadata. |

Published images follow the same context/write rules as Skills. get_image supplies metadata and the local original-file path for clients on this PC; view_image supplies a smaller preview. A PC file path is not a cloud download link.

```callout
{"type": "tip", "title": "Remember", "body": "CyAICodex stores references and instructions. It does not generate or edit image pixels. Do not replace the original with a screenshot of its preview."}
```
