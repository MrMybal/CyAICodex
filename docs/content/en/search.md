---
id: search
title: Find the right resource
description: SQLite full-text search normalizes accents, matches word prefixes and ranks titles, summaries and tags highly. Several words narrow results. This is not semantic/vector similarity search.
section: User guide
order: 3
revision: 1
---

## Find the right resource {#content}


1. Enter a few meaningful words in Library search: title fragments, tags or terms from the summary/content.
2. Combine search with category, context and status filters. Toggle Include global skills when working within a project.
3. Browse with Previous / Next. Clear text and category filters if an expected record is missing.

SQLite full-text search normalizes accents, matches word prefixes and ranks titles, summaries and tags highly. Several words narrow results. This is not semantic/vector similarity search.

The interface can list drafts and archives via the status filter. MCP always returns published resources in the connection’s scope, with short excerpts; get_skill retrieves the complete record.

```callout
{"type": "tip", "title": "Remember", "body": "An empty AI search can reflect scope, publication state or search terms. Check get_context before assuming the server is disconnected."}
```
