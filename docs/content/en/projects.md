---
id: projects
title: Projects, types and visibility
description: A project connection combines that project, its type and optionally globals. A type-only connection sees that type and optionally globals. Without project/type, only globals can be visible when included. Other projects stay outside scope.
section: User guide
order: 5
revision: 1
---

## Projects, types and visibility {#content}


1. In Projects & types, create a type such as Web application, then a project linked to it.
2. Assign each Skill/image to Global, that type or that specific project.
3. In Connections, choose each AI’s project or type context and whether global resources are included.

## A project connection can read {#diagram-1}

```diagram
{"type": "flow", "title": "A project connection can read", "nodes": [{"id": "n0", "label": "Global skills", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "Project-type skills", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "Project skills", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **Global skills** — Only when Include global is enabled.
- **Project-type skills** — Resources for this project’s type.
- **Project skills** — Resources for this specific project.

A project connection combines that project, its type and optionally globals. A type-only connection sees that type and optionally globals. Without project/type, only globals can be visible when included. Other projects stay outside scope.

```callout
{"type": "tip", "title": "Remember", "body": "Each connection has its own context. Multiple clients can work on different projects simultaneously. Write access covers every accessible resource, including globals when included."}
```

## Screenshot {#illustration}

```image
{"id": "projects-illustration", "src": "assets/images/project-scopes.jpg", "alt": "A sample project associated with a project type.", "title": "A sample project associated with a project type.", "controls": "minimal"}
```
