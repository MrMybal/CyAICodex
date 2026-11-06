---
id: backup
title: Export, full backup and restore
description: Choose a JSON export or back up and restore the complete library.
section: Daily use
order: 14
revision: 2
parent: windows
---


## Protect your library {#content}


## Choose the backup you need {#diagram-1}

```diagram
{"type": "flow", "title": "Choose the backup you need", "nodes": [{"id": "need", "label": "What to keep?", "x": 0, "y": 95, "width": 180}, {"id": "export", "label": "JSON Skill export", "x": 240, "y": 0, "width": 240}, {"id": "backup", "label": "Complete data backup", "x": 240, "y": 190, "width": 240}, {"id": "restore", "label": "Restore the full copy", "x": 560, "y": 190, "width": 240}], "edges": [{"from": "need", "to": "export", "label": "Skills only"}, {"from": "need", "to": "backup", "label": "All data"}, {"from": "backup", "to": "restore"}]}
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
