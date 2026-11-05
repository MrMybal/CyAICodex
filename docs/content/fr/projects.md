---
id: projects
title: Projets, types et visibilité
description: Une connexion de projet réunit le projet, son type et éventuellement les globaux. Une connexion de type voit ce type et éventuellement les globaux. Sans projet ni type, seuls les globaux peuvent être visibles si inclus. Les autres projets sont exclus.
section: Guide utilisateur
order: 5
revision: 1
sourceRevision: 1
---

## Projets, types et visibilité {#content}


1. Dans Projets & types, créez un type comme Application web puis un projet rattaché.
2. Attribuez chaque Skill ou image à Globale, à ce type ou à ce projet précis.
3. Dans Connexions, choisissez le projet ou type de chaque IA et l’inclusion éventuelle des globaux.

## Une connexion de projet peut lire {#diagram-1}

```diagram
{"type": "flow", "title": "Une connexion de projet peut lire", "nodes": [{"id": "n0", "label": "Skills globaux", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "Skills du type", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "Skills du projet", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **Skills globaux** — Uniquement si Inclure les globaux est activé.
- **Skills du type** — Ressources du type de ce projet.
- **Skills du projet** — Ressources de ce projet précis.

Une connexion de projet réunit le projet, son type et éventuellement les globaux. Une connexion de type voit ce type et éventuellement les globaux. Sans projet ni type, seuls les globaux peuvent être visibles si inclus. Les autres projets sont exclus.

```callout
{"type": "tip", "title": "À retenir", "body": "Chaque connexion a son propre contexte. Plusieurs clients peuvent travailler sur des projets différents. L’écriture couvre toutes les ressources accessibles, globales comprises si incluses."}
```

## Illustration {#illustration}

```image
{"id": "projects-illustration", "src": "assets/images/project-scopes.fr.jpg", "alt": "Exemple de projet rattaché à un type.", "title": "Exemple de projet rattaché à un type.", "controls": "minimal"}
```
