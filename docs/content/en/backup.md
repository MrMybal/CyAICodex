---
id: backup
title: Export, full backup and restore
description: Export library at the bottom of Library downloads skills.json: Skill records and classification without account keys or tokens. It is not a full backup of images, settings, credentials and history. This version has no general JSON import button.
section: User guide
order: 14
revision: 1
---

## Export, full backup and restore {#content}


## Choose the backup you need {#diagram-1}

```diagram
{"type": "flow", "title": "Choose the backup you need", "nodes": [{"id": "n0", "label": "Export library", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "Full backup", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "Restore", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **Export library** — JSON: Skills and classification to inspect or share.
- **Full backup** — Stop CyAICodex and copy the entire data folder.
- **Restore** — Stop, preserve current data, restore a complete backup.

Export library at the bottom of Library downloads skills.json: Skill records and classification without account keys or tokens. It is not a full backup of images, settings, credentials and history. This version has no general JSON import button.

## Full backup {#full-backup}

1. Quit and stop the tray server. Close/disconnect MCP clients so they do not restart it immediately.
2. Copy the entire %LOCALAPPDATA%\CyAICodex\data folder to your backup location. Portable/source copies use data beside the application unless --data-dir overrides it.
3. Keep originals, database and companion SQLite files together. Protect the backup: it can contain private instructions and connection information.

## Restore {#restore}

1. Stop the server and clients again. Keep the current data folder separately as a recovery copy.
2. Restore the complete backup to the intended data location and reopen CyAICodex.
3. Check representative Skills, image originals, history and connections.

```callout
{"type": "tip", "title": "Remember", "body": "DPAPI credentials are tied to the Windows account/profile that encrypted them. Another account/PC may require entering credentials again. Older libraries may use methodes.sqlite3; new ones use skills.sqlite3. Do not rename or merge open databases manually."}
```
