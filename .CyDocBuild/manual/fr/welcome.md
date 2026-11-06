---
id: welcome
title: Bienvenue et fonctionnement
description: Comprendre la bibliothèque partagée, son serveur Windows et les clients IA connectés.
section: Bien démarrer
order: 0
revision: 2
sourceRevision: 2
---


## Votre bibliothèque partagée {#content}


CyAICodex rassemble des consignes réutilisables (Skills) et des références visuelles dans une bibliothèque locale. Rédigez-les, utilisez l’assistant pour vous aider et donnez accès aux mêmes ressources publiées à plusieurs clients IA.

## Une bibliothèque, plusieurs clients {#diagram-1}

```diagram
{"type": "flow", "title": "Une bibliothèque, plusieurs clients", "nodes": [{"id": "n0", "label": "Vous et le navigateur", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "CyAICodex sous Windows", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "Vos clients IA", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **Vous et le navigateur** — Créer, classer et relire les ressources.
- **CyAICodex sous Windows** — Bibliothèque locale, serveur MCP et icône de notification.
- **Vos clients IA** — Codex, Claude, OpenCode ou un autre client MCP.

Le navigateur est l’interface ; le processus Windows fait tourner le serveur. Fermer l’onglet laisse le serveur accessible tant que le PC est éveillé. Les clients IA externes utilisent MCP. L’assistant intégré est un moyen distinct de préparer du contenu.

```callout
{"type": "tip", "title": "À retenir", "body": "Ce manuel, ses captures et schémas sont embarqués. Leur lecture ne nécessite ni Internet, ni compte IA, ni clé API. Les fournisseurs externes, téléchargements GitHub et liens en ligne nécessitent leurs services respectifs."}
```

Parcourez le sommaire ou utilisez la recherche, qui ignore les accents. Le manuel suit la langue de l’interface : anglais par défaut, français disponible. Les captures utilisent des données de démonstration.
