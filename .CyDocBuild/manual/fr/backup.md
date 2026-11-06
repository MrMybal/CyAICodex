---
id: backup
title: Export, sauvegarde complète et restauration
description: Choisir un export JSON ou sauvegarder et restaurer toute la bibliothèque.
section: Au quotidien
order: 14
revision: 2
sourceRevision: 2
parent: windows
---


## Protéger votre bibliothèque {#content}


## Choisir la sauvegarde adaptée {#diagram-1}

```diagram
{"type": "flow", "title": "Choisir la sauvegarde adaptée", "nodes": [{"id": "need", "label": "À conserver ?", "x": 0, "y": 95, "width": 180}, {"id": "export", "label": "Export JSON des Skills", "x": 240, "y": 0, "width": 240}, {"id": "backup", "label": "Copie complète de data", "x": 240, "y": 190, "width": 240}, {"id": "restore", "label": "Restaurer toute la copie", "x": 560, "y": 190, "width": 240}], "edges": [{"from": "need", "to": "export", "label": "Fiches seules"}, {"from": "need", "to": "backup", "label": "Toutes les données"}, {"from": "backup", "to": "restore"}]}
```

- **Exporter** — JSON : Skills et classement à consulter ou partager.
- **Tout sauvegarder** — Arrêter CyAICodex et copier tout data.
- **Restaurer** — Arrêter, préserver data courant et restaurer une copie complète.

Exporter la bibliothèque, en bas de Bibliothèque, télécharge skills.json : fiches et classement, sans clés ni jetons. Ce n’est pas une sauvegarde complète des images, réglages, identifiants et historiques. Cette version n’a pas de bouton général d’import JSON.

## Sauvegarde complète {#full-backup}

1. Quittez et arrêtez le serveur de l’icône. Fermez ou déconnectez les clients MCP pour éviter sa relance immédiate.
2. Copiez tout %LOCALAPPDATA%\CyAICodex\data vers votre sauvegarde. Les versions portables ou sources utilisent data à côté de l’application sauf option --data-dir.
3. Gardez ensemble originaux, base et fichiers SQLite associés. Protégez la copie : elle peut contenir des consignes privées et informations de connexion.

## Restaurer {#restore}

1. Arrêtez à nouveau serveur et clients. Conservez le dossier data courant séparément pour revenir en arrière.
2. Restaurez la copie complète à l’emplacement prévu et rouvrez CyAICodex.
3. Vérifiez des Skills, originaux d’images, historique et connexions.

```callout
{"type": "tip", "title": "À retenir", "body": "Les identifiants DPAPI sont liés au compte et profil Windows d’origine. Un autre compte ou PC peut imposer une nouvelle saisie. Les anciennes bases peuvent utiliser methodes.sqlite3 ; les nouvelles skills.sqlite3. Ne renommez ni ne fusionnez des bases ouvertes."}
```
