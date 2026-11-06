---
id: projects
title: Projets, types et visibilité
description: Définir la visibilité par portée globale, type de projet ou projet.
section: Bibliothèque
order: 5
revision: 2
sourceRevision: 2
parent: skills
---


## Choisir qui peut consulter chaque ressource {#content}


1. Dans Projets & types, créez un type comme Application web puis un projet rattaché.
2. Attribuez chaque Skill ou image à Globale, à ce type ou à ce projet précis.
3. Dans Connexions, choisissez le projet ou type de chaque IA et l’inclusion éventuelle des globaux.

## Une connexion de projet peut lire {#diagram-1}

```diagram
{"type": "flow", "title": "Une connexion projet peut lire", "nodes": [{"id": "context", "label": "Connexion projet", "x": 0, "y": 120, "width": 220}, {"id": "global", "label": "Globaux si activés", "x": 340, "y": 0, "width": 300}, {"id": "type", "label": "Skills du type de projet", "x": 340, "y": 120, "width": 300}, {"id": "project", "label": "Skills de ce projet", "x": 340, "y": 240, "width": 300}], "edges": [{"from": "context", "to": "global"}, {"from": "context", "to": "type"}, {"from": "context", "to": "project"}]}
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
